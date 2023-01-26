from TokenType import *
from Token import *
from Error import *
import re

KEYWORDS = {
    "and": TokenType.AND,
    "class": TokenType.CLASS,
    "else": TokenType.ELSE,
    "false": TokenType.FALSE,
    "for": TokenType.FOR,
    "fun": TokenType.FUN,
    "if": TokenType.IF,
    "nil": TokenType.NIL,
    "or": TokenType.OR,
    "print": TokenType.PRINT,
    "return": TokenType.RETURN,
    "super": TokenType.SUPER,
    "this": TokenType.THIS,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE,
}

# In C, we can compare chars against each other with <, > but in python that is not possible.
# Hence why I am just rolling with regular expressions to match those characters.
IDENT_START = re.compile('[a-zA-Z_]')
IDENT_CONT = re.compile('[a-zA-Z0-9_]')

class Scanner:
    def __init__(
        self,
        source: str,
        tokens: list[Token],
        start: int = 0,
        current: int = 0,
        line: int = 1,
    ) -> None:
        self.source = source
        self.tokens = tokens
        self.start = start
        self.current = current
        self.line = line

    def scan_tokens(self) -> list[Token]:
        while not self.at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def at_end(self) -> bool:
        return self.current >= len(self.source)

    def scan_token(self) -> None:
        char = self.advance()

        if char == "(":
            self.add_token(TokenType.LEFT_PAREN)
        elif char == ")":
            self.add_token(TokenType.RIGHT_PAREN)
        elif char == "{":
            self.add_token(TokenType.LEFT_BRACE)
        elif char == "}":
            self.add_token(TokenType.RIGHT_BRACE)
        elif char == ",":
            self.add_token(TokenType.COMMA)
        elif char == ".":
            self.add_token(TokenType.DOT)
        elif char == "-":
            self.add_token(TokenType.MINUS)
        elif char == "+":
            self.add_token(TokenType.PLUS)
        elif char == ";":
            self.add_token(TokenType.SEMICOLON)
        elif char == "*":
            self.add_token(TokenType.STAR)
        elif char == "!":
            self.add_token(TokenType.BANG_EQUAL if self.match("=") else TokenType.BANG)
        elif char == "=":
            self.add_token(
                TokenType.EQUAL_EQUAL if self.match("=") else TokenType.EQUAL
            )
        elif char == "<":
            self.add_token(TokenType.LESS_EQUAL if self.match("=") else TokenType.LESS)
        elif char == ">":
            self.add_token(
                TokenType.GREATER_EQUAL if self.match("=") else TokenType.GREATER
            )
        elif char == "/":
            if self.match("/"):
                while self.peek() != "\n" and not self.at_end():
                    self.advance()
            else:
                self.add_token(TokenType.SLASH)
        elif char == " " or char == "\r" or char == "\t":
            pass
        elif char == "\n":
            line += 1
        elif char == "\n":
            self.string()
        elif char.isdigit():
            self.number()
        elif IDENT_START.match(char):
            self.identifier()
        else:
            error(self.line, "Unexpected character.")

    def advance(self) -> str:
        self.current += 1
        return self.source[self.current - 1]

    def add_token(self, type: TokenType, literal: LiteralType = None) -> None:
        self.tokens.append(
            Token(type, self.source[self.start : self.current], literal, self.line)
        )

    def match(self, expected: str) -> bool:
        if self.at_end():
            return False

        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def peek(self) -> str:
        if self.at_end():
            return ""

        return self.source[self.current]

    def string(self) -> None:
        while self.peek() != '"' and not self.at_end():
            if self.peek() == "\n":
                self.line += 1
            self.advance()

        if self.at_end():
            error(self.line, "Unterminated string.")
            return

        self.advance()

        self.add_token(TokenType.STRING, self.source[self.start + 1, self.current - 1])

    def number(self) -> None:
        while self.peek().isdigit():
            self.advance()

        if self.peek() == "." and self.peek_next().isdigit():
            self.advance()

            # parse the fractional part
            while self.peek().isdigit():
                self.advance()

        self.add_token(TokenType.NUMBER, float(self.source[self.start, self.current]))

    def peek_next(self) -> str:
        if len(self.source) >= self.current + 1:
            return ""

        return self.source[self.current + 1]

    def identifier(self) -> None:
        while IDENT_CONT.match(self.peek()):
            self.advance()

        text = self.source[self.start, self.current]
        
        if text in KEYWORDS:
            self.add_token(KEYWORDS[text])
        else:
            self.add_token(TokenType.IDENTIFIER)
