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

from schemebot.api.audit import AuditLog
from schemebot.api.schemas import AskRequest, AskResponse, HealthResponse
from schemebot.config import get_settings
from schemebot.generate.answer import Answer

logger = logging.getLogger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"
AUDIT_LOG_NAME = "requests.jsonl"


class AnswerService(Protocol):
    def answer(self, question: str) -> Answer: ...


class AppState:
    """Everything built at startup. The lock serialises model use on the single GPU."""

    def __init__(self, service: AnswerService, audit: AuditLog) -> None:
        self.service = service
        self.audit = audit
        self.lock = threading.Lock()


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
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        configure_logging()
        audit_dir = log_dir or get_settings().log_dir
        app.state.schemebot = AppState(build_service(), AuditLog(audit_dir / AUDIT_LOG_NAME))
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
        return AskResponse.from_answer(answer)

    return app


app = create_app()
