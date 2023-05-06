from AST.Expr import *
from TokenType import TokenType


class ASTPrinter(ExprVisitor):
    def print(self, expr: Expr):
        return expr.accept(self)

    def parenthesize(self, name: str, *expressions: Expr) -> str:
        # recursion !
        return f"({name} {' '.join([expr.accept(self) for expr in expressions])})"

    def visit_binary(self, expr: Binary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping(self, expr: Grouping) -> str:
        return self.parenthesize("group", expr.expression)

    def visit_literal(self, expr: Literal) -> str:
        if not expr.value:
            return "None"

        return str(expr.value)

    def visit_unary(self, expr: Unary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.right)


def main() -> None:
    expr = Binary(
        Unary(
            Token(TokenType.MINUS, "-", None, 1),
            Literal(123),
        ),
        Token(TokenType.STAR, "*", None, 1),
        Grouping(Literal(45.67)),
    )

    print(ASTPrinter().print(expr))


if __name__ == "__main__":
    main()
