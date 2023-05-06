import os
import sys
from collections import abc
from datetime import datetime
from typing import TextIO

EXPR = {
    "Binary": ["Expr left", "Token operator", "Expr right"],
    "Grouping": ["Expr expression"],
    "Literal": ["LiteralType value"],
    "Unary": ["Token operator", "Expr right"],
}

TYPE = dict[str, list[str]]


def main() -> None:
    args = sys.argv[1:]

    if len(args) < 1:
        # print("Usage: python GenerateAST <output_directory>")
        # sys.exit(64)
        args.append("AST")

    try:
        os.mkdir(args[0])
    except FileExistsError:
        pass

    define_ast(args[0], "Expr", EXPR)


def define_ast(output_dir: str, base_name: str, types: TYPE) -> None:
    with open(os.path.join(output_dir, base_name + ".py"), "w") as file:
        now = datetime.now()

        file.write(
            f"""#
# This file was automatically generated by GenerateAST.py on {now.strftime("%d/%m/%Y")} at {now.strftime("%H:%M:%S")}
#

from __future__ import annotations
from dataclasses import dataclass
from Token import Token, LiteralType


class {base_name}:
    def accept(self, visitor: ExprVisitor):
        raise NotImplementedError("Tried calling a virtual method")\n\n\n"""
        )

        define_visitor(file, base_name, types.keys())

        for class_name, fields in types.items():
            file.write(
                f"""


@dataclass
class {class_name}({base_name}):"""
            )

            for field in fields:
                field_type, field_name = field.split(" ")
                file.write(
                    f"""
    {field_name}: {field_type}"""
                )

            file.write(
                f"""

    def accept(self, visitor: {base_name}Visitor):
        return visitor.visit_{class_name.lower()}(self)"""
            )

        file.write("\n")


def define_visitor(file: TextIO, base_name: str, types: abc.KeysView):
    file.write(f"class {base_name}Visitor:\n")

    for t in types:
        file.write(
            f"""    def visit_{t.lower()}(self, expr: {t}):
        raise NotImplementedError("Tried calling a virtual method")

"""
        )


if __name__ == "__main__":
    main()
