from .retrieval import get_sources
from .chunker import write_chunks
from .llm_model import get_answer, Small_LLM_Model
from .pydantic_classes import (
        MinimalAnswer,
        RagDataset,
        StudentSearchResults,
        StudentSearchResultsAndAnswer,
        AnsweredQuestion)
from tqdm import tqdm
import fire
import json
import os
from typing import cast


def index(max_chunk_size: int) -> None:
    write_chunks(max_chunk_size)


def search(query: str, k: int) -> None:
    results = get_sources(query, k if k > 0 else 0, False)
    for elem in results:
        print(f"{elem.file_path} ", end="")
        print(f"[{elem.first_character_index}:{elem.last_character_index}]")


def search_dataset(dataset_path: str, k: int, save_directory: str) -> None:
    with open(dataset_path, "r") as f:
        q = RagDataset.model_validate(json.load(f)).rag_questions

    retrieved_sources = get_sources(q, k, True)

    if not save_directory.endswith("/"):
        save_directory += "/"
    save_directory += "StudentSearchResults"
    os.makedirs(os.path.dirname(save_directory), exist_ok=True)
    with open(save_directory, "w") as f:
        json.dump(retrieved_sources.model_dump(), f)


def answer(prompt: str, k: int) -> None:
    llm = Small_LLM_Model()
    print(get_answer(llm, prompt, k))


def answer_dataset(
        student_search_results_path: str,
        save_directory: str) -> None:

    llm = Small_LLM_Model()
    with open(student_search_results_path, "r") as f:
        search_results = StudentSearchResults.model_validate(
                json.load(f)).search_results

    answer_results = StudentSearchResultsAndAnswer(
            search_results=[], k=5)

    for i in tqdm(range(len(search_results)), desc="answering dataset"):
        answer_results.search_results.append(
                MinimalAnswer(
                    question_id=search_results[i].question_id,
                    question=search_results[i].question,
                    retrieved_sources=search_results[i].retrieved_sources,
                    answer=get_answer(
                        llm, search_results[i].question, 0,
                        search_results[i].retrieved_sources)))
        print(answer_results.search_results[-1].question)
        print(answer_results.search_results[-1].answer)

    if not save_directory.endswith("/"):
        save_directory += "/"
    save_directory += "StudentSearchResultsAndAnswer"

    os.makedirs(os.path.dirname(save_directory), exist_ok=True)
    with open(save_directory, "w") as f:
        json.dump(answer_results.model_dump(), f)


def evaluate(student_search_results_path: str, dataset_path: str) -> None:
    with open(dataset_path, "r") as f:
        temp = RagDataset.model_validate(json.load(f)).rag_questions
    dataset = [cast(AnsweredQuestion, elem) for elem in temp]
    with open(student_search_results_path, "r") as f:
        student_results = StudentSearchResults.model_validate(
                json.load(f)).search_results

    correct, incorrect = 0, 0

    for answer in dataset:
        correct_source = answer.sources[0]
        found = 0
        for student_answer in student_results:
            if answer.question_id == student_answer.question_id:
                for student_source in student_answer.retrieved_sources:
                    if student_source.file_path == correct_source.file_path:
                        intersection = min(
                                student_source.last_character_index,
                                correct_source.last_character_index)
                        intersection -= max(
                            student_source.first_character_index,
                            correct_source.first_character_index)
                        if intersection > 0.05 * (
                                correct_source.last_character_index - (
                                    correct_source.first_character_index)):
                            correct += 1
                            found += 1
                            break
        if not found:
            incorrect += 1
    print(
            f"{round(100 * (correct / (correct + incorrect)), 2)}"
            "% of your sources contained the correct "
            "path with at least 5% of the correct chunk")


if __name__ == "__main__":
    try:
        fire.Fire()
    except Exception as err:
        print(err)
