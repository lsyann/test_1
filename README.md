*This activity has been created as part of the 42 curriculum by ylau-sim*

Description:
    The goal of this activity was to use a llm to answer a prompt with a json-format answer.
    The answer has 3 categories:
        -prompt (the user prompt)
        -name (the name of the function used to answer the prompt)
        -parameters (the parameters of the function)
    This was done through constrained decoding, meaning i restricted the allowed tokens to
    guide the llm to the answer.

Instructions:
    do:
        uv run -m src [-functions_definition data/input/functions_definition.json] [-input data/input/function_calling_tests.json] [-output data/output/function_calling_results.json]

Ressources:
    ai was used to make the prompts to the llm.
    stackoverflow threads

Algorithm explanation:
    for all llm prompting i used greedy decoding, meaning i add everything it answers to the prompt    

    i add the information i already know to my ouput (prompt, dict keys, json formatting)
    and i prompt the llm for what i don't know (function names, parameters)
    
    To get the correct function I give the llm all function names then give it 40 tokens to
    think about the right one before asking it to answer. I limit it's answers to the function names.

    To get the parameters I give it 30 tokens to think about what they are going to be before
    prompting it either for an int or a string depending on the param type.

Design decisions:
    I chose not to have the llm write everything because it would be useless to prompt it before
    limiting it to a single choice.

Performance analysis:
    For the test prompts it's right 10/11 times. it takes around 10-20 seconds to answer a prompt.

Challenges faced:
    The llm is very small so I had to explain exactly what it needed to do at every step
    or it would output nonsense

Testing strategy:
    I first prompted it with my own prompts then when i had it working often enough i made a parser
    for the school prompts and used them instead

Example usage:
    "what is 10 + 32"
    "reverse the word 'hello'"
    "what is the square root of 121"
