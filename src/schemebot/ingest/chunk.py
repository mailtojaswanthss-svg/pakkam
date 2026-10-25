"""Section-aware chunking.

Scheme documents are organised under headings such as Eligibility, Documents required and
How to apply. Keeping chunks inside one section means a retrieved passage answers one kind
of question, and the section name becomes useful metadata for citations and filtering.
"""

import re
from collections.abc import Iterator
from dataclasses import dataclass

from schemebot.ingest.extract import PageText
from schemebot.ingest.langid import detect_language
from schemebot.ingest.models import Chunk, SourceDoc

MAX_CHUNK_CHARS = 1000
"""Characters, not tokens. Tamil needs roughly 2-3 characters per token in the bge-m3
tokenizer, so 1000 characters stays inside the reranker's 512-token window with a query."""

OVERLAP_MAX_CHARS = 250
"""The last paragraph of a chunk is repeated in the next one if it is at most this long."""

MAX_HEADING_CHARS = 80
MAX_KEYWORD_ANYWHERE_WORDS = 4
SENTENCE_ENDINGS = (".", "।", ":", "?", "!", ";")
MIN_CAPS_HEADING_DISTINCT_LETTERS = 4
MIN_CAPS_HEADING_LETTER_SHARE = 0.8

# Lower-case heading keywords in the three document languages.
# fmt: off
HEADING_KEYWORDS = (
    # English
    "eligibility", "who can apply", "documents required", "required documents",
    "how to apply", "application procedure", "procedure for applying", "benefits",
    "objective", "objectives", "scheme details", "selection", "contact", "helpline",
    "frequently asked questions", "exclusion", "assistance",
    # Tamil
    "தகுதி", "ஆவணங்கள்", "விண்ணப்பிக்கும் முறை", "விண்ணப்பிப்பது எப்படி", "பயன்கள்",
    "நோக்கம்", "தொடர்பு", "உதவி மையம்", "தேர்வு முறை",
    # Hindi
    "पात्रता", "दस्तावेज़", "दस्तावेज", "आवेदन कैसे करें", "आवेदन प्रक्रिया", "लाभ",
    "उद्देश्य", "संपर्क", "हेल्पलाइन",
)
# fmt: on

_PAGE_FURNITURE = re.compile(r"^(page\s*)?[-–]?\s*\d+\s*(of\s*\d+)?\s*[-–]?$", re.IGNORECASE)
_SENTENCE_END = re.compile(r"(?<=[.?!।])\s+")
_NUMBERING = re.compile(r"^(\d+(\.\d+)*|[ivx]+|[a-z])[.)]\s*", re.IGNORECASE)


@dataclass
class _Block:
    """A paragraph with the page it came from and the section it belongs to."""

    text: str
    page: int
    section: str | None
    extraction: str


def is_heading(line: str) -> bool:
    if not line or len(line) > MAX_HEADING_CHARS or line.endswith((".", "।", ",")):
        return False
    if "|" in line:  # an OCR'd table row, not a heading
        return False
    bare = _NUMBERING.sub("", line).rstrip(":").strip().lower()
    if any(bare.startswith(keyword) for keyword in HEADING_KEYWORDS):
        return True
    # Tamil and Hindi often put the modifier first ("தேவையான ஆவணங்கள்", required documents),
    # so very short lines may contain the keyword anywhere.
    if len(bare.split()) <= MAX_KEYWORD_ANYWHERE_WORDS and any(
        keyword in bare for keyword in HEADING_KEYWORDS
    ):
        return True
    # ALL-CAPS English lines such as "SCHEME GUIDELINES" are headings too, but OCR of
    # diagrams produces caps noise like "DDDDDDD" or "BDO/ MC/", so require word-like text.
    visible = [char for char in line if not char.isspace()]
    letters = [char for char in visible if char.isalpha()]
    return (
        line.isupper()
        and len(set(letters)) >= MIN_CAPS_HEADING_DISTINCT_LETTERS
        and len(letters) / len(visible) >= MIN_CAPS_HEADING_LETTER_SHARE
    )


def _blocks(pages: list[PageText]) -> Iterator[_Block]:
    section: str | None = None
    for page in pages:
        paragraph: list[str] = []
        # The trailing "" closes the last paragraph on the page.
        for raw_line in [*page.text.splitlines(), ""]:
            line = raw_line.strip()
            if _PAGE_FURNITURE.match(line):
                continue
            # A heading starts a paragraph. A line continuing an unfinished sentence is a
            # wrapped fragment, however much it looks like a heading on its own.
            starts_paragraph = not paragraph or paragraph[-1].endswith(SENTENCE_ENDINGS)
            heading = starts_paragraph and is_heading(line)
            if (not line or heading) and paragraph:
                yield _Block(" ".join(paragraph), page.page, section, page.method)
                paragraph = []
            if heading:
                section = _NUMBERING.sub("", line).rstrip(":").strip()
            elif line:
                paragraph.append(line)


def _split_long(text: str, limit: int) -> list[str]:
    """Split an oversize paragraph at sentence ends, then hard-split any remaining giants."""
    pieces: list[str] = []
    current = ""
    for sentence in _SENTENCE_END.split(text):
        candidate = f"{current} {sentence}".strip()
        if len(candidate) <= limit:
            current = candidate
            continue
        if current:
            pieces.append(current)
        while len(sentence) > limit:
            pieces.append(sentence[:limit])
            sentence = sentence[limit:]
        current = sentence
    if current:
        pieces.append(current)
    return pieces


def _sized_blocks(blocks: Iterator[_Block], limit: int) -> Iterator[_Block]:
    for block in blocks:
        if len(block.text) <= limit:
            yield block
            continue
        for piece in _split_long(block.text, limit):
            yield _Block(piece, block.page, block.section, block.extraction)


def _make_chunk(doc: SourceDoc, blocks: list[_Block], index: int) -> Chunk:
    text = "\n\n".join(block.text for block in blocks)
    language = detect_language(text)
    extractions = {block.extraction for block in blocks}
    worst = next((method for method in ("text-unverified", "ocr") if method in extractions), "text")
    return Chunk(
        chunk_id=f"{doc.doc_id}-p{blocks[0].page}-{index:03d}",
        doc_id=doc.doc_id,
        scheme=doc.scheme,
        source_url=doc.source_url,
        page_start=blocks[0].page,
        page_end=blocks[-1].page,
        section=blocks[0].section,
        language=doc.language if language == "unknown" else language,
        doc_date=doc.doc_date,
        text=text,
        extraction=worst,
    )


def chunk_document(
    doc: SourceDoc, pages: list[PageText], max_chars: int = MAX_CHUNK_CHARS
) -> list[Chunk]:
    """Group paragraphs into chunks of at most `max_chars`, never crossing a section."""
    chunks: list[Chunk] = []
    current: list[_Block] = []

    def size(blocks: list[_Block]) -> int:
        return sum(len(block.text) for block in blocks) + 2 * max(len(blocks) - 1, 0)

    for block in _sized_blocks(_blocks(pages), max_chars):
        same_section = bool(current) and current[0].section == block.section
        if current and same_section and size([*current, block]) <= max_chars:
            current.append(block)
            continue

        if current:
            chunks.append(_make_chunk(doc, current, len(chunks)))
        tail = current[-1] if current else None
        carry_overlap = (
            same_section
            and tail is not None
            and len(tail.text) <= OVERLAP_MAX_CHARS
            and size([tail, block]) <= max_chars
        )
        current = [tail, block] if carry_overlap and tail else [block]

    if current:
        chunks.append(_make_chunk(doc, current, len(chunks)))
    return chunks
