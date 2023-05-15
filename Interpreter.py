from AST.Expr import *
from AST.Stmt import *
from TokenType import TokenType
from RuntimeError import LoxRuntimeError, runtime_error


class Interpreter(ExprVisitor, StmtVisitor):
    def interpret(self, statements: list[Stmt]) -> bool:
        try:
            for statement in statements:
                self.execute(statement)

            return False
        except LoxRuntimeError as error:
            runtime_error(error)
            return True

    def execute(self, statement: Stmt):
        statement.accept(self)

    def evaluate(self, expr: Expr) -> any:
        return expr.accept(self)

    def visit_literal_expr(self, expr: LiteralExpr) -> LiteralType:
        return expr.value

    def visit_grouping_expr(self, expr: GroupingExpr) -> any:
        return self.evaluate(expr.expression)

    def visit_unary_expr(self, expr: UnaryExpr) -> any:
        right = self.evaluate(expr.right)

        if expr.operator.type == TokenType.MINUS:
            self.check_number_operand(expr.operator, right)
            return -float(right)
        elif expr.operator.type == TokenType.BANG:
            return not self.is_truthy(right)

        raise Exception(f"Operator: {expr.operator.type}")

    @staticmethod
    def is_truthy(expr: Expr) -> bool:
        if isinstance(expr, LiteralExpr):
            if expr.value is None:
                return False
            if type(expr.value) == bool:
                return expr.value

        return True

    @staticmethod
    def check_number_operand(operator: Token, operand: any) -> None:
        if type(operand) == float:
            return

        raise LoxRuntimeError(operator, "Operand must be a number.")

    @staticmethod
    def check_number_operands(operator: Token, left: any, right: any) -> None:
        if type(left) == float and type(right) == float:
            return

        raise LoxRuntimeError(operator, "Operands must be a numbers.")

    def visit_binary_expr(self, expr: BinaryExpr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        if expr.operator.type == TokenType.PLUS:
            if type(left) == float and type(right) == float:
                return float(left) + float(right)

            elif type(left) == str and type(right) == str:
                return str(left) + str(right)

            raise LoxRuntimeError(expr.operator, "Operands must be two numbers or two strings.")

        elif expr.operator.type == TokenType.MINUS:
            self.check_number_operands(expr.operator, left, right)
            return float(left) - float(right)

        elif expr.operator.type == TokenType.STAR:
            self.check_number_operands(expr.operator, left, right)
            return float(left) * float(right)

        elif expr.operator.type == TokenType.SLASH:
            self.check_number_operands(expr.operator, left, right)

            if float(right) == 0.0:
                raise LoxRuntimeError(expr.operator, "Divide by zero error.")

            return float(left) / float(right)

        elif expr.operator.type == TokenType.GREATER:
            self.check_number_operands(expr.operator, left, right)
            return left > right

        elif expr.operator.type == TokenType.GREATER_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return left >= right

        elif expr.operator.type == TokenType.LESS:
            self.check_number_operands(expr.operator, left, right)
            return left < right

        elif expr.operator.type == TokenType.LESS_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return left <= right

        elif expr.operator.type == TokenType.BANG_EQUAL:
            return not self.is_equal(left, right)

        elif expr.operator.type == TokenType.EQUAL_EQUAL:
            return self.is_equal(left, right)

        raise Exception(f"Left: {type(left)}, right: {type(right)}")

    @staticmethod
    def is_equal(left: any, right: any) -> bool:
        return left == right

    def visit_expression_stmt(self, stmt: ExpressionStmt):
        self.evaluate(stmt.expression)

    def visit_print_stmt(self, stmt: PrintStmt):
        value = self.evaluate(stmt.expression)

        if isinstance(value, str):
            print(f"\"{value}\"")
        else:
            print(str(value))
