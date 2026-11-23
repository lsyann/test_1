import sys
import resource
import traceback
import contextlib
import io
import json


def block_mischief(event,arg):
    if event=='open' or event.split('.')[0] in ['subprocess', 'os', 'shutil', 'winreg']:
        raise IOError('file write forbidden')


def error(err, out, output, status):
    temp = traceback.format_exception(err)
    nb = [nb for nb, elem in enumerate(temp) if "<string>" in elem][0]
    output["error"] = "".join(temp[nb:])
    output["status"] = status
    output["error_type"] = type(err).__name__
    output["error_message"] = str(err)
    return output


class output_redirect:
    def __init__(self):
        self.text = ""
        self.limit = 5000
        self.len = 0
        self.truncated = False

    def write(self, text):
        self.len += len(text)
        if not self.truncated and self.len > self.limit:
            self.truncated = True
        i = 0
        while len(self.text) < self.limit and i < len(text):
            self.text += text[i]
            i += 1


def main():
    argv = [int(elem) for elem in sys.argv[1:]]
    env = {}
    try:
        sys.addaudithook(block_mischief)
        resource.setrlimit(resource.RLIMIT_CPU, (argv[0] * 4, argv[0] * 4 + 10))
        resource.setrlimit(resource.RLIMIT_AS, (argv[1] * 1024 * 1024, argv[1] * 1024 * 1024))
        while True:
            code = ""
            for line in sys.stdin:
                if line == "end of this chunkEOC\n":
                    break
                code += line
            if code == "":
                return
            output= {"status": "ok"}
            out = output_redirect()
            try:
                with contextlib.redirect_stdout(out):
                    exec(code, env)
            except Exception as err:
                output = error(err, out, output, "error")
            except BaseException as err:
                raise Exception("BaseException caught")
            output["output"] = out.text
            print(json.dumps(output), "\nend of this chunkEOC")
            sys.stdout.flush()
    except Exception as err:
        output = error(err, out, output, "dead")
        output["output"] = out.getvalue()
        print(json.dumps(output), "\nend of this chunkEOC")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
