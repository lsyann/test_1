import os
import json


class Chunk:
    def __init__(self, path: str, start: int, end: int):
        self.path = path
        self.start = start
        self.end = end


def _divider(temp: int, index: int, max_length: int) -> int:
    divider = 2
    while round((temp - index) / divider) > max_length:
        divider += 1
    temp = index + round((temp - index) / divider)
    if temp - index + round((temp - index) / 10) < max_length:
        return temp + round((temp - index) / 10)
    return temp


def _chunk_text(file: str, index: int, max_length: int) -> int:
    temp = index
    while temp < len(file) and file[temp] == "#":
        temp += 1
    while temp < len(file) and file[temp] != "#":
        temp += 1
    temp -= 1
    if temp - index < max_length:
        return temp
    return _divider(temp, index, max_length)


def _chunk_code(file: str, index: int, max_length: int) -> int:
    temp = index
    if file[temp] == "@":
        temp = file.find("def ", temp) if file.find("def ", temp) != -1 else temp + 1
    if file.find("def ", temp) == temp:
        temp += 3
    if file.find("class ", temp) == temp:
        temp += 4
    end = [file.find("def ", temp), file.find("class ", temp), file.find("@", temp)]
    end = [elem for elem in end if elem != -1]
    temp = len(file) - 1 if len(end) == 0 else min(end) - 1
    if temp - index < max_length:
        return temp
    return _divider(temp, index, max_length)


def _get_chunks(path: str, max_length: int, is_code: bool) -> list[Chunk]:
    file = ""
    with open(path, "r") as f:
        for line in f:
            file += line
    file_len = len(file)
    chunk_method = _chunk_code if is_code else _chunk_text
    index = 0
    chunk_list = []
    while index < file_len:
        chunk_end_index = chunk_method(file, index, max_length)
        chunk_list.append(Chunk(path, index, chunk_end_index))
        index = chunk_end_index + 1
    return chunk_list


def _chunk_files(path: str, max_length: int) -> list[list[Chunk]]:
    files = os.listdir(path)
    lst = []
    for file in files:
        if "." not in file:
            try:
                temp = _chunk_files(path + "/" + file, max_length)
            except Exception as err:
                ...
            if temp:
                for elem in temp:
                    lst.append(elem)
        elif file.endswith(".md"):
            lst.append(_get_chunks(path + "/" + file, max_length, False))
        elif file.endswith(".py"):
            lst.append(_get_chunks(path + "/" + file, max_length, True))
    return lst


def write_chunks():
    chunked_files = _chunk_files(os.getcwd() + "/vllm-0.10.1", 2000)
    lst = []
    for file in chunked_files:
        for chunk in file:
            lst.append({"path": chunk.path, "start": chunk.start, "end": chunk.end})
    
    os.makedirs(os.path.dirname("data/processed"), exist_ok=True)
    with open("data/processed", "w") as f:
        json.dump(lst, f)


if __name__ == "__main__":
    write_chunks()
