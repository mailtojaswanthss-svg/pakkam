"""Scheme alias resolver, transliteration mapper, and speech slip corrector.

Loads data/scheme_aliases.json and maps user slang, colloquialisms, and STT slips
to canonical scheme names to boost retrieval recall.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from pydantic import BaseModel, ConfigDict


class SchemeAlias(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    canonical: str
    aliases: list[str]
    transliterations: list[str]
    stt_slips: list[str]

    @property
    def all_forms(self) -> list[str]:
        return [self.canonical] + self.aliases + self.transliterations + self.stt_slips


@dataclass
class AliasMatchResult:
    canonical: str
    matched_term: str
    match_type: str  # "exact", "alias", "transliteration", "stt_slip"


class AliasMatcher:
    def __init__(self, alias_groups: list[SchemeAlias]) -> None:
        self.groups = alias_groups

    @classmethod
    def load(cls, path: Path) -> Self:
        if not path.is_file():
            return cls([])
        data = json.loads(path.read_text(encoding="utf-8"))
        groups = [SchemeAlias.model_validate(item) for item in data]
        return cls(groups)

    def match(self, query: str) -> AliasMatchResult | None:
        """Find the strongest scheme match in query by inspecting all known variants."""
        q_lower = query.lower().strip()

        # Check in order: exact canonical, aliases, transliterations, slips
        for group in self.groups:
            if group.canonical.lower() in q_lower:
                return AliasMatchResult(
                    canonical=group.canonical,
                    matched_term=group.canonical,
                    match_type="exact",
                )

        for group in self.groups:
            for alias in group.aliases:
                pattern = rf"(?i)\b{re.escape(alias.lower())}\b"
                if re.search(pattern, q_lower) or alias.lower() in q_lower:
                    return AliasMatchResult(
                        canonical=group.canonical,
                        matched_term=alias,
                        match_type="alias",
                    )

        for group in self.groups:
            for trans in group.transliterations:
                pattern = rf"(?i)\b{re.escape(trans.lower())}\b"
                if re.search(pattern, q_lower) or trans.lower() in q_lower:
                    return AliasMatchResult(
                        canonical=group.canonical,
                        matched_term=trans,
                        match_type="transliteration",
                    )

        for group in self.groups:
            for slip in group.stt_slips:
                pattern = rf"(?i)\b{re.escape(slip.lower())}\b"
                if re.search(pattern, q_lower) or slip.lower() in q_lower:
                    return AliasMatchResult(
                        canonical=group.canonical,
                        matched_term=slip,
                        match_type="stt_slip",
                    )

        return None

    def suggest_candidates(self, query: str, top_k: int = 2) -> list[str]:
        """Suggest up to top_k candidate schemes when query is ambiguous or near-threshold."""
        q_lower = query.lower().strip()
        candidates: list[tuple[str, int]] = []

        tokens = set(re.findall(r"\w+", q_lower))
        for group in self.groups:
            score = 0
            for form in group.all_forms:
                form_tokens = set(re.findall(r"\w+", form.lower()))
                overlap = len(tokens & form_tokens)
                if overlap > score:
                    score = overlap
            if score > 0:
                candidates.append((group.canonical, score))

        candidates.sort(key=lambda x: x[1], reverse=True)
        return [c[0] for c in candidates[:top_k]]

    def expand_query(self, query: str) -> str:
        """If an alias or slip is detected, append canonical scheme to strengthen retrieval."""
        match_res = self.match(query)
        if match_res and match_res.canonical.lower() not in query.lower():
            return f"{query} {match_res.canonical}"
        return query
