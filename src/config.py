import sys
from pydantic import BaseModel, model_validator
from typing import Any


class Functions(BaseModel):
    name: str
    description: str
    parameters: dict[Any, Any]
    returns: dict[Any, Any]

    @model_validator(mode='after')
    def validate_functions(self):
        if self.returns["type"] not in ("string", "number"):
            raise Exception(f"Invalid return type: {self.returns["type"]}")
        for key in self.parameters.keys():
            if self.parameters[key]["type"] not in ("string", "number"):
                raise Exception(f"Invalid parameter type: {self.parameters[key]["type"]}")
        return self


class Answer(BaseModel):
    prompt: str
    name: str
    params: dict[Any, Any]


def config() -> dict[str, str]:
    if len(sys.argv) != 7:
        raise Exception("Invalid number of argument")

    args = sys.argv
    lst = ["-functions_definition", "-input", "-output"]
    dic = {}
    i = 1
    while i < 7:
        if args[i][1:] in lst:
            lst.pop(lst.index(args[i][1:]))
        else:
            raise Exception(f"unknown param: {args[i][1:]}")
        dic[args[i][1:]] = args[i + 1][:-1]

        i += 2

    return dic
