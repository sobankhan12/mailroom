from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, ValidationError


class Subscriber(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    group: Literal["shawl-lovers", "gift-buyers", "loyal-shoppers"]
    joined_on: date
    consent: str = Field(min_length=1)


def make_subscriber(values: list[str]) -> Subscriber:
    # Every row from outside goes through the model here; bad data raises ValidationError.
    return Subscriber.model_validate(
        {
            "first_name": values[0],
            "last_name": values[1],
            "email": values[2],
            "group": values[3],
            "joined_on": values[4],
            "consent": values[5],
        }
    )


def read_rows(path: str) -> list[list[str]]:
    text = Path(path).read_text(encoding="utf-8")
    lines = text.strip().split("\n")
    rows: list[list[str]] = []
    i = 1  # line 0 is the header, so start at line 1
    while i < len(lines):
        rows.append(lines[i].strip().split(","))
        i += 1
    return rows


def read_subscribers(path: str) -> list[Subscriber]:
    subscribers: list[Subscriber] = []
    for values in read_rows(path):
        subscribers.append(make_subscriber(values))
    return subscribers


@dataclass
class Reason:
    field: str  # which column was wrong, e.g. "email"
    message: str  # Pydantic's words for what was wrong


@dataclass
class ImportedRow:
    first_name: str
    subscriber: Subscriber | None  # None means the row was rejected
    reasons: list[Reason]


def import_signups(path: str) -> list[ImportedRow]:
    imported: list[ImportedRow] = []
    for values in read_rows(path):
        try:
            imported.append(ImportedRow(values[0], make_subscriber(values), []))
        except ValidationError as error:
            reasons: list[Reason] = []
            for problem in error.errors():
                reasons.append(Reason(str(problem["loc"][0]), problem["msg"]))
            imported.append(ImportedRow(values[0], None, reasons))
    return imported


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
        joined = subscriber.joined_on  # already a real date, thanks to the model
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
