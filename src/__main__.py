from .__init__ import write_chunks, get_scores, MinimalSearchResults, MinimalSource
import fire
import json


def index(max_chunk_size: int) -> None:
    write_chunks(max_chunk_size)


def search(prompt: str, k: int) -> None:
    results = get_scores(prompt, k)
    for elem in results:
        print(f"{elem["path"]} [{elem["start"]}:{elem["end"]}]")


def search_dataset(dataset_path: str, k: int, save_directory: str):
    with open(dataset_path, "r") as f:
        questions = json.load(f)["rag_questions"]
    lst = []
    #for q in questions:
    for i in range(1):
        q = questions[i]
        q["question"] == "llm"
        temp = [MinimalSource(file_path=elem["path"], first_character_index=elem["start"], last_character_index=elem["end"]) for elem in get_scores(q["question"], k)]
        lst.append(MinimalSearchResults(question_id=q["question_id"], question=q["question"], retrieved_sources=temp))
    with open(save_directory, "w") as f:
        json.dump(new, f)


if __name__ == "__main__":
    try:
        fire.Fire()
    except Exception as err:
        print(err)
