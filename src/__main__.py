from __init__ import write_chunks, get_scores
import fire


def index(max_chunk_size: int) -> None:
    write_chunks(max_chunk_size)


def search(prompt: str, k: int) -> None:
    scores = get_scores(prompt, k)


def search_dataset(dataset_path: str, k: int, save_directory: str):
    


if __name__ == "__main__":
    try:
        fire.Fire()
    except Exception as err:
        print(err)
