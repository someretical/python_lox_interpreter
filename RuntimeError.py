from Token import Token


class LoxRuntimeError(Exception):
    def __init__(self, token: Token, message: str) -> None:
        super().__init__(message)
        self.token = token

def runtime_error(error: LoxRuntimeError) -> None:
    print(f"{error.args[0]}\n[line {error.token.line}]")
