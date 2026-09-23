import os
import json
from .pydantic_classes import MinimalSource


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
    if file[temp] == "@" and file.find("def ", temp) != -1:
        temp = file.find("def ", temp)
    else:
        temp += 1
    if file.find("def ", temp) == temp:
        temp += 3
    if file.find("class ", temp) == temp:
        temp += 4
    end = [file.find("def ", temp), file.find("class ", temp)]
    end.append(file.find("@", temp))
    end = [elem for elem in end if elem != -1]
    temp = len(file) - 1 if len(end) == 0 else min(end) - 1
    if temp - index < max_length:
        return temp
    return _divider(temp, index, max_length)


def _get_chunks(
        path: str,
        max_length: int,
        is_code: bool) -> list[MinimalSource]:
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
        chunk_list.append(
                MinimalSource(
                    file_path=path,
                    first_character_index=index,
                    last_character_index=chunk_end_index))
        index = chunk_end_index + 1
    return chunk_list


def _chunk_files(path: str, max_length: int) -> list[list[MinimalSource]]:
    files = os.listdir(path)
    lst = []
    for file in files:
        try:
            temp = _chunk_files(path + "/" + file, max_length)
            if temp:
                for elem in temp:
                    lst.append(elem)
        except Exception as err:
            err = err
        if file.endswith(".md") or file.endswith(".txt"):
            lst.append(_get_chunks(path + "/" + file, max_length, False))
        elif file.endswith(".py"):
            lst.append(_get_chunks(path + "/" + file, max_length, True))
    return lst


def write_chunks(max_chunk_size: int) -> None:
    chunked_files = _chunk_files("data/raw", max_chunk_size)
    lst = []
    for file in chunked_files:
        for chunk in file:
            lst.append(chunk.model_dump())

    os.makedirs(os.path.dirname("data/processed/"), exist_ok=True)
    with open("data/processed/processed", "w") as f:
        json.dump(lst, f)
    print("Successfully chunked the corpus under data/processed/processed")


if __name__ == "__main__":
    write_chunks(2000)
