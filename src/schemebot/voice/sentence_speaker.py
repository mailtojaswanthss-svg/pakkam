"""Sentence-by-sentence speech synthesis pipelining with number spelling.

Pipelining architecture:
1. Decomposes answer text into clean, individual sentences.
2. Applies deterministic Indic money / number spelling via `voice/numbers.py`.
3. Synthesizes each sentence sequentially or on-demand for sub-second first-audio (TTFA).
4. Supports instant cancellation / stop control.
"""

import logging
import re
import time
from collections.abc import Iterator
from typing import Protocol

from schemebot.voice.numbers import spell_amounts
from schemebot.voice.tts import Speaker, language_code_for

logger = logging.getLogger(__name__)

# Basic sentence boundary splitter for Indic scripts and English
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?।॥])\s+")
_CITATION_MARKER = re.compile(r"\s*\[\d+\]")


def split_sentences(text: str) -> list[str]:
    """Split answer text into clean individual sentences without citation marks."""
    cleaned = _CITATION_MARKER.sub("", text).strip()
    if not cleaned:
        return []

    # Protect abbreviations and decimal points from false splitting
    protected = cleaned
    placeholders = {
        "Rs.": "Rs__DOT__",
        "ரூ.": "ரூ__DOT__",
        "रु.": "रु__DOT__",
        "No.": "No__DOT__",
        "no.": "no__DOT__",
        "Dr.": "Dr__DOT__",
        "e.g.": "eg__DOT__",
        "i.e.": "ie__DOT__",
    }
    for orig, rep in placeholders.items():
        protected = protected.replace(orig, rep)

    splits = [s.strip() for s in _SENTENCE_SPLIT_RE.split(protected) if s.strip()]
    restored = []
    for s in splits:
        for orig, rep in placeholders.items():
            s = s.replace(rep, orig)
        restored.append(s)
    return restored if restored else [cleaned]


class StopFlag(Protocol):
    def is_stopped(self) -> bool: ...


class SentenceSpeaker:
    """Pipelines synthesis across sentences for immediate first-sound playback."""

    def __init__(self, speaker: Speaker, spell_numbers: bool = True) -> None:
        self.speaker = speaker
        self.spell_numbers = spell_numbers

    def synthesize_sentence(
        self, sentence: str, language: str
    ) -> tuple[str, bytes, float]:
        """Synthesize a single sentence into audio bytes with timing.

        Returns: (spelled_sentence_text, wav_bytes, duration_ms)
        """
        lang_code = language_code_for(language)
        text_to_speak = sentence
        if self.spell_numbers:
            text_to_speak = spell_amounts(sentence, lang_code)

        start = time.perf_counter()
        audio = self.speaker.speak(text_to_speak, lang_code)
        duration_ms = (time.perf_counter() - start) * 1000.0
        return text_to_speak, audio, duration_ms

    def stream_sentences(
        self, text: str, language: str, stop_flag: StopFlag | None = None
    ) -> Iterator[tuple[int, str, bytes, float]]:
        """Yield synthesized sentences one by one for pipelined playback.

        Yields: (index, spoken_text, audio_bytes, duration_ms)
        Stops early if stop_flag has is_stopped() returning True.
        """
        sentences = split_sentences(text)
        for i, s in enumerate(sentences):
            if stop_flag is not None and getattr(stop_flag, "is_stopped", lambda: False)():
                logger.info("Speech generation halted by stop control at sentence %d", i)
                break
            spoken_text, audio, ms = self.synthesize_sentence(s, language)
            yield i, spoken_text, audio, ms
