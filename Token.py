from TokenType import *

LiteralType = str | float | None


class Token:
    def __init__(
        self, type: TokenType, lexeme: str, literal: LiteralType, line: int
    ) -> None:
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def to_string(self) -> str:
        return self.type + " " + self.lexeme + " " + self.literal
