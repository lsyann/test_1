from .llm_sdk import Small_LLM_Model
import json
import os
from .config import config, Answer, Functions


def get_str(llm: Small_LLM_Model, tokens: list[int], lst: list[int]) -> None:
    idk = llm.encode('"')[0]
    lst.append(idk)
    tokens.append(idk)

    while True:
        logits = llm.get_logits_from_input_ids(tokens)

        for token_id in range(len(logits)):
            token_str = llm.decode([token_id])

            if "(" in token_str:
                logits[token_id] = float('-inf')

        next_id = logits.index(max(logits))

        if '"' in llm.decode([next_id]):
            lst.append(idk)
            tokens.append(idk)
            return None

        lst.append(next_id)
        tokens.append(next_id)


def get_int(llm: Small_LLM_Model, tokens: list[int], lst: list[int]) -> None:
    first = True

    while True:
        logits = llm.get_logits_from_input_ids(tokens)

        for token_id, score in enumerate(logits):
            token_str = llm.decode([token_id])

            if first:
                if token_str.isnumeric() is False and token_str not in ("-"):
                    logits[token_id] = float('-inf')
            else:
                if token_str.isnumeric() is False and token_str not in (
                        "-", ","):
                    logits[token_id] = float('-inf')

        next_id = logits.index(max(logits))

        if "," in llm.decode([next_id]):
            temp = llm.encode(".0")
            for elem in temp:
                lst.append(elem)
            return None

        if first:
            first = False

        lst.append(next_id)
        tokens.append(next_id)


def main(text: str) -> str:
    with open(definition_file, "r") as f:
        definitions = json.load(f)

    functions = [llm.encode(elem["name"]) for elem in definitions]

    text = text.replace('"', "'")

    lst = llm.encode("{" + f'"prompt": "{text}", "name": "')

    tokens = llm.encode(f"user request: {
                       text}, available functions: {
                       llm.decode(functions)}, function choice: ")

    temp = llm.encode("think about which function fits the user's request:")
    for elem in temp:
        tokens.append(elem)

    index = 0
    while True:
        logits = llm.get_logits_from_input_ids(tokens)

        next_id = logits.index(max(logits))

        if llm.decode([next_id]) == "\n" or index > 40:
            break
        tokens.append(next_id)
        index += 1

    index = 0

    while True:
        logits = llm.get_logits_from_input_ids(tokens)

        allowed = [elem[index] for elem in functions if index < len(elem)]

        for token_id, score in enumerate(logits):
            if token_id not in allowed:
                logits[token_id] = float('-inf')

        next_id = logits.index(max(logits))
        functions = [elem for elem in functions if elem[index] == next_id]

        tokens.append(next_id)
        lst.append(next_id)

        index += 1
        if len(functions) == 1 and len(functions[0]) == index:
            break

    temp = llm.encode('", "parameters": {')
    for elem in temp:
        lst.append(elem)

    params = [elem for elem in definitions if elem[
        "name"] == llm.decode(functions[0])][0]

    temp = llm.encode(f"\n[System: Extract parameters for {params['name']}]\n")
    for elem in temp:
        tokens.append(elem)

    for key in params["parameters"].keys():
        temp = llm.encode(f"{key} ({params["parameters"][key]["type"]}), ")
        for nb in temp:
            tokens.append(nb)

    temp = llm.encode("Let's extract the exact parameter"
                      "values from the prompt safely.\n"
                      f"Target function: {params['name']}\n"
                      "Extracted Values:\n")
    for elem in temp:
        tokens.append(elem)

    index = 0
    while True:
        logits = llm.get_logits_from_input_ids(tokens)

        next_id = logits.index(max(logits))

        if index > 30:
            break
        tokens.append(next_id)
        index += 1

    key = list(params["parameters"].keys())
    for i in range(len(key)):
        arg_type = params["parameters"][key[i]]["type"]

        temp = llm.encode(f'value of param "{key[i]}" ({arg_type}): ')
        for elem in temp:
            tokens.append(elem)

        temp = llm.encode(f'"{key[i]}": ')
        for elem in temp:
            lst.append(elem)

        if arg_type == "number":
            get_int(llm, tokens, lst)
        elif arg_type == "string":
            get_str(llm, tokens, lst)
        else:
            return f"unknown data type: {arg_type}"

        if i < len(key) - 1:
            temp = llm.encode(", ")
            for elem in temp:
                lst.append(elem)
                tokens.append(elem)
        else:
            temp = llm.decode(lst)
            if temp[-1] == ",":
                temp = temp[:-1]
            lst = llm.encode(temp)

    output: str = llm.decode(lst)
    output += "}}"

    return output


try:
    dic = config()

    definition_file = dic["-functions_definition"]
    input_file = dic["-input"]
    output_file = dic["-output"]

    llm = Small_LLM_Model()

    with open(input_file, "r") as f:
        prompts = json.load(f)

    with open(definition_file, "r") as f:
        definitions = json.load(f)

    for elem in definitions:
        Functions(name=elem["name"], description=elem["description"], parameters=elem["parameters"], returns=elem["returns"])
    
    answer = []

    for elem in prompts:
        answer.append(main(elem["prompt"]))
        print(answer[-1])
    
    final = "["
    for i in range(len(answer)):
        final += answer[i]
        if i < len(answer) - 1:
            final += ","
    final += "]"

    ls = json.loads(final)
    for elem in ls:
        Answer(prompt=elem["prompt"], name=elem["name"], params=elem["parameters"])
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(ls, f)

except Exception as err:
    print("error message: ", err)
