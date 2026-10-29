"""Official contact points per scheme, shown when the assistant cannot answer.

Helpline numbers are only listed when an official source document states them (with the
page recorded in `helpline_source`), following the project rule that every number comes
from a source. Websites are the schemes' official portals from docs/data_sources.md.
"""

import csv
from pathlib import Path

from pydantic import BaseModel, ConfigDict, HttpUrl, TypeAdapter, model_validator

CONTACTS_NAME = "contacts.json"


def verify_helplines(csv_path: Path) -> list[str]:
    """Verify that every non-null helpline in the check sheet has a source and verifier."""
    errors: list[str] = []
    if not csv_path.exists():
        return [f"Helpline verification sheet not found at {csv_path}"]

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=2):
            scheme = (row.get("scheme") or "").strip()
            helpline = (row.get("helpline") or "").strip()
            source_url = (row.get("source_url") or "").strip()
            verified_by = (row.get("verified_by") or "").strip()

            if helpline:
                if not source_url:
                    errors.append(f"Row {idx} ({scheme}): helpline '{helpline}' lacks source_url.")
                if not verified_by:
                    errors.append(
                        f"Row {idx} ({scheme}): helpline '{helpline}' lacks human verified_by."
                    )
    return errors


class Contact(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    scheme: str
    helpline: str | None
    helpline_source: str | None
    website: HttpUrl

    @model_validator(mode="after")
    def _helpline_needs_source(self) -> "Contact":
        if self.helpline and not self.helpline_source:
            raise ValueError(f"helpline for {self.scheme} has no source document")
        return self


def load_contacts(path: Path) -> dict[str, Contact]:
    """Scheme name -> contact. A missing file means no contacts, not an error."""
    if not path.is_file():
        return {}
    contacts = TypeAdapter(list[Contact]).validate_json(path.read_bytes())
    return {contact.scheme: contact for contact in contacts}
