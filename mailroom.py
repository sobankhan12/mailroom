import sys
from datetime import date
from pathlib import Path

from issue_checks import check_issue
from schedule import next_send
from subscribers import count_by_group, count_joined_since, count_subscribers, read_lines


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
