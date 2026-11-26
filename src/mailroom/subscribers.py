from datetime import date, timedelta
from pathlib import Path

# Position of each column in a line of subscribers.csv (counting from 0).
EMAIL_COLUMN = 2
GROUP_COLUMN = 3
JOINED_COLUMN = 4


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


def count_joined_since(lines: list[str], run_date: str, days: int) -> int:
    end = date.fromisoformat(run_date)
    start = end - timedelta(days=days)
    count = 0
    i = 1  # line 0 is the header, so start at line 1
    while i < len(lines):
        values = lines[i].strip().split(",")
        joined = date.fromisoformat(values[JOINED_COLUMN])
        if joined >= start and joined <= end:
            count += 1
        i += 1
    return count


def next_send(run_date: str) -> str:
    day = date.fromisoformat(run_date) + timedelta(days=1)
    while day.day != 1:  # walk forward to the 1st of the next month
        day = day + timedelta(days=1)
    while day.weekday() != 0:  # then walk forward to Monday (0)
        day = day + timedelta(days=1)
    return day.isoformat()
