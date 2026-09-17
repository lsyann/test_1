from .__init__ import write_chunks, get_scores, get_text, get_answer, MinimalSearchResults, MinimalSource, StudentSearchResultsAndAnswer, MinimalAnswer, Small_LLM_Model
import fire
import json
import os


def index(max_chunk_size: int) -> None:
    write_chunks(max_chunk_size)


def search(prompt: str, k: int) -> None:
    results = get_scores(prompt, k)
    for elem in results:
        print(f"{elem["file_path"]} [{elem["first_character_index"]}:{elem["last_character_index"]}]")


def search_dataset(dataset_path: str, k: int, save_directory: str) -> None:
    with open(dataset_path, "r") as f:
        questions = json.load(f)["rag_questions"]
    lst = []
    #for q in questions:
    for i in range(1):
        q = questions[i]
        q["question"] == "llm"

        sources = []
        for elem in get_scores(q["question"], k):
            sources.append(MinimalSource.model_validate(elem))

        lst.append(MinimalSearchResults(
            question_id=q["question_id"], 
            question=q["question"],
            retrieved_sources=sources))

    new = []
    for elem in lst:
        new.append(elem.model_dump())
    if not save_directory.endswith("/"):
        save_directory += "/"
    save_directory += "StudentSearchResults"
    os.makedirs(os.path.dirname(save_directory), exist_ok=True)
    with open(save_directory, "w") as f:
        json.dump(new, f)


def answer(prompt: str, k: int) -> None:
    llm = Small_LLM_Model()
    print(get_answer(llm, prompt, k))


def answer_dataset(student_search_results_path: str, save_directory: str) -> None:
    llm = Small_LLM_Model()
    with open(student_search_results_path, "r") as f:
        results = json.load(f)
    search_results = StudentSearchResultsAndAnswer(search_results=[], k=len(results))
    sources = ""
    for result in results:
        for source in result["retrieved_sources"]:
            sources += "\n" + get_text({"path": source["file_path"], "start": source["first_character_index"], "end": source["last_character_index"]}) + "\n"
        search_results.search_results.append(MinimalAnswer(question_id=result["question_id"], question=result["question"], retrieved_sources=result["retrieved_sources"], answer=get_answer(llm, result["question"], 0, sources)))
    new = search_results.model_dump()
    if not save_directory.endswith("/"):
        save_directory += "/"
    save_directory += "StudentSearchResultsAndAnswer"

    os.makedirs(os.path.dirname(save_directory), exist_ok=True)
    with open(save_directory, "w") as f:
        json.dump(new, f)


if __name__ == "__main__":
    try:
        fire.Fire()
    except Exception as err:
        print(err)
