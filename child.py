import sys
import resource
import traceback
import contextlib
import io
import json


def block_mischief(event,arg):
    if event=='open' or event.split('.')[0] in ['subprocess', 'os', 'shutil', 'winreg']:
        raise IOError('file write forbidden')


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
            try:
                output= {"status": "ok"}
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    exec(code, env)
            except Exception as err:
                output["error"] = "".join(traceback.format_exception(err))
                output["status"] = "error"
            except BaseException as err:
                raise Exception("BaseException caught")
            output["output"] = out.getvalue()
            print(json.dumps(output), "\nend of this chunkEOC")
            sys.stdout.flush()
    except Exception as err:
        output["error"] = "".join(traceback.format_exception(err))
        output["status"] = "error"
        output["output"] = out.getvalue()
        print(json.dumps(output), "\nend of this chunkEOC")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
