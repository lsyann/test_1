*This activity has been created as part of the 42 curriculum by ylau-sim*

Description:
    The goal of this activity was to implement retrieval-augmented generation in order to help an llm answer questions about a codebase.
    We first had to divide the files into chunks of 2000 characters or less, then I used the bm25 algorithm to identify the most important sources for a given prompt and these sources were then given as context to an llm who gave an answer.

Instruction:
    all commands use fire, they should start as:
        uv run python -m src <command>
    commands:
        index -max_chunk_size <int>
        search -query <str> -k <int>
        search_dataset -dataset_path <str> -k <int> -save_directory <str>
        answer -prompt <str> -k <int>
        answer_dataset -student_search_results_path <str> -save_directory <str>
        evaluate -student_search_results_path <str> -dataset_path <str>

Resources:
    https://www.geeksforgeeks.org/nlp/what-is-bm25-best-matching-25-algorithm/
    https://blog.stephane-robert.info/docs/developper/programmation/python/rag-chunking/
    I tried using AI to help me with bm25 but it was useless.

System architecture:
    chunker.py chunks the documents and writes the chunks to a file
    retrieval.py use bm25 to give a score to each of these chunks for a given prompt and returns a list of the top k sources
    llm_model.py uses these sources and gives them as context with the prompt to generate an answer

Chunking strategy:
    For .md files I chunked using '#' which are used to signal titles and parts, each new '#' starting a new chunk
    For .py files I started a new chunk when there was a new 'def', 'class' or '@'
    
    For both methods if the created chunk was to big i would divide it into equal parts that would fit in the max-chunk-size   

Retrieval method:
    For each chunk I had a score that had the sum of the scores of the query words and I returned the top k chunks

Performance analysis:
    The score increases up to recall@5 then it stagnates showing little difference between @5 and @10

Design decisions:
    The bm25 wasn't returning the correct chunks and I realised that adding the of the chunk before the text was making it more precise but i wasn't enough so I added it a second then a third time and it performed better every time so I left it that way.

Challenges faced:
    As mentioned in the design decisions the bm25 wasn't returning the right chunks so I added the path 3 times at the start

Example usage:
    make run
    make search-doc
    make evaluate-doc
