from TokenType import *
from dataclasses import *

LiteralType = str | float | None


@dataclass
class Token:
    type: TokenType
    lexeme: str
    literal: LiteralType
    line: int

    def to_string(self) -> str:
        return self.type.name + " " + self.lexeme + " " + str(self.literal)
