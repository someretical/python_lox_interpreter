from __future__ import annotations
from dataclasses import *
from RuntimeError import *


@dataclass
class Environment:
    enclosing: Environment | None = None
    values: dict[str, any] = field(default_factory=dict)

    def define(self, name: str, value: any):
        self.values[name] = value

    def get(self, name: Token):
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name: Token, value: any):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        if self.enclosing is not None:
            return self.enclosing.assign(name, value)

        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
