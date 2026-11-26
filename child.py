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
    env = {}
    try:
        sys.addaudithook(block_mischief)
        resource.setrlimit(resource.RLIMIT_CPU, (argv[0] * 4, argv[0] * 4 + 10))
        resource.setrlimit(resource.RLIMIT_AS, (argv[1] * 1024 * 1024, argv[1] * 1024 * 1024))
        while True:
            line = sys.stdin.readline()
            if not line:
                exit()
            code = json.loads(line)["code"]
            output= {"status": "ok"}
            out = output_redirect()
            try:
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
