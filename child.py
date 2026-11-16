import sys
import resource


def block_mischief(event,arg):
    if event=='open' or event.split('.')[0] in ['subprocess', 'os', 'shutil', 'winreg']:
        raise IOError('file write forbidden')


def main():
    argv = [int(elem) for elem in sys.argv[1:]]
    env = {}
    sys.addaudithook(block_mischief)
    resource.setrlimit(resource.RLIMIT_CPU, (argv[0] * 4, argv[0] * 4 + 10))
    resource.setrlimit(resource.RLIMIT_AS, (argv[1] * 1024 * 1024, argv[1] * 1024 * 1024))

    while True:
        try:
            code = ""
            for line in sys.stdin:
                if line == "end of this chunkEOC\n":
                    break
                code += line
            if code == "":
                return
            try:
                exec(code, env)
            except Exception as err:
                print(err)
            except BaseException as err:
                return
            print("\nend of this chunkEOC")
            sys.stdout.flush()
        except Exception as err:
            print(err)
            return


if __name__ == "__main__":
    main()
