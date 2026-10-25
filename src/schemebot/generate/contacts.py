"""Official contact points per scheme, shown when the assistant cannot answer.

Helpline numbers are only listed when an official source document states them (with the
page recorded in `helpline_source`), following the project rule that every number comes
from a source. Websites are the schemes' official portals from docs/data_sources.md.
"""

from pathlib import Path

from pydantic import BaseModel, ConfigDict, HttpUrl, TypeAdapter, model_validator

CONTACTS_NAME = "contacts.json"


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
