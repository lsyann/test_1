import json
import math
from tqdm import tqdm
from typing import Any
from .pydantic_classes import MinimalSource, MinimalSearchResults, StudentSearchResults


def clean(text: str) -> list[str]:
    cleaner = "".join(c if c.isalnum() or c == '_' else " " for c in text)
    return cleaner.lower().split()


def get_text(doc: dict[str, Any]) -> str:
    file = ""
    with open(doc.file_path, "r") as f:
        for line in f:
            file += line

    chunk = " ".join(doc.file_path.split("/")) + "\n"
    chunk += file[doc.first_character_index:doc.last_character_index + 1]
    return chunk


def _get_score(
        word: str, scores: list[int],
        data: list[dict[str, Any]],
        data_text: list[dict[str, Any]],
        avg_len: float) -> None:

    nb_docs = len(data)

    count = 0
    freq = []
    for i in range(nb_docs):
        freq.append(data_text[i]["text"].count(word))
        count += 1 if freq[-1] > 0 else 0

    IDF = math.log(1 + (nb_docs - count + 0.5) / (count + 0.5))
    for i in range(nb_docs):
        temp = freq[i] + 1.2 * (0.25 + 0.75 * (data_text[i]["len"] / avg_len))
        scores[i] += IDF * freq[i] / temp


def unique_prompt(
        prompt: str,
        data: list[dict[str, Any]],
        data_text: list[dict[str, Any]],
        avg_len: float, k: int) -> MinimalSource:

    score = [0] * len(data)
    for word in clean(prompt):
        _get_score(word, score, data, data_text, avg_len)
    if score == [0] * len(score):
        return [MinimalSource(
            file_path="",
            first_character_index=0,
            last_character_index=0)]
    index = []
    for i, _ in sorted(enumerate(score), key=lambda x: x[1], reverse=True)[:k]:
        index.append(i)
    return [MinimalSource.model_validate(data[elem]) for elem in index]


def multiple_prompts(
        prompts: list[str],
        data: list[dict[str, Any]],
        data_text: list[dict[str, Any]],
        avg_len: float,
        k: int) -> list[MinimalSource]:

    search_results = StudentSearchResults(search_results=[], k=k)
    for i in tqdm(range(len(prompts)), desc="searching dataset"):
        search_results.search_results.append(MinimalSearchResults(
            question_id=prompts[i].question_id,
            question=prompts[i].question,
            retrieved_sources=unique_prompt(
                prompts[i].question,
                data, data_text, avg_len, k)))
    return search_results


def get_sources(prompts: Any, k: int, multiple: bool) -> Any:
    with open("data/processed/processed", "r") as f:
        data = [MinimalSource.model_validate(elem) for elem in json.load(f)]

    data_text: list[dict[Any, Any]] = [
            {"text": clean(get_text(elem))} for elem in data]
    for i in range(len(data)):
        data_text[i]["len"] = len(data_text[i]["text"])
    avg_len = sum(d["len"] for d in data_text) / len(data)
    if multiple:
        return multiple_prompts(prompts, data, data_text, avg_len, k)
    return unique_prompt(prompts, data, data_text, avg_len, k)
