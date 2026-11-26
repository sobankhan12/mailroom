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
