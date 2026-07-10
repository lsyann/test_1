import sys


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
