import sys
from Scanner import Scanner
from Token import *

had_error = False


def main() -> None:
    args = sys.argv[1:]
    if len(args) > 1:
        print("Usage: main.py [script]")
        sys.exit(64)
    elif len(args) == 1:
        run_file(args[0])
    else:
        run_prompt()


def run_file(file_path: str) -> None:
    with open(file_path, "r") as file:
        run(file.read())

    if had_error:
        sys.exit(65)


def run_prompt() -> None:
    while True:
        line = input("> ")
        if len(line) == 0:
            break

        run(line)
        had_error = False


def run(source: str) -> None:
    scanner = Scanner(source, [])
    tokens = scanner.scan_tokens()

    for token in tokens:
        print(f"{token.type} | {token.literal}")


if __name__ == "__main__":
    main()
