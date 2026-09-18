from .__init__ import write_chunks, get_sources, get_text, get_answer, MinimalSearchResults, MinimalSource, StudentSearchResultsAndAnswer, MinimalAnswer, Small_LLM_Model
from tqdm import tqdm
import fire
import json
import os


def index(max_chunk_size: int) -> None:
    write_chunks(max_chunk_size)


def search(query: str, k: int) -> None:
    results = get_sources(query, k, False)
    for elem in results:
        print(f"{elem.file_path} [{elem.first_character_index}:{elem.last_character_index}]")


def search_dataset(dataset_path: str, k: int, save_directory: str) -> None:
    with open(dataset_path, "r") as f:
        q = json.load(f)["rag_questions"]

    lst = []
    sources = get_sources(q, k, True)
    for i in range(len(q)):
        lst.append(MinimalSearchResults(
            question_id=q[i]["question_id"], 
            question=q[i]["question"],
            retrieved_sources=sources[i]))

    new = []
    for elem in lst:
        new.append(elem.model_dump())
    if not save_directory.endswith("/"):
        save_directory += "/"
    save_directory += "StudentSearchResults"
    os.makedirs(os.path.dirname(save_directory), exist_ok=True)
    with open(save_directory, "w", encoding="utf-8") as f:
        json.dump(new, f, indent=2, ensure_ascii=False)


def answer(prompt: str, k: int) -> None:
    llm = Small_LLM_Model()
    print(get_answer(llm, prompt, k))


def answer_dataset(student_search_results_path: str, save_directory: str) -> None:
    llm = Small_LLM_Model()
    with open(student_search_results_path, "r") as f:
        results = json.load(f)
    search_results = StudentSearchResultsAndAnswer(search_results=[], k=len(results))
    sources = ""
    for i in tqdm(range(len(results)), desc = "answering dataset"):
        for source in results[i]["retrieved_sources"]:
            sources += "\n" + get_text(source) + "\n"
        search_results.search_results.append(
                MinimalAnswer(
                    question_id=results[i]["question_id"],
                    question=results[i]["question"],
                    retrieved_sources=results[i]["retrieved_sources"],
                    answer=get_answer(llm, results[i]["question"], 0, sources)))
                
    new = search_results.model_dump()
    if not save_directory.endswith("/"):
        save_directory += "/"
    save_directory += "StudentSearchResultsAndAnswer"

    os.makedirs(os.path.dirname(save_directory), exist_ok=True)
    with open(save_directory, "w") as f:
        json.dump(new, f)


def evaluate(student_search_results_path, dataset_path) -> None:
    with open(dataset_path, "r") as f:
        dataset = json.load(f)["rag_questions"]
    with open(student_search_results_path, "r") as f:
        results = json.load(f)
    correct, incorrect = 0, 0

    for answer in results:
        for elem in dataset:
            if answer["question_id"] == elem["question_id"]:
                if elem["sources"][0]["file_path"] in [s["file_path"] for s in answer["retrieved_sources"]]:
                    correct += 1
                else:
                    incorrect += 1
    print(f"{round(100 * correct / (incorrect + correct), 2)}% of your sources contained the correct path")


if __name__ == "__main__":
    try:
        fire.Fire()
    except Exception as err:
        print(err)
