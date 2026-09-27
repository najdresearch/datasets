"""Deterministic parsers recovered from the historical Najd question collector."""

from __future__ import annotations

import re
from html import unescape
from html.parser import HTMLParser
from typing import Callable


class _VisibleText(HTMLParser):
    """Small dependency-free HTML-to-lines adapter for direct article snapshots."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.lines: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript", "svg"}:
            self._skip += 1
        if tag in {"br", "p", "div", "li", "h1", "h2", "h3", "h4"}:
            self.lines.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript", "svg"} and self._skip:
            self._skip -= 1
        if tag in {"p", "div", "li", "h1", "h2", "h3", "h4", "article"}:
            self.lines.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip:
            self.lines.append(data)


def html_to_lines(html: str) -> list[str]:
    parser = _VisibleText()
    parser.feed(html)
    text = unescape("".join(parser.lines))
    return [clean_markdown(line) for line in text.splitlines() if clean_markdown(line)]


def parse_almrsal_riddles(html: str) -> list[tuple[str, str]]:
    lines = html_to_lines(html)
    pairs: list[tuple[str, str]] = []
    for index, line in enumerate(lines):
        if not re.match(r"^اللغز\s*[:：]", line):
            continue
        question = clean_markdown(re.sub(r"^اللغز\s*[:：]\s*", "", line))
        answer = ""
        for candidate in lines[index + 1 : index + 12]:
            if re.match(r"^اللغز\s*[:：]", candidate):
                break
            match = re.match(r"^(?:الإجابة|الجواب|الحل)\s*[:：]?\s*(.*)$", candidate)
            if match:
                answer = clean_markdown(match.group(1))
                if not answer:
                    following = lines[index + 2 : index + 12]
                    answer = next((clean_markdown(item) for item in following if item), "")
                break
        if (
            question
            and answer
            and ("؟" in question or "?" in question)
            and len(question) <= 600
            and len(answer) <= 300
        ):
            pairs.append((question, answer))
    # Several Almrsal articles use an HTML table: number, question, answer.
    for index, line in enumerate(lines[:-2]):
        if not re.fullmatch(r"\d{1,3}", line):
            continue
        question, answer = lines[index + 1], lines[index + 2]
        if ("؟" in question or "?" in question) and answer not in {"السؤال", "الجواب"}:
            if len(question) <= 600 and len(answer) <= 300:
                pairs.append((question, answer))
    unique: list[tuple[str, str]] = []
    seen: set[str] = set()
    for question, answer in pairs:
        key = normalized(question)
        if key and key not in seen:
            seen.add(key)
            unique.append((question, answer))
    return unique


def clean_markdown(text: str) -> str:
    text = re.sub(r"!\[[^]]*]\([^)]*\)", "", text)
    text = re.sub(r"\[\[?\d+]?]\([^)]*\)", "", text)
    text = re.sub(r"\[([^]]+)]\([^)]*\)", r"\1", text)
    text = re.sub(r"^[#>*_\s]+|[#>*_\s]+$", "", text.strip())
    return re.sub(r"\s+", " ", text).strip(" .\u00a0")


def parse_numbered_pairs(
    markdown: str, *, start_marker: str, answer_prefix: bool
) -> list[tuple[str, str]]:
    lines = [line.strip() for line in markdown.splitlines()]
    start = next((index for index, line in enumerate(lines) if start_marker in line), 0)
    pairs: list[tuple[str, str]] = []
    for index in range(start, len(lines)):
        match = re.match(r"^\s*\d+\.\s+(?:##\s*)?(.*)", lines[index])
        if not match:
            continue
        question = clean_markdown(match.group(1))
        if "؟" not in question and "?" not in question:
            continue
        answer = ""
        for candidate in lines[index + 1 : index + 6]:
            candidate = candidate.strip()
            if not candidate or candidate.startswith(("#", "![", "[")):
                continue
            if re.match(r"^\d+\.\s+", candidate):
                break
            if answer_prefix and not re.match(r"^(?:الحل|الإجابة|الجواب)\s*[:：]", candidate):
                continue
            answer = re.sub(r"^(?:الحل|الإجابة|الجواب)\s*[:：]\s*", "", candidate)
            answer = clean_markdown(answer)
            break
        if question and answer and len(question) <= 600 and len(answer) <= 300:
            pairs.append((question, answer))
    return pairs


def parse_twinkl_riddles(markdown: str) -> list[tuple[str, str]]:
    return parse_numbered_pairs(markdown, start_marker="القسم الأول", answer_prefix=True)


def parse_twinkl_islamic(markdown: str) -> list[tuple[str, str]]:
    return parse_numbered_pairs(markdown, start_marker="سؤالًا عن القرآن", answer_prefix=False)


def parse_numbered(markdown: str) -> list[tuple[str, str]]:
    return parse_numbered_pairs(markdown, start_marker="", answer_prefix=False)


def parse_mawdoo3(markdown: str) -> list[tuple[str, str]]:
    lines = [line.strip() for line in markdown.splitlines()]
    pairs: list[tuple[str, str]] = []
    for index, line in enumerate(lines):
        if not re.match(r"^###\s+.*اللغز", line):
            continue
        values = []
        for candidate in lines[index + 1 : index + 9]:
            if not candidate or candidate.startswith(("#", "![")):
                continue
            value = clean_markdown(candidate)
            if value:
                values.append(value)
            if len(values) == 2:
                break
        if len(values) == 2 and ("؟" in values[0] or "?" in values[0]):
            pairs.append((values[0], values[1]))
    return pairs


def parse_qusama(markdown: str) -> list[tuple[str, str]]:
    start = markdown.find("مجموعه الغاز مع الحل")
    end = markdown.find("اتمني يعجبكم", start)
    if start < 0:
        return []
    body = markdown[start : end if end > start else None]
    pattern = re.compile(
        r"(?:^|\s)(\d+)\s*/\s*(.*?[؟?])\s*(.*?)"
        r"(?=(?:\s+\d+\s*/)|(?:\s+اتمني)|$)",
        re.DOTALL,
    )
    pairs = []
    for _, question, answer in pattern.findall(body):
        question = clean_markdown(question)
        answer = clean_markdown(answer)
        embedded = re.match(r"^(.*?)\s*/\s*(.*?[؟?])\s*(.+)$", answer)
        if embedded:
            first_answer, second_question, second_answer = map(clean_markdown, embedded.groups())
            if question and first_answer:
                pairs.append((question, first_answer))
            if second_question and second_answer:
                pairs.append((second_question, second_answer))
            continue
        if question and answer and len(question) <= 600 and len(answer) <= 300:
            pairs.append((question, answer))
    return pairs


PARSERS: dict[str, Callable[[str], list[tuple[str, str]]]] = {
    "twinkl_riddles": parse_twinkl_riddles,
    "twinkl_islamic": parse_twinkl_islamic,
    "qusama": parse_qusama,
    "mawdoo3": parse_mawdoo3,
    "almrsal_riddles": parse_almrsal_riddles,
    "numbered": parse_numbered,
}


def normalized(text: str) -> str:
    text = re.sub(r"[ًٌٍَُِّْـ]", "", text.lower())
    text = text.translate(str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ى": "ي", "ة": "ه"}))
    return re.sub(r"\W+", " ", text, flags=re.UNICODE).strip()
