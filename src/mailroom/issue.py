from pathlib import Path


def read_issue(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")
