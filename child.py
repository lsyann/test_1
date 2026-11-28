import sys
import resource
import traceback
import contextlib
import io
import json
import builtins
import ast
import os



ALLOWED_IMPORTS = ["math", "cmath", "decimal", "itertools", "operator", "bisect",
                   "heapq", "string", "textwrap", "re", "functools", "datetime",
                   "copy", "array", "collections.*"]

SAFE_NAMES = ["abs", "all", "any", "ascii", "bin", "bool", "bytearray", "bytes",
              "callable", "chr", "classmethod", "complex", "dict", "divmod",
              "enumerate", "filter", "float", "format", "frozenset", "hasattr",
              "hash", "hex", "int", "isinstance", "issubclass", "iter", "len",
              "list", "map", "max", "min", "next", "object", "oct", "ord", "pow",
              "print", "property", "range", "repr", "reversed", "round", "set",
              "slice", "sorted", "staticmethod", "str", "sum", "super", "tuple",
              "type", "zip", "NotImplemented", "Ellipsis", "__build_class__"]

allowed_directories = ["/etc"]
def safe_open(file, mode):
    path = os.path.realpath(file)
    for elem in allowed_directories:
        if path.startswith(elem):
            return open(file, mode)
    raise PermissionError(f"{file} is in a forbidden directory. Allowed dictories: {allowed_directories}")

def is_allowed(name, allowed):
    if name in allowed:
        return True
    for elem in allowed:
        if elem.endswith(".*"):
            base = elem[:-2]
            if name == base or name.startswith(base + "."):
                return True
    return False


def allowlist(allowed_imports):
    real_import = builtins.__import__

    def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
        if level != 0 or not is_allowed(name, allowed_imports):
            raise ImportError(f"import of '{name}' is not allowed: {allowed_imports}")
        return real_import(name, globals, locals, fromlist, level)

    allowed = {elem: getattr(builtins, elem) for elem in SAFE_NAMES}
    for elem in builtins.__dict__:
        obj = getattr(builtins, elem)
        if isinstance(obj, type) and issubclass(obj, BaseException):
            allowed[elem] = obj
    allowed["__import__"] = safe_import
    allowed["open"] = safe_open
    return allowed


class ForbiddenCode(Exception):
    pass


def check_code(code):
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            name = node.attr
        elif isinstance(node, ast.Name):
            name = node.id
        else:
            continue
        if name.startswith("_"):
            raise ForbiddenCode(f"line {node.lineno}: access to '{name}' is not allowed")

def block_mischief(event, arg):
    if event=='open':
        print(arg)


def error(err, out, output, status):
    frames = traceback.format_exception(err)
    nb = [nb for nb, elem in enumerate(frames) if "<string>" in elem]
    temp1 = frames[-1]
    if len(temp1) > 1000:
        temp1 = temp1[:1000] + "[following output omitted]"
    if len(nb) != 0:
        temp = "".join(frames[nb[0]:-1])
        if len(temp) > 2000:
            temp = "[earlier output omitted]" + temp[-2000:]
        output["error"] = temp + temp1
    else:
        output["error"] = temp1
    output["status"] = status
    output["error_type"] = type(err).__name__
    error_message = str(err)
    if len(error_message) > 2000:
        error_message = error_message[:2000]
    output["error_message"] = error_message
    return output


class output_redirect(io.TextIOBase):
    def __init__(self):
        self.text = ""
        self.limit = 5000
        self.len = 0
        self.truncated = False
        self.save = ""

    def write(self, text):
        self.len += len(text)
        if not self.truncated and self.len > self.limit:
            self.truncated = True
        i = 0
        while len(self.text) < self.limit and i < len(text):
            self.text += text[i]
            i += 1
        if self.len >= self.limit and len(text.strip()) > 0:
            self.save = ""
            if len(text) > self.limit / 2:
                self.save = text[len(text) - round(self.limit / 2):]
            else:
                self.save = text
        return len(text)

    def get_text(self):
        if len(self.save.strip()) == 0:
            return self.text
        self.text = self.text[:len(self.text) - len(self.save) - 25]
        self.text += "... string was truncated\n"
        self.text += self.save
        return self.text


def child():
    argv = [int(elem) for elem in sys.argv[1:]]
    env = {"__name__": "sandbox"}
    try:
        #sys.addaudithook(block_mischief)
        resource.setrlimit(resource.RLIMIT_CPU, (argv[0] * 4, argv[0] * 4 + 10))
        resource.setrlimit(resource.RLIMIT_AS, (argv[1] * 1024 * 1024, argv[1] * 1024 * 1024))
        while True:
            env["__builtins__"] = allowlist(ALLOWED_IMPORTS)
            line = sys.stdin.readline()
            if not line:
                exit()
            code = json.loads(line)["code"]
            output= {"status": "ok"}
            out = output_redirect()
            try:
                check_code(code)
                with contextlib.redirect_stdout(out):
                    exec(code, env)
            except Exception as err:
                output = error(err, out, output, "error")
            except BaseException as err:
                output = error(err, out, output, "dead")
                output["output"] = out.get_text()
                print(json.dumps(output), flush=True)
                return
            output["output"] = out.get_text()
            if out.truncated:
                output["additional info"] = f"the output was truncated, original length was {out.len}"
            print(json.dumps(output), flush=True)
    except Exception as err:
        output = error(err, out, output, "dead")
        output["output"] = out.get_text()
        print(json.dumps(output), flush=True)


if __name__ == "__main__":
    child()
