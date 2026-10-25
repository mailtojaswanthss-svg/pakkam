"""HTTP API: `POST /ask` and `GET /health`.

Run with `uv run fastapi run` (entrypoint is set in pyproject.toml). The embedding and
reranker models load once at startup; requests then reuse them.
"""

import logging
import threading
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Protocol

from fastapi import Depends, FastAPI, Request, Response
from fastapi.responses import JSONResponse
from pydantic import TypeAdapter

from schemebot.api.audit import AuditLog
from schemebot.api.schemas import AskRequest, AskResponse, HealthResponse, SourceOut
from schemebot.config import PROJECT_ROOT, get_settings
from schemebot.generate.answer import Answer
from schemebot.ingest.models import SourceDoc

SOURCES_NAME = "sources.json"

logger = logging.getLogger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"
AUDIT_LOG_NAME = "requests.jsonl"


class AnswerService(Protocol):
    def answer(self, question: str) -> Answer: ...


class AppState:
    """Everything built at startup. The lock serialises model use on the single GPU."""

    def __init__(self, service: AnswerService, audit: AuditLog, titles: dict[str, str]) -> None:
        self.service = service
        self.audit = audit
        self.titles = titles
        self.lock = threading.Lock()


def load_sources() -> list[SourceDoc]:
    # Read through the model, not the ingest pipeline, so the API needs no PDF libraries.
    path = get_settings().data_dir / SOURCES_NAME
    return TypeAdapter(list[SourceDoc]).validate_json(path.read_bytes())


def get_state(request: Request) -> AppState:
    state: AppState = request.app.state.schemebot
    return state


StateDep = Annotated[AppState, Depends(get_state)]


def configure_logging() -> None:
    """Send the app's own INFO+ logs to stderr alongside uvicorn's; safe to call twice."""
    app_logger = logging.getLogger("schemebot")
    app_logger.setLevel(logging.INFO)
    if not app_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
        app_logger.addHandler(handler)


def _default_service() -> AnswerService:
    from schemebot.generate.factory import build_answerer

    return build_answerer(get_settings())


def create_app(
    build_service: Callable[[], AnswerService] = _default_service,
    log_dir: Path | None = None,
    web_dir: Path | None = None,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        configure_logging()
        audit_dir = log_dir or get_settings().log_dir
        titles = {d.doc_id: d.title or d.doc_id for d in load_sources()}
        app.state.schemebot = AppState(
            build_service(), AuditLog(audit_dir / AUDIT_LOG_NAME), titles
        )
        logger.info("models loaded, ready")
        yield

    app = FastAPI(
        title="Multilingual Citizen-Scheme Assistant",
        description=(
            "Answers questions about public Indian government schemes in Tamil, Hindi, "
            "English and Tanglish, citing official documents. Informational only; not an "
            "official government service."
        ),
        version="0.1.0",
        lifespan=lifespan,
    )

    @app.middleware("http")
    async def add_request_id(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request.state.request_id = uuid.uuid4().hex[:12]
        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request.state.request_id
        return response

    @app.exception_handler(Exception)
    async def internal_error(request: Request, error: Exception) -> JSONResponse:
        # Log the details server-side; never send stack traces or internals to the client.
        request_id = getattr(request.state, "request_id", "-")
        logger.exception("unhandled error (request %s)", request_id)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal error. Please try again later.", "request_id": request_id},
            headers={REQUEST_ID_HEADER: request_id},
        )

    @app.get("/health")
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    @app.post("/ask")
    def ask(body: AskRequest, state: StateDep, request: Request) -> AskResponse:
        # Plain `def`: model inference blocks, so FastAPI runs this in its threadpool.
        with state.lock:
            answer = state.service.answer(body.question)
        state.audit.record(request.state.request_id, answer)
        return AskResponse.from_answer(answer, state.titles)

    @app.get("/sources")
    def sources() -> list[SourceOut]:
        return [
            SourceOut(
                doc_id=d.doc_id,
                scheme=d.scheme,
                title=d.title or d.doc_id,
                language=d.language,
                source_url=str(d.source_url),
                doc_date=d.doc_date.isoformat() if d.doc_date else None,
            )
            for d in load_sources()
        ]

    # The chat UI (web/). Registered last: API routes above always match first.
    site = web_dir if web_dir is not None else PROJECT_ROOT / "web"
    if site.is_dir():
        app.frontend("/", directory=str(site))

    return app


app = create_app()
