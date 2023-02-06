from Token import Token
from TokenType import *


def report(line: int, where: str, message: str) -> None:
    print(f"[line {line}] Error {where}: {message}")
    had_error = True


def error(line: int, message: str) -> None:
    report(line, "", message)


def parse_error(token: Token, message: str):
    if token.type == TokenType.EOF:
        report(token.line, " at end", message)
    else:
        report(token.line, " at '" + token.lexeme + "'", message)
