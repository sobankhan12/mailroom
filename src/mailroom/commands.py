import sys
from datetime import date

from mailroom.checks import check_issue
from mailroom.issue import read_issue
from mailroom.subscribers import (
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


# The command line. Only this part may read today's date, and only this module prints.
def main() -> None:
    if len(sys.argv) > 1:
        command = sys.argv[1]
        run_date = get_option(sys.argv, "--run-date") or date.today().isoformat()

        if command == "subscribers":
            subscribers = read_subscribers("data/subscribers.csv")
            since_days = get_option(sys.argv, "--since-days")
            if since_days:
                count = count_joined_since(subscribers, run_date, int(since_days))
                print("joined in the last", since_days, "days before", run_date + ":", count)
            else:
                print("subscribers:", count_subscribers(subscribers))
                groups = count_by_group(subscribers)
                for group in groups:
                    print("  " + group + ":", groups[group])

        if command == "next-send":
            print("next send:", next_send(run_date))

        if command == "check":
            issue_path = sys.argv[2]
            issue = read_issue(issue_path)
            problems = check_issue(issue)
            if len(problems) == 0:
                print(issue_path + ": OK")
            else:
                print(issue_path + ": " + str(len(problems)) + " problem(s)")
                for problem in problems:
                    print("  " + problem)
                sys.exit(1)
