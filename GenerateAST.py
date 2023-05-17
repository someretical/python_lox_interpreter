import os
import sys
from collections import abc
from datetime import datetime
from typing import TextIO

EXPR = {
    "Assign": ["Token name", "Expr value"],
    "Binary": ["Expr left", "Token operator", "Expr right"],
    "Grouping": ["Expr expression"],
    "Literal": ["LiteralType value"],
    "Unary": ["Token operator", "Expr right"],
    "Variable": ["Token name"],
}

STMT = {
    "Block": ["list[Stmt] statements"],
    "Expression": ["Expr expression"],
    "Print": ["Expr expression"],
    "Variable": ["Token name", "Expr initializer"],
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

    define_ast(args[0], "Expr", EXPR, ["from Token import Token, LiteralType"])
    define_ast(args[0], "Stmt", STMT, ["from AST.Expr import Expr", "from Token import Token"])


def define_ast(output_dir: str, base_name: str, types: TYPE, extra_imports=None) -> None:
    if extra_imports is None:
        extra_imports = []

    bn_lower = base_name.lower()

    with open(os.path.join(output_dir, base_name + ".py"), "w") as file:
        now = datetime.now()

        file.write(
            f"""#
# This file was automatically generated by GenerateAST.py on {now.strftime("%d/%m/%Y at %H:%M:%S")}
#

from __future__ import annotations
from dataclasses import dataclass
""")

        for extra in extra_imports:
            file.write(extra + "\n")

        file.write(
            f"""         
\n#
# Interfaces
#

class {base_name}:
    def accept(self, visitor: {base_name}Visitor):
        raise NotImplementedError("Tried calling a virtual method")"""
        )

        file.write("""
\n\n#
# Concrete visitors
#
""")

        define_visitor(file, base_name, types.keys())

        file.write("""
#
# Concrete elements
#""")

        for class_name, fields in types.items():
            file.write(f"""\n\n@dataclass\nclass {class_name}{base_name}({base_name}):\n""")

            for field in fields:
                field_type, field_name = field.split(" ")
                file.write(f"""    {field_name}: {field_type}\n""")

            visitor_parameter = f"visitor: {base_name}Visitor"
            method_name = f"visit_{class_name.lower()}_{bn_lower}"
            file.write(
                f"""\n    def accept(self, {visitor_parameter}):
        return visitor.{method_name}(self)\n"""
            )


def define_visitor(file: TextIO, base_name: str, types: abc.KeysView):
    file.write(f"class {base_name}Visitor:\n")

    bn_lower = base_name.lower()
    for t in types:
        expression_parameter = f"{bn_lower}: {t}{base_name}"
        method_name = f"visit_{t.lower()}_{bn_lower}"
        file.write(
            f"""    def {method_name}(self, {expression_parameter}):
        raise NotImplementedError("Tried calling a virtual method {method_name}")\n\n"""
        )


if __name__ == "__main__":
    main()
