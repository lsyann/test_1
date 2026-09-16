import json
import math
from __init__ import Chunk


def get_text(doc: Chunk) -> str:
    file = ""
    with open(doc["path"], "r") as f:
        for line in f:
            file += line

    chunk = ""
    index = doc["start"]
    while index < doc["end"]:
        chunk += file[index]
        index += 1
    return chunk
                

def _TF(word: str, file: str, avg_len: int) -> int:
    freq = file.count(word)
    nb_word = len(file.split())

    return freq / (freq + 1.2 * (1 - 0.75 + 0.75 * (nb_word / avg_len)))


def _get_score(word: str, scores: list[int], data: list[Chunk]) -> int:
    avg_len = 0
    nb_docs = len(data)
    for doc in data:
        avg_len += doc["end"] - doc["start"]
    avg_len = round(avg_len / nb_docs)
    
    data_text = []
    count = 0
    for doc in data:
        data_text.append(get_text(doc))
        if data_text[-1].count(word) != 0:
            count += 1

    IDF = math.log((nb_docs - count + 0.5) / (count + 0.5))
    for i in range(nb_docs):
        scores[i] += _TF(word, data_text[i], avg_len) * IDF


def placeholder(prompt: str) -> list[int]:
    try:
        with open("data/processed", "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as err:
        print("Invalid JSON syntax: ", err)
        return 0
    except FileNotFoundError as err:
        print("Missing data file: ", err)
        return 0

    scores = []
    for elem in data:
        scores.append(0)
    for word in prompt.split():
        _get_score(word, scores, data)
    #return scores
    print(data[scores.index(max(scores))]["path"])
    print(data[scores.index(max(scores))]["start"])
    print(data[scores.index(max(scores))]["end"])


if __name__ == "__main__":
    placeholder("What determines whether custom allreduce is enabled in vLLM's CudaCommunicator?")
