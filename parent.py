import subprocess
import select
import signal
import json

class Sandbox:
    def __init__(self):
        self.child: subprocess.Popen = None
        self.timeout = "20"
        self.max_memory = "512"

    def raise_child(self):
        print("new child")
        self.child = subprocess.Popen(["python3", "child.py",
                                       self.timeout,
                                       self.max_memory],
                                      stdout=subprocess.PIPE,
                                      stdin=subprocess.PIPE,
                                      text=True)
    
    def reset_child(self):
        try:
            self.child.kill()
            self.child.wait()
            self.raise_child()
        except Exception as err:
            print(err)


    def run(self, code: str) -> str:
        if self.child is None or self.child.poll() is not None:
            self.raise_child()
        try:
            self.child.stdin.write(json.dumps({"code":code}) + "\n")
            self.child.stdin.flush()
            timeout = select.poll()
            timeout.register(self.child.stdout)
            if len(timeout.poll(1000 * int(self.timeout))) == 0:
                self.reset_child()
                return "process timeout"
            line = self.child.stdout.readline()
            if line == "" or self.child.poll() is not None:
                sig = self.child.returncode
                self.reset_child()
                try:
                    return signal.Signals(-sig)
                except Exception as err:
                    return f"exit code: {sig}, the child was reset"
            try:
                output = json.loads(line)
            except Exception as err:
                self.reset_child()
                return "problem with child"
            if output["status"] == "dead":
                self.reset_child()
            return line
        except Exception as err:
            return f"problem with sandbox: {err}"

RESET = "problem with child, the child was reset"
TIMEOUT = "process timeout"


def check(sd, test):
    def norm(s):
        # ignore excessive newlines: collapse runs of \n, strip leading/trailing ones
        if not isinstance(s, str):
            return s
        return "\n".join(line for line in s.split("\n") if line != "")

    passed = 0
    for name, code, expected in test:
        got = sd.run(code)                 # run() must return a list of strings
        ok = expected(got) if callable(expected) else norm(got) == norm(expected)
        if ok:
            passed += 1
            print(f"PASS  {name}")
        else:
            print(f"FAIL  {name}")
            print(f"      code:     {code!r}")
            print(f"      expected: {norm(expected)!r}" if not callable(expected)
                  else f"      expected: {expected.__name__}(output) to be True")
            print(f"      got:      {norm(got)!r}")
    print(f"\n{passed}/{len(test)} passed")

if __name__ == "__main__":
    # check(Sandbox(), tests)
    # check(Sandbox(), cpu_tests)
    # check(Sandbox(), memory_tests)
    sd = Sandbox()
    print(sd.run("raise ZeroDivisionError"))
    print(sd.run("print('testidk')"))
    print(sd.run("print(a)"))
    print(sd.run("a = 'a' * 10**9"))
    print(sd.run("for i in range(10000):\n    print('asdf' * 1000);print('alive')"))
    print(sd.run("print('asdf')"))
    print(sd.run("pass"))
    print(sd.run("exit()"))
    print(sd.run("x = 1/x00"))
    print(sd.run("raise KeyboardInterrupt"))
