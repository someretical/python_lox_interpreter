import sys

from AstPrinter import ASTPrinter
from Interpreter import Interpreter
from Parser import Parser
from Scanner import Scanner


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


def run_prompt() -> None:
    interpreter = Interpreter()

    while True:
        line = input("> ")
        if len(line) == 0:
            break

        run(line, interpreter)


def run(source: str, interpreter: Interpreter | None = None) -> None:
    if not interpreter:
        interpreter = Interpreter()

    scanner = Scanner(source, [])
    tokens = scanner.scan_tokens()
    parser = Parser(tokens)

    interpreter.interpret(parser.parse())


if __name__ == "__main__":
    main()
