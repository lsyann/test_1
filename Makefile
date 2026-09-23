index:
	uv run python -m src index -max_chunk_size 2000

search-doc:
	uv run python -m src search_dataset -dataset_path data/dataset/UnansweredQuestions/dataset_docs_public.json -k 5 -save_directory data/output/search_results_and_answer

evaluate-doc:
	uv run python -m src evaluate -student_search_results_path data/output/search_results_and_answer/StudentSearchResults -dataset_path data/dataset/AnsweredQuestions/dataset_docs_public.json

search-code:
	uv run python -m src search_dataset -dataset_path data/dataset/UnansweredQuestions/dataset_code_public.json -k 5 -save_directory data/output/search_results_and_answer

evaluate-code:
	uv run python -m src evaluate -student_search_results_path data/output/search_results_and_answer/StudentSearchResults -dataset_path data/dataset/AnsweredQuestions/dataset_code_public.json


clean:
	rm -rf data/output
	rm -rf data/processed

lint:
	flake8 src
	mypy src

lint-strict:
	flake8 src
	mypy --strict src

