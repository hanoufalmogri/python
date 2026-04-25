from html.parser import HTMLParser
from pathlib import Path
import re
import sys


TERM_PATTERN = re.compile(r"\(\s*[a-zA-Z]+\s*\)")
OUTPUT_DIR = Path("_site")


class TextCollector(HTMLParser):
    """Collect text from headings and paragraphs in rendered HTML pages."""

    def __init__(self) -> None:
        super().__init__()
        self._capture_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "p" or (tag.startswith("h") and len(tag) == 2 and tag[1].isdigit()):
            self._capture_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if self._capture_depth and (tag == "p" or (tag.startswith("h") and len(tag) == 2 and tag[1].isdigit())):
            self._capture_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._capture_depth:
            self.parts.append(data)


def extract_terms(html: str) -> list[str]:
    parser = TextCollector()
    parser.feed(html)
    text = "\n".join(parser.parts)
    return TERM_PATTERN.findall(text)


def main() -> int:
    if not OUTPUT_DIR.exists():
        print(f"Skip post-render scan: {OUTPUT_DIR} does not exist yet.")
        return 0

    for file in OUTPUT_DIR.glob("**/*.html"):
        print(file)
        content = file.read_text(encoding="utf-8")
        terms = extract_terms(content)
        print(terms)
        if len(terms) > 50:
            break

    return 0


if __name__ == "__main__":
    sys.exit(main())
