from .llm import Small_LLM_Model
import json
from .config import config


def get_str(llm: Small_LLM_Model, tokens: list[int], lst: list[int]) -> None:
    idk = llm._encode('"')[0]
    lst.append(idk)
    tokens.append(idk)

    while True:
        # print(llm._decode(tokens))
        logits = llm.get_logits_from_input_ids(tokens)

        next_id = logits.index(max(logits))

        if '"' in llm._decode([next_id]):
            lst.append(idk)
            tokens.append(idk)
            return None

        lst.append(next_id)
        tokens.append(next_id)


def get_int(llm: Small_LLM_Model, tokens: list[int], lst: list[int]) -> None:
    first = True

    while True:
        # print(llm._decode(tokens))
        logits = llm.get_logits_from_input_ids(tokens)

        for token_id, score in enumerate(logits):
            token_str = llm._decode([token_id])

            if first:
                if token_str.isnumeric() is False and token_str not in ("-"):
                    logits[token_id] = float('-inf')
            else:
                if token_str.isnumeric() is False and token_str not in (
                        "-", ",", "."):
                    logits[token_id] = float('-inf')

        next_id = logits.index(max(logits))

        if "," in llm._decode([next_id]):
            return None

        if first:
            first = False

        lst.append(next_id)
        tokens.append(next_id)


def main(text: str) -> str:
    with open(definition_file, "r") as f:
        definitions = json.load(f)

    functions = [llm._encode(elem["name"]) for elem in definitions]

    text = text.replace('"', "'")

    lst = llm._encode("{" + f'"prompt": "{text}", "name": "')

    tokens = llm._encode(f"user request: {
                       text}, available functions: {
                       llm._decode(functions)}, function choice: ")

    temp = llm._encode("think about which function fits the user's request:")
    for elem in temp:
        tokens.append(elem)

    index = 0
    while True:
        logits = llm.get_logits_from_input_ids(tokens)

        next_id = logits.index(max(logits))

        if llm._decode([next_id]) == "\n" or index > 40:
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

    temp = llm._encode('", "parameters": {')
    for elem in temp:
        lst.append(elem)

    params = [elem for elem in definitions if elem[
        "name"] == llm._decode(functions[0])][0]

    temp = llm._encode(f"prompt: {
                       text}, use function {
                       params["name"]}, function description: {
                       params["description"]}, function parameters: ")
    tokens = []
    for elem in temp:
        tokens.append(elem)

    for key in params["parameters"].keys():
        temp = llm._encode(f"{key} ({params["parameters"][key]["type"]}), ")
        for nb in temp:
            tokens.append(nb)

    temp = llm._encode("think scratchpad:")
    for elem in temp:
        tokens.append(elem)

    index = 0
    while True:
        logits = llm.get_logits_from_input_ids(tokens)

        next_id = logits.index(max(logits))

        if llm._decode([next_id]) == "\n" or index > 30:
            break
        tokens.append(next_id)
        index += 1
    # print(llm._decode(tokens))

    key = list(params["parameters"].keys())
    for i in range(len(key)):
        arg_type = params["parameters"][key[i]]["type"]

        temp = llm._encode(f'value of param "{key[i]}" ({arg_type}): ')
        for elem in temp:
            tokens.append(elem)

        temp = llm._encode(f'"{key[i]}": ')
        for elem in temp:
            lst.append(elem)

        if arg_type == "number":
            get_int(llm, tokens, lst)
        elif arg_type == "string":
            get_str(llm, tokens, lst)
        else:
            return f"unknown data type: {arg_type}"

        if i < len(key) - 1:
            temp = llm._encode(", ")
            for elem in temp:
                lst.append(elem)
                tokens.append(elem)
        else:
            temp = llm._decode(lst)
            if temp[-1] == ",":
                temp = temp[:-1]
            lst = llm._encode(temp)

    output: str = llm._decode(lst)
    output += "}}"

    with open(output_file, "r") as f:
        file = ""
        for line in f:
            file += line

    if file == "":
        output = f"[{output}]"
        ls = json.loads(output)
    else:
        ls = json.loads(file)
        ls.append(json.loads(output))
    with open(output_file, "w") as f:
        json.dump(ls, f)

    return output


try:
    dic = config()

    definition_file = dic["-functions_definition"]
    input_file = dic["-input"]
    output_file = dic["-output"]

    llm = Small_LLM_Model()

    with open(input_file, "r") as f:
        prompts = json.load(f)

    for elem in prompts:
        print(main(elem["prompt"]), "\n")

except Exception as err:
    print("error message: ", err)
