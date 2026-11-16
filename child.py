import sys
import resource

def main():
    argv = [int(elem) for elem in sys.argv[1:]]
    env = {}
    while True:
        try:
            resource.setrlimit(resource.RLIMIT_CPU, (argv[0] * 4, argv[0] * 4 + 10))
            resource.setrlimit(resource.RLIMIT_AS, (argv[1] * 1024 * 1024, argv[1] * 1024 * 1024))
            line = sys.stdin.readline()
            if line == "":
                return
            try:
                exec(line, env)
                print("\n")
            except Exception as err:
                print(err)
            print("end of this chunkEOC")
            sys.stdout.flush()
        except Exception as err:
            print(err)
            return

main()
