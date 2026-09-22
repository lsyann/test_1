import json
import math
from tqdm import tqdm
from .pydantic_classes import MinimalSource


def tokenize(text: str) -> list[str]:
    cleaned = "".join(c if c.isalnum() or c == '_' else " " for c in text)
    return cleaned.lower().split()

def get_text(doc: dict) -> str:
    file = ""
    with open(doc["file_path"], "r") as f:
        for line in f:
            file += line
    
    chunk = "".join(doc["file_path"].split("/")) + "\n"
    chunk += file[doc["first_character_index"]:doc["last_character_index"] + 1]
    return chunk
                

def _get_score(word: str, scores: list[int], data: list[dict], data_text: list[dict], avg_len: int) -> None:
    nb_docs = len(data)
    
    count = 0
    freq = []
    for i in range(nb_docs):
        freq.append(data_text[i]["text"].count(word))
        count += 1 if freq[-1] > 0 else 0

    IDF = math.log(1 + (nb_docs - count + 0.5) / (count + 0.5))
    for i in range(nb_docs):
        scores[i] += freq[i] / (freq[i] + 1.2 * (0.25 + 0.75 * (data_text[i]["len"] / avg_len))) * IDF


def unique_prompt(prompt, data, data_text, avg_len, k):
    scores = [0] * len(data)
    for word in tokenize(prompt):
        _get_score(word, scores, data, data_text, avg_len)
    if scores == [0] * len(scores):
        return [MinimalSource(file_path="", first_character_index=0, last_character_index=0)]
    index = [idx for idx, val in sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:k]]
    return [MinimalSource.model_validate(data[elem]) for elem in index]


def multiple_prompts(prompts, data, data_text, avg_len, k):
    lst = []
    for i in tqdm(range(len(prompts)), desc="searching dataset"):
        lst.append(unique_prompt(prompts[i]["question"], data, data_text, avg_len, k))
    return lst


def get_sources(prompts, k: int, multiple: bool) -> list[dict]:
    try:
        with open("data/processed", "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as err:
        print("Invalid JSON syntax: ", err)
        return 0
    except FileNotFoundError as err:
        print("Missing data file: ", err)
        return 0

    data_text = [{"text": tokenize(get_text(elem))} for elem in data]
    for i in range(len(data)):
        data_text[i]["len"] = len(data_text[i]["text"])
    avg_len = sum(d["len"] for d in data_text) / len(data)
    if multiple:
        return multiple_prompts(prompts, data, data_text, avg_len, k)
    return unique_prompt(prompts, data, data_text, avg_len, k)
