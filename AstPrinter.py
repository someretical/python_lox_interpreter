from AST.Expr import *
from TokenType import TokenType


class ASTPrinter(ExprVisitor):
    def print(self, expr: Expr):
        return expr.accept(self)

    def parenthesize(self, name: str, *expressions: Expr) -> str:
        # recursion !
        return f"({name} {' '.join([expr.accept(self) for expr in expressions])})"

    def visit_binary_expr(self, expr: BinaryExpr) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr: GroupingExpr) -> str:
        return self.parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr: LiteralExpr) -> str:
        return str(expr.value)

    def visit_unary_expr(self, expr: UnaryExpr) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.right)


def main() -> None:
    expr = BinaryExpr(
        UnaryExpr(
            Token(TokenType.MINUS, "-", None, 1),
            LiteralExpr(123),
        ),
        Token(TokenType.STAR, "*", None, 1),
        GroupingExpr(LiteralExpr(45.67)),
    )

    print(ASTPrinter().print(expr))


if __name__ == "__main__":
    main()
