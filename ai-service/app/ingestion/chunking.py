"""
Splits a document's Markdown body into chunks bounded by headings (## through
####), rather than fixed-size windows, so a chunk maps onto a coherent
documentation section (DECISIONS.md: "chunk by heading"). H1 is assumed to be
the page title and is not treated as a boundary.
"""

import re
from dataclasses import dataclass

HEADING_RE = re.compile(r"^(#{2,4})\s+(.*)$", re.MULTILINE)

DEFAULT_MIN_CHUNK_CHARS = 40


@dataclass
class HeadingChunk:
    heading: str | None
    text: str


def chunk_by_heading(
    markdown_text: str, min_chunk_chars: int = DEFAULT_MIN_CHUNK_CHARS
) -> list[HeadingChunk]:
    matches = list(HEADING_RE.finditer(markdown_text))

    if not matches:
        text = markdown_text.strip()
        return [HeadingChunk(heading=None, text=text)] if len(text) >= min_chunk_chars else []

    chunks: list[HeadingChunk] = []

    preamble = markdown_text[: matches[0].start()].strip()
    if len(preamble) >= min_chunk_chars:
        chunks.append(HeadingChunk(heading=None, text=preamble))

    for i, match in enumerate(matches):
        heading_text = match.group(2).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown_text)
        body = markdown_text[start:end].strip()
        if len(body) < min_chunk_chars:
            continue
        chunks.append(HeadingChunk(heading=heading_text, text=body))

    return chunks
