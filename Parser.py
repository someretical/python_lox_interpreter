from AST.Expr import *
from Error import parse_error
from Token import Token
from TokenType import *


class ParseError(Exception):
    pass


class Parser:
    def __init__(
        self,
        tokens: list[Token],
    ) -> None:
        self.tokens = tokens
        self.current = 0

    def match(self, *types: TokenType) -> bool:
        for type in types:
            if self.check(type):
                self.advance()
                return True

        return False

    def check(self, type: TokenType) -> bool:
        if self.at_end():
            return False

        return self.peek().type == type

    def advance(self) -> Token:
        if not self.at_end():
            self.current += 1

        return self.previous()

    def at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def expression(self) -> Expr:
        return self.equality()

    def error(self, token: Token, message: str) -> ParseError:
        parse_error(token, message)
        return ParseError()

    def synchronise(self) -> None:
        self.advance()

        if (
            self.peek().type == TokenType.CLASS
            or self.peek().type == TokenType.FUN
            or self.peek().type == TokenType.VAR
            or self.peek().type == TokenType.FOR
            or self.peek().type == TokenType.IF
            or self.peek().type == TokenType.WHILE
            or self.peek().type == TokenType.PRINT
            or self.peek().type == TokenType.RETURN
        ):
            return

        self.advance()

    def equality(self) -> Expr:
        expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.BANG_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)

        return expr

    def comparison(self) -> Expr:
        expr = self.term()

        while self.match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)

        return expr

    def term(self) -> Expr:
        expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)

        return expr

    def factor(self) -> Expr:
        expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)

        return expr

    def unary(self) -> Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)

        return self.primary()

    def primary(self) -> Expr:
        if self.match(TokenType.FALSE):
            return Literal(False)
        if self.match(TokenType.TRUE):
            return Literal(True)
        if self.match(TokenType.NIL):
            return Literal(None)

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)

        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expression")
            return Grouping(expr)

        raise SyntaxError(self.peek().to_string() + "Expected expression.")

    def consume(self, type: TokenType, message: str) -> Token:
        if self.check(type):
            return self.advance()

        raise SyntaxError(message)

    def parse(self) -> Expr:
        try:
            return self.expression()
        except ParseError:
            return Expr()
