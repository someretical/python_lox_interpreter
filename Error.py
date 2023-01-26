def error(line: int, message: str) -> None:
    report(line, "", message)


def report(line: int, where: str, message: str) -> None:
    print(f"[line {line}] Error {where}: {message}")
    had_error = True