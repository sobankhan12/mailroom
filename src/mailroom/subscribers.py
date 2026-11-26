from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, ValidationError

from mailroom.errors import DataFileError


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


COLUMNS = "first_name,last_name,email,group,joined_on,consent"


@dataclass
class Problem:
    row: int  # as in a spreadsheet: the header is row 1
    field: str  # which column was wrong, e.g. "email"
    message: str  # what was wrong


@dataclass
class SubscriberReport:
    subscribers: list[Subscriber]  # the good ones
    problems: list[Problem]  # every problem, in row order


def read_lines(path: str) -> list[str]:
    if not Path(path).is_file():
        raise DataFileError("There is no file at " + path + ".")
    lines = Path(path).read_text(encoding="utf-8").strip().split("\n")
    if lines[0].strip() != COLUMNS:
        raise DataFileError(path + " has the wrong columns: it must start with " + COLUMNS + ".")
    return lines


OUR_DOMAIN = "@example.com"


def check_our_rules(row: int, subscriber: Subscriber, run_date: str) -> list[Problem]:
    # Our own rules, for rows the model has already accepted.
    problems: list[Problem] = []
    if subscriber.email[-len(OUR_DOMAIN) :] != OUR_DOMAIN:
        problems.append(Problem(row, "email", "must be an " + OUR_DOMAIN + " address"))
    if subscriber.joined_on > date.fromisoformat(run_date):
        problems.append(Problem(row, "joined_on", "joined after the run date " + run_date))
    return problems


def read_subscribers(path: str, run_date: str) -> SubscriberReport:
    lines = read_lines(path)
    report = SubscriberReport([], [])
    i = 1  # line 0 is the header, so start at line 1
    while i < len(lines):
        row = i + 1  # spreadsheet row number
        values = lines[i].strip().split(",")
        i += 1
        if len(values) != 6:
            report.problems.append(
                Problem(row, "columns", "expected 6 values, found " + str(len(values)))
            )
            continue
        try:
            subscriber = make_subscriber(values)
        except ValidationError as error:
            for problem in error.errors():
                report.problems.append(Problem(row, str(problem["loc"][0]), problem["msg"]))
            continue
        problems = check_our_rules(row, subscriber, run_date)
        if len(problems) == 0:
            report.subscribers.append(subscriber)
        else:
            for problem in problems:
                report.problems.append(problem)
    return report


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
