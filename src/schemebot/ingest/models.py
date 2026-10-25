"""Records shared by ingestion and the later index / retrieve / eval stages."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from schemebot.ingest.langid import Language

DOC_ID_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"


class SourceDoc(BaseModel):
    """One entry in data/sources.json: a public document saved in data/raw/."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    doc_id: str = Field(pattern=DOC_ID_PATTERN, examples=["kmut-guidelines-ta"])
    scheme: str
    file: str = Field(description="File name inside data/raw/")
    source_url: HttpUrl
    language: Language = Field(description="Main language of the document")
    doc_date: date | None = Field(default=None, description="Date printed on the document")
    accessed: date
    force_ocr: bool = Field(default=False, description="Set for known legacy-font PDFs")


class Chunk(BaseModel):
    """A retrievable passage. `doc_id` + `page_start` is what answers cite."""

    model_config = ConfigDict(frozen=True)

    chunk_id: str
    doc_id: str
    scheme: str
    source_url: HttpUrl
    page_start: int = Field(ge=1)
    page_end: int = Field(ge=1)
    section: str | None
    language: Language
    doc_date: date | None
    text: str
    extraction: str = Field(description="text, ocr, or text-unverified")
