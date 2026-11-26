import sys
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


SUBJECT_LIMIT = 50


def check_subject(issue_text: str) -> list[str]:
    lines = issue_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if line[0:8] == "Subject:":
            subject = line[8:].strip()  # the text after "Subject:", without spaces
            if subject == "":
                return ["empty"]
            if len(subject) > SUBJECT_LIMIT:
                return ["too long"]
            return []
        i += 1
    return ["missing"]



PREVIEW_LIMIT = 90


def check_preview(issue_text: str) -> list[str]:
    lines = issue_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if line[0:8] == "Preview:":
            preview = line[8:].strip()  # the text after "Preview:", without spaces
            if preview == "":
                return ["empty"]
            if len(preview) > PREVIEW_LIMIT:
                return ["too long"]
            return []
        i += 1
    return ["missing"]


def count_text(text: str, piece: str) -> int:
    # Slide along the text and count every place where piece appears.
    count = 0
    i = 0
    while i <= len(text) - len(piece):
        if text[i : i + len(piece)] == piece:
            count += 1
        i += 1
    return count


def check_greeting(issue_text: str) -> list[str]:
    if count_text(issue_text, "{{first_name}}") == 0:
        return ["missing"]
    return []


def check_link(issue_text: str) -> list[str]:
    links = count_text(issue_text, "](https://")  # where [Button text] meets (https://...)
    if links == 0:
        return ["missing"]
    if links > 1:
        return ["too many"]
    return []


REASON_START = "You're getting this because"
UNSUBSCRIBE_TEXT = "Unsubscribe: {{unsubscribe_url}}"


def check_footer(issue_text: str) -> list[str]:
    lines = issue_text.split("\n")
    has_reason = False
    has_unsubscribe = False
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line[0 : len(REASON_START)] == REASON_START:
            has_reason = True
        if count_text(line, UNSUBSCRIBE_TEXT) > 0:
            has_unsubscribe = True
        i += 1
    problems: list[str] = []
    if not has_reason:
        problems.append("missing reason")
    if not has_unsubscribe:
        problems.append("missing unsubscribe")
    return problems


def check_issue(issue_text: str) -> list[str]:
    problems: list[str] = []
    for problem in check_subject(issue_text):
        problems.append("subject: " + problem)
    for problem in check_preview(issue_text):
        problems.append("preview: " + problem)
    for problem in check_greeting(issue_text):
        problems.append("greeting: " + problem)
    for problem in check_link(issue_text):
        problems.append("link: " + problem)
    for problem in check_footer(issue_text):
        problems.append("footer: " + problem)
    return problems

def get_option(args: list[str], name: str) -> str:
    i = 0
    while i < len(args) - 1:
        if args[i] == name:
            return args[i + 1]
        i += 1
    return ""


# The command line. Only this part may read today's date.
if len(sys.argv) > 1:
    command = sys.argv[1]
    run_date = get_option(sys.argv, "--run-date") or date.today().isoformat()

    if command == "subscribers":
        lines = read_lines("data/subscribers.csv")
        since_days = get_option(sys.argv, "--since-days")
        if since_days:
            count = count_joined_since(lines, run_date, int(since_days))
            print("joined in the last", since_days, "days before", run_date + ":", count)
        else:
            print("subscribers:", count_subscribers(lines))
            groups = count_by_group(lines)
            for group in groups:
                print("  " + group + ":", groups[group])

    if command == "next-send":
        print("next send:", next_send(run_date))

    if command == "check":
        issue_path = sys.argv[2]
        issue_text = Path(issue_path).read_text(encoding="utf-8")
        problems = check_issue(issue_text)
        if len(problems) == 0:
            print(issue_path + ": OK")
        else:
            print(issue_path + ": " + str(len(problems)) + " problem(s)")
            for problem in problems:
                print("  " + problem)
            sys.exit(1)
