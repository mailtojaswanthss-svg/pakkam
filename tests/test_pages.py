from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from schemebot.api.main import create_app
from schemebot.api.pages import PageUnavailable, _pieces, render_page

pymupdf = pytest.importorskip("pymupdf")


@pytest.fixture
def pdf(tmp_path: Path) -> Path:
    path = tmp_path / "order.pdf"
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 100), "Families with annual income below Rs.2.5 lakh are eligible.")
    page.insert_text((72, 130), "The entitlement is Rs.1,000 per month to the woman head.")
    doc.save(path)
    doc.close()
    return path


def test_renders_the_page_as_png_and_marks_the_passage(pdf: Path) -> None:
    plain = render_page(pdf, 1)
    marked = render_page(pdf, 1, "Families with annual income below Rs.2.5 lakh are eligible.")

    assert plain.startswith(b"\x89PNG")
    assert marked.startswith(b"\x89PNG") and marked != plain  # the highlight changes pixels


def test_out_of_range_page_or_missing_file_is_unavailable(pdf: Path) -> None:
    with pytest.raises(PageUnavailable):
        render_page(pdf, 2)
    with pytest.raises(PageUnavailable):
        render_page(pdf.with_name("missing.pdf"), 1)


def test_search_pieces_skip_fragments_and_shorten_long_clauses() -> None:
    pieces = _pieces("i) Rs.2.5 lakh. ok. " + "word " * 30)
    assert "ok." not in pieces
    assert all(len(p) <= 60 for p in pieces)


class NoService:
    def answer(self, question: str, voice_mode: bool = False) -> object:
        raise AssertionError("not used")


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    with TestClient(create_app(lambda: NoService(), log_dir=tmp_path)) as test_client:
        yield test_client


def test_only_documents_in_sources_json_can_be_requested(client: TestClient) -> None:
    assert client.get("/page", params={"doc": "../../etc/passwd", "p": 1}).status_code == 404


def test_a_known_document_without_its_pdf_on_disk_is_404(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("SCHEMEBOT_DATA_DIR", str(tmp_path))
    response = client.get("/page", params={"doc": "apy-brochure-en", "p": 1})
    assert response.status_code == 404
