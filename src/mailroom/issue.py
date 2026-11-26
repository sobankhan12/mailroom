from pathlib import Path

LINK_START = "](https://"  # where [Button text] meets (https://...)


def find_links(text: str) -> list[str]:
    links: list[str] = []
    i = 0
    while i <= len(text) - len(LINK_START):
        if text[i : i + len(LINK_START)] == LINK_START:
            start = i + 2  # the link starts after "]("
            end = start
            while end < len(text) and text[end] != ")":
                end += 1
            links.append(text[start:end])
        i += 1
    return links


def fill_in(text: str, piece: str, value: str) -> str:
    # Build a new text, putting value everywhere piece appears.
    result = ""
    i = 0
    while i < len(text):
        if text[i : i + len(piece)] == piece:
            result += value
            i += len(piece)
        else:
            result += text[i]
            i += 1
    return result


class Issue:
    def __init__(self, text: str) -> None:
        self.subject: str | None = None  # None means there is no Subject line
        self.preview: str | None = None  # None means there is no Preview line
        self.body = ""
        for line in text.split("\n"):
            if line[0:8] == "Subject:" and self.subject is None:
                self.subject = line[8:].strip()  # the text after "Subject:", without spaces
            elif line[0:8] == "Preview:" and self.preview is None:
                self.preview = line[8:].strip()  # the text after "Preview:", without spaces
            else:
                self.body += line + "\n"
        self.links = find_links(self.body)

    def personalize(self, first_name: str) -> str:
        return fill_in(self.body, "{{first_name}}", first_name)


def read_issue(path: str) -> Issue:
    return Issue(Path(path).read_text(encoding="utf-8"))
