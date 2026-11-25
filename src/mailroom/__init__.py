from pathlib import Path

# Position of each column in a line of subscribers.csv (counting from 0).
EMAIL_COLUMN = 2
GROUP_COLUMN = 3


def read_lines(path: str) -> list[str]:
    text = Path(path).read_text(encoding="utf-8")
    return text.strip().split("\n")


def count_unique(lines: list[str], column: int) -> int:
    seen: dict[str, int] = {}
    i = 1  # line 0 is the header, so start at line 1
    while i < len(lines):
        values = lines[i].strip().split(",")
        seen[values[column]] = 1  # a repeated value lands on the same key
        i += 1
    return len(seen)


def main() -> None:
    lines = read_lines("data/subscribers.csv")
    print("subscribers:", count_unique(lines, EMAIL_COLUMN))
    print("groups:", count_unique(lines, GROUP_COLUMN))
