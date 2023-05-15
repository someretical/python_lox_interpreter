#
# This file was automatically generated by GenerateAST.py on 15/05/2023 at 21:10:31
#

from __future__ import annotations
from dataclasses import dataclass
from AST.Expr import Expr
         

#
# Interfaces
#

class Stmt:
    def accept(self, visitor: StmtVisitor):
        raise NotImplementedError("Tried calling a virtual method")


#
# Concrete visitors
#
class StmtVisitor:
    def visit_expression_stmt(self, stmt: ExpressionStmt):
        raise NotImplementedError("Tried calling a virtual method")

    def visit_print_stmt(self, stmt: PrintStmt):
        raise NotImplementedError("Tried calling a virtual method")


#
# Concrete elements
#

@dataclass
class ExpressionStmt(Stmt):
    expression: Expr

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_expression_stmt(self)


@dataclass
class PrintStmt(Stmt):
    expression: Expr

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_print_stmt(self)