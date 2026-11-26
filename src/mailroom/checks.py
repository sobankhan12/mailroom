from mailroom.issue import Issue

SUBJECT_LIMIT = 50


def check_subject(issue: Issue) -> list[str]:
    if issue.subject is None:
        return ["missing"]
    if issue.subject == "":
        return ["empty"]
    if len(issue.subject) > SUBJECT_LIMIT:
        return ["too long"]
    return []


PREVIEW_LIMIT = 90


def check_preview(issue: Issue) -> list[str]:
    if issue.preview is None:
        return ["missing"]
    if issue.preview == "":
        return ["empty"]
    if len(issue.preview) > PREVIEW_LIMIT:
        return ["too long"]
    return []


def count_text(text: str, piece: str) -> int:
    # Slide along the text and count every place where piece appears.
    count = 0
    i = 0
    while i <= len(text) - len(piece):
        if text[i : i + len(piece)] == piece:
            count += 1
        i += 1
    return count


def check_greeting(issue: Issue) -> list[str]:
    if count_text(issue.body, "{{first_name}}") == 0:
        return ["missing"]
    return []


def check_link(issue: Issue) -> list[str]:
    if len(issue.links) == 0:
        return ["missing"]
    if len(issue.links) > 1:
        return ["too many"]
    return []


REASON_START = "You're getting this because"
UNSUBSCRIBE_TEXT = "Unsubscribe: {{unsubscribe_url}}"


def check_footer(issue: Issue) -> list[str]:
    lines = issue.body.split("\n")
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


def check_issue(issue: Issue) -> list[str]:
    problems: list[str] = []
    for problem in check_subject(issue):
        problems.append("subject: " + problem)
    for problem in check_preview(issue):
        problems.append("preview: " + problem)
    for problem in check_greeting(issue):
        problems.append("greeting: " + problem)
    for problem in check_link(issue):
        problems.append("link: " + problem)
    for problem in check_footer(issue):
        problems.append("footer: " + problem)
    return problems
