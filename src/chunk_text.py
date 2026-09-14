import os
from __init__ import Chunk


def _chunk_text(file: str, index: int, max_length: int) -> int:
    temp = index
    while file[temp] == "#":
        temp += 1
    while temp < len(file) and file[temp] != "#":
        temp += 1
    temp -= 1
    if temp - index < max_length:
        return temp
    divider = 2
    while round((temp - index) / divider) > max_length:
        divider += 1
    temp = index + round((temp - index) / divider)
    if temp - index + round((temp - index) / 10) < max_length:
        return temp + round((temp - index) / 10)
    return temp


def _chunk_code(file: str, index: int, max_length: int) -> int:
    temp = index
    if file.find("def", index) == index:
        temp += 3



def get_chunks(path: str, max_length: int, is_code: bool) -> list[Chunk]:
    file = ""
    file_len = 0
    with open(path, "r") as f:
        for line in f:
            file += line
            file_len += len(line)
    chunk_method = _chunk_code if is_code else _chunk_text
    index = 0
    chunk_list = []
    while index < file_len:
        chunk_end_index = chunk_method(file, index, max_length)
        chunk_list.append(Chunk(path, index, chunk_end_index))
        index = chunk_end_index + 1
    return chunk_list

test = get_chunks("/home/ylau-sim/rag/src/chunk_text.py", 20, True)
#test = get_chunks("/home/ylau-sim/rag/notes.txt", 20, False)
for elem in test:
    print(elem.start, elem.end)
