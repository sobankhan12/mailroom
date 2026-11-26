import sys
from datetime import date

from mailroom.checks import check_issue
from mailroom.errors import DataFileError
from mailroom.issue import read_issue
from mailroom.subscribers import (
    SubscriberReport,
    count_by_group,
    count_joined_since,
    count_subscribers,
    next_send,
    read_subscribers,
)


def get_option(args: list[str], name: str) -> str:
    i = 0
    while i < len(args) - 1:
        if args[i] == name:
            return args[i + 1]
        i += 1
    return ""


def get_file(args: list[str], command: str) -> str:
    # The file comes right after the command, e.g. mailroom import data/new-signups.csv
    if len(args) < 3 or args[2][0:2] == "--":
        stop("Give a file: mailroom " + command + " <file>")
    return args[2]


def stop(sentence: str) -> None:
    # A user's mistake: one plain sentence, no traceback, exit 2.
    print(sentence)
    sys.exit(2)


def print_problems(report: SubscriberReport) -> None:
    print(str(len(report.problems)) + " problem(s):")
    for problem in report.problems:
        print("  row " + str(problem.row) + ", " + problem.field + ": " + problem.message)


# The command line. Only this part may read today's date, and only this module prints.
def main() -> None:
    if len(sys.argv) > 1:
        command = sys.argv[1]
        run_date = get_option(sys.argv, "--run-date") or date.today().isoformat()
        try:
            run_command(command, run_date)
        except DataFileError as error:
            stop(str(error))


def run_command(command: str, run_date: str) -> None:
    if command == "subscribers":
        report = read_subscribers("data/subscribers.csv", run_date)
        subscribers = report.subscribers
        since_days = get_option(sys.argv, "--since-days")
        if since_days:
            count = count_joined_since(subscribers, run_date, int(since_days))
            print("joined in the last", since_days, "days before", run_date + ":", count)
        else:
            print("subscribers:", count_subscribers(subscribers))
            groups = count_by_group(subscribers)
            for group in groups:
                print("  " + group + ":", groups[group])
        if len(report.problems) > 0:
            print_problems(report)
            sys.exit(1)

    if command == "next-send":
        print("next send:", next_send(run_date))

    if command == "check":
        issue_path = get_file(sys.argv, command)
        issue = read_issue(issue_path)
        problems = check_issue(issue)
        if len(problems) == 0:
            print(issue_path + ": OK")
        else:
            print(issue_path + ": " + str(len(problems)) + " problem(s)")
            for problem in problems:
                print("  " + problem)
            sys.exit(1)

    if command == "import":
        report = read_subscribers(get_file(sys.argv, command), run_date)
        for subscriber in report.subscribers:
            print("accepted:", subscriber.first_name)
        if len(report.problems) > 0:
            print_problems(report)
            sys.exit(1)
