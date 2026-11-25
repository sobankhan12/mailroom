import sys
from pathlib import Path

# Position of each column in a line of subscribers.csv (counting from 0).
EMAIL_COLUMN = 2
GROUP_COLUMN = 3


def read_lines(path: str) -> list[str]:
    text = Path(path).read_text(encoding="utf-8")
    return text.strip().split("\n")


def count_subscribers(lines: list[str]) -> int:
    emails: dict[str, int] = {}
    i = 1  # line 0 is the header, so start at line 1
    while i < len(lines):
        values = lines[i].strip().split(",")
        emails[values[EMAIL_COLUMN]] = 1  # a repeated email lands on the same key
        i += 1
    return len(emails)


def count_by_group(lines: list[str]) -> dict[str, int]:
    groups: dict[str, int] = {}
    i = 1  # line 0 is the header, so start at line 1
    while i < len(lines):
        values = lines[i].strip().split(",")
        group = values[GROUP_COLUMN]
        groups[group] = groups.get(group, 0) + 1
        i += 1
    return groups


if len(sys.argv) > 1 and sys.argv[1] == "subscribers":
    lines = read_lines("data/subscribers.csv")
    print("subscribers:", count_subscribers(lines))
    groups = count_by_group(lines)
    for group in groups:
        print("  " + group + ":", groups[group])
