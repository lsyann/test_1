chunk:
	python3 src/chunker.py

clean:
	rm -rf src/__pycache__

fclean: clean
	rm -rf data/processed
