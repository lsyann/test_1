all: run

run:
	uv run -m src [-functions_definition data/input/functions_definition.json] [-input data/input/function_calling_tests.json] [-output data/output/function_calling_results.json]

install:
	uv sync

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

clean:
	rm -rf src/__pycache*
	rm -rf src/llm*/__pyca*
