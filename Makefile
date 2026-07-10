all: run

run:
	python3 -m src [-functions_definition data/input/functions_definition.json] [-input data/input/function_calling_tests.json] [-output data/output/function_calling_results.json] 

clean:
	rm -rf src/__pycache__
