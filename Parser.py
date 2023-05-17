import Token
from AST.Expr import *
from AST.Stmt import *
from Error import parse_error


from TokenType import *


class ParseError(Exception):
    pass


class Parser:
    def __init__(
        self,
        tokens: list[Token],
    ) -> None:
        self.tokens = tokens
        # current = index of current token to be parsed
        self.current = 0

    def match(self, *types: TokenType) -> bool:
        """
        Returns true if the current token to be parsed has the same type as any of the token types passed in
        :param types: token types to match against
        :return:
        """
        for t in types:
            if self.check(t):
                self.advance()
                return True

        return False

    def check(self, token_type: TokenType) -> bool:
        """
        Returns true if the current token to be parsed is of the given type, otherwise false
        :param token_type: the type to match against
        :return:
        """

        if self.at_end():
            return False

        return self.peek().type == token_type

    def advance(self) -> Token:
        """
        Advances to the next token
        :return: the next token to be parsed
        """

        if not self.at_end():
            self.current += 1

        return self.previous()

    def at_end(self) -> bool:
        """
        Returns true if the current token is EOF, otherwise false
        :return:
        """

        return self.peek().type == TokenType.EOF

    def peek(self) -> Token:
        """
        Returns the current token to be parsed
        :return: the next token
        """

        return self.tokens[self.current]

    def previous(self) -> Token:
        """
        Returns the previous parsed token
        :return: the previous parsed token
        """

        return self.tokens[self.current - 1]

    def expression(self) -> Expr:
        """
        expression -> assignment ;
        :return:
        """

        return self.assignment()

    def assignment(self):
        """
        assignment -> IDENTIFIER "=" assignment
                      | equality ;
        :return:
        """

        # Adding types here explicitly to make things more obvious
        expr: Expr = self.equality()

        if self.match(TokenType.EQUAL):
            equals: Token = self.previous()
            value: Expr = self.assignment()

            # The trick is that right before we create the assignment expression node, we look at the left-hand side
            # expression and figure out what kind of assignment target it is. We convert the r-value expression node
            # into an l-value representation.
            # https://craftinginterpreters.com/statements-and-state.html#assignment-syntax
            if isinstance(expr, VariableExpr):
                name: Token = expr.name
                return AssignExpr(name, value)

            self.error(equals, "Invalid assignment target.")

        return expr

    @staticmethod
    def error(token: Token, message: str) -> ParseError:
        parse_error(token, message)
        return ParseError()

    def synchronise(self) -> None:
        """
        Advance until a probable statement boundary is found.
        This is useful for parse error recovery because we do not want cascading errors.

        :return:
        """

        self.advance()

        while not self.at_end():
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
        """
        equality -> comparison ( ( "!=" | "==" ) comparison )* ;
        :return:
        """

        expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.BANG_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def comparison(self) -> Expr:
        """
        comparison -> term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
        :return:
        """

        expr = self.term()

        while self.match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = self.previous()
            right = self.term()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def term(self) -> Expr:
        """
        term -> factor ( ( "-" | "+" ) factor )* ;
        :return:
        """

        expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def factor(self) -> Expr:
        """
        factor -> unary ( ( "/" | "*" ) unary )* ;
        :return:
        """

        expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def unary(self) -> Expr:
        """
        unary -> ( "!" | "-" ) unary
                 | primary ;
        :return:
        """

        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return UnaryExpr(operator, right)

        return self.primary()

    def primary(self) -> Expr:
        """
        primary -> NUMBER | STRING | "true" | "false" | "nil"
                   | "(" expression ")"
                   | IDENTIFIER ;
        :return:
        """

        if self.match(TokenType.FALSE):
            return LiteralExpr(False)
        if self.match(TokenType.TRUE):
            return LiteralExpr(True)
        if self.match(TokenType.NIL):
            return LiteralExpr(None)

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return LiteralExpr(self.previous().literal)

        if self.match(TokenType.IDENTIFIER):
            return VariableExpr(self.previous())

        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expression")
            return GroupingExpr(expr)

        raise self.error(self.peek(), "Expected expression.")

    def consume(self, token_type: TokenType, message: str) -> Token:
        """
        Checks the current token to be parsed against the token type provided.
        If it matches, then the current token to be parsed is consumed and the next token is returned.
        If it doesn't match, raise a parse error with the provided message.
        :param token_type:
        :param message:
        :return:
        """

        if self.check(token_type):
            return self.advance()

        raise self.error(self.peek(), message)

    def statement(self):
        """
        statement -> exprStmt
                     | printStmt
                     | block ;
        :return:
        """

        if self.match(TokenType.PRINT):
            return self.print_statement()

        if self.match(TokenType.LEFT_BRACE):
            return BlockStmt(self.block())

        return self.expression_statement()

    def print_statement(self):
        """
        printStmt -> "print" expression ";" ;
        :return:
        """

        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return PrintStmt(value)

    def block(self):
        """
        block -> "{" declaration* "}" ;
        :return:
        """

        statements = []

        while not self.check(TokenType.RIGHT_BRACE) and not self.at_end():
            statements.append(self.declaration())

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")

        return statements

    def expression_statement(self):
        """
        exprStmt -> expression ";" ;
        :return:
        """

        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return ExpressionStmt(value)

    def declaration(self):
        """
        declaration -> varDecl
                       | statement ;
        :return:
        """

        try:
            if self.match(TokenType.VAR):
                return self.variable_declaration()

            return self.statement()
        except ParseError:
            self.synchronise()
            return None

    def variable_declaration(self):
        """
        varDecl -> "var" IDENTIFIER ( "=" expression )? ";" ;
        :return:
        """

        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer = LiteralExpr(None)

        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' variable declaration.")

        return VariableStmt(name, initializer)

    def parse(self) -> list[Stmt]:
        """
        Parse the provided tokens into an AST

        program -> declaration* EOF ;

        :return: An expression object representing the AST
        """

        statements = []

        while not self.at_end():
            statement = self.declaration()
            if statement:
                statements.append(statement)

        return statements
