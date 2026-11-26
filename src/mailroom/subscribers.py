from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path


@dataclass
class Subscriber:
    first_name: str
    last_name: str
    email: str
    group: str
    joined_on: str
    consent: str


def read_subscribers(path: str) -> list[Subscriber]:
    text = Path(path).read_text(encoding="utf-8")
    lines = text.strip().split("\n")
    subscribers: list[Subscriber] = []
    i = 1  # line 0 is the header, so start at line 1
    while i < len(lines):
        values = lines[i].strip().split(",")
        subscribers.append(
            Subscriber(values[0], values[1], values[2], values[3], values[4], values[5])
        )
        i += 1
    return subscribers


def count_subscribers(subscribers: list[Subscriber]) -> int:
    emails: dict[str, int] = {}
    for subscriber in subscribers:
        emails[subscriber.email] = 1  # a repeated email lands on the same key
    return len(emails)


def count_by_group(subscribers: list[Subscriber]) -> dict[str, int]:
    groups: dict[str, int] = {}
    for subscriber in subscribers:
        groups[subscriber.group] = groups.get(subscriber.group, 0) + 1
    return groups


def count_joined_since(subscribers: list[Subscriber], run_date: str, days: int) -> int:
    end = date.fromisoformat(run_date)
    start = end - timedelta(days=days)
    count = 0
    for subscriber in subscribers:
        joined = date.fromisoformat(subscriber.joined_on)
        if joined >= start and joined <= end:
            count += 1
    return count


def next_send(run_date: str) -> str:
    day = date.fromisoformat(run_date) + timedelta(days=1)
    while day.day != 1:  # walk forward to the 1st of the next month
        day = day + timedelta(days=1)
    while day.weekday() != 0:  # then walk forward to Monday (0)
        day = day + timedelta(days=1)
    return day.isoformat()
