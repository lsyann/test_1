import subprocess
import select
import signal
import json

class Sandbox:
    def __init__(self):
        self.child: subprocess.Popen = None
        self.timeout = "2"
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
        code += "\n"
        if self.child is None or self.child.poll() is not None:
            self.raise_child()
        try:
            self.child.stdin.write(code)
            self.child.stdin.write("\nend of this chunkEOC\n")
            self.child.stdin.flush()
            timeout = select.poll()
            timeout.register(self.child.stdout)
            if len(timeout.poll(1000 * int(self.timeout))) == 0:
                self.reset_child()
                return "process timeout"
            output = ""
            for line in self.child.stdout:
                if line == "end of this chunkEOC\n":
                    return output
                output += line
        except Exception as err:
            return f"problem with sandbox: {err}"

RESET = "problem with child, the child was reset"
TIMEOUT = "process timeout"


def main():
    sd = Sandbox()
    for test in tests:
        sd.run(test)


def nonempty(out):
    return out != ""

tests = [
    # (name, code, expected)  expected = exact string, or a function(output) -> bool
    ("assignment, no output",   "x = 1",                                    "no output"),
    ("state persists",          "print(x)",                                 "1\n"),
    ("comment only",            "# hi",                                     "no output"),
    ("whitespace only",         "    ",                                     "no output"),
    ("semicolons",              "a = 1; b = 2; print(a + b)",               "3\n"),
    ("one-line loop",           "for i in range(3): print(i)",              "0\n1\n2\n"),
    ("embedded newline",        "print('a\\nb')",                           "a\nb\n"),
    ("empty print",             "print()",                                  "no output\n"),
    ("unicode",                 "print('héllo ✓ 日本')",                     "héllo ✓ 日本\n"),
    ("import",                  "import math; print(math.sqrt(16))",        "4.0\n"),
    ("lambda",                  "f = lambda n: n * 2; print(f(21))",        "42\n"),
    ("stderr only",             "import sys; print('e', file=sys.stderr)",  "no output"),

    ("runtime error",           "1 / 0",                                    "division by zero\n"),
    ("state survives error",    "print(x)",                                 "1\n"),
    ("name error",              "print(nope)",                              "name 'nope' is not defined\n"),
    ("syntax error",            "def f(",                                   nonempty),  # message text varies by Python version
    ("unexpected indent",       "  x = 2",                                  nonempty),

    # these kill the child: the parent should report a reset
    ("exit()",                  "exit()",                                   RESET),
    ("state gone after reset",  "print(x)",                                 "name 'x' is not defined\n"),
    ("os._exit",                "import os; os._exit(0)",                   RESET),
    ("KeyboardInterrupt",       "raise KeyboardInterrupt",                  RESET),
    ("kill itself",             "import os, signal; os.kill(os.getpid(), signal.SIGKILL)", RESET),

    # these must hit the timeout (they are safe only if your handler kills the child)
    ("busy loop",               "while True: pass",                         TIMEOUT),
    ("sleep",                   "import time; time.sleep(30)",              TIMEOUT),
    ("input() waits for stdin", "input()",                                  TIMEOUT),

    ("works after timeouts",    "print('alive')",                           "alive\n"),
]

memory_tests = [
    # --- allocation beyond the limit must fail cleanly ---
    ("huge string",        "exec(\"try: x = 'a' * 10**9\\nexcept MemoryError: print('MemoryError')\")", "MemoryError\n"),
    ("huge list",          "exec(\"try: x = [0] * 10**9\\nexcept MemoryError: print('MemoryError')\")",  "MemoryError\n"),
    ("gradual growth",     "exec(\"try: x = [bytearray(10**7) for _ in range(100)]\\nexcept MemoryError: print('MemoryError')\")", "MemoryError\n"),

    # --- the child must survive a MemoryError and keep its state ---
    ("alive after error",  "print('alive')",                         "alive\n"),
    ("old state intact",   "a = 5; print(a)",                        "5\n"),
    ("failed name unbound","print('x' in dir())",                    "False\n"),   # x must not be half-assigned

    # --- allocations under the limit must still work ---
    ("small allocation",   "y = [0] * 1000; print(len(y))",          "1000\n"),
    ("100 MB allocation",  "z = 'a' * (100 * 10**6); print(len(z))", "100000000\n"),
    ("free then reuse",    "del z; w = 'b' * (100 * 10**6); print(len(w))", "100000000\n"),

    # --- the limit must not be liftable by the code itself ---
    ("raise own limit",    "import resource; resource.setrlimit(resource.RLIMIT_AS, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))", nonempty),  # error either way
    ("still limited after","exec(\"try: x = 'a' * 10**9\\nexcept MemoryError: print('MemoryError')\")", "MemoryError\n"),
]

cpu_tests = [
    # --- work that fits in the limits must pass ---
    ("light compute",      "print(sum(range(10**6)))",               "499999500000\n"),
    ("heavier compute",    "print(sum(range(10**7)))",               "49999995000000\n"),   # ~0.3 to 1 s

    # --- wall-clock timeout (parent kills the child) ---
    ("busy loop",          "while True: pass",                       TIMEOUT),
    ("works after kill",   "print('alive')",                         "alive\n"),
    ("state gone",         "print('a' in dir())",                    "False\n"),             # fresh child
    ("sleep, no CPU",      "import time; time.sleep(60)",            TIMEOUT),
    ("blocked on stdin",   "input()",                                TIMEOUT),
    ("output flood",       "exec('while True: print(\"x\" * 1000)')", TIMEOUT),             # also needs an output cap in the parent
    ("alive after flood",  "print('alive')",                         "alive\n"),

    # --- the CPU backstop must not kill a healthy persistent child ---
    # run the heavy compute many times on the SAME child; cumulative CPU time exceeds a tight RLIMIT_CPU
    *[(f"cumulative {i}",  "print(sum(range(10**7)))",               "49999995000000\n") for i in range(10)],
]


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
    print(Sandbox().run("raise ZeroDivisionError"))
    print(Sandbox().run("print('testidk')"))
    print(Sandbox().run("print(a)"))
    print(Sandbox().run("a = 'a' * 10**9"))
    print(Sandbox().run("for i in range(10000):\n    print('asdf' * 1000)"))
    print(Sandbox().run("print('asdf')"))
    print(Sandbox().run("pass"))
