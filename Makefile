index:
	uv run python -m src index -max_chunk_size 2000

search-doc:
	uv run python -m src search_dataset -dataset_path data/datasets/UnansweredQuestions/dataset_docs_public.json -k 5 -save_directory data/output/search_results

evaluate-doc:
	uv run python -m src evaluate -student_search_results_path data/output/search_results/docs_search_results -dataset_path data/datasets/AnsweredQuestions/dataset_docs_public.json

search-code:
	uv run python -m src search_dataset -dataset_path data/datasets/UnansweredQuestions/dataset_code_public.json -k 5 -save_directory data/output/search_results

evaluate-code:
	uv run python -m src evaluate -student_search_results_path data/output/search_results/code_search_results -dataset_path data/datasets/AnsweredQuestions/dataset_code_public.json


clean:
	rm -rf data/output
	rm -rf data/processed
	rm -rf src/__pycache__

lint:
	flake8 src
	uv run mypy src

lint-strict:
	flake8 src
	uv run mypy --strict src

