"""HTTP API: `POST /ask` and `GET /health`.

Run with `uv run fastapi run` (entrypoint is set in pyproject.toml). The embedding and
reranker models load once at startup; requests then reuse them.
"""

import logging
import math
import mimetypes
import re
import time
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Protocol

from fastapi import Depends, FastAPI, Form, HTTPException, Request, Response, UploadFile
from fastapi.responses import JSONResponse
from pydantic import TypeAdapter, ValidationError

from schemebot.api.audit import AuditLog
from schemebot.api.ratelimit import AskLimiter
from schemebot.api.schemas import (
    AskRequest,
    AskResponse,
    HealthResponse,
    SourceOut,
    SpeakRequest,
    VoiceAskResponse,
)
from schemebot.config import PROJECT_ROOT, get_settings
from schemebot.generate.answer import Answer
from schemebot.ingest.models import SourceDoc
from schemebot.voice.stt import (
    GNANI_LANGUAGE_CODES,
    SttError,
    Transcriber,
    VoiceLanguage,
    build_transcriber,
    check_audio,
)
from schemebot.voice.tts import Speaker, TtsError, build_speaker, language_code_for

SOURCES_NAME = "sources.json"
CITATION_MARKER = re.compile(r"\s*\[\d+\]")

# Windows' MIME table has no entry for WebP, so photos would be served as octet-stream.
mimetypes.add_type("image/webp", ".webp")

logger = logging.getLogger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"
AUDIT_LOG_NAME = "requests.jsonl"


class AnswerService(Protocol):
    def answer(self, question: str) -> Answer: ...


class AppState:
    """Everything built at startup.

    No lock here: the retriever makes requests take turns on the GPU itself, and the LLM
    calls (most of the time per answer) can then run for several users at once."""

    def __init__(
        self,
        service: AnswerService,
        audit: AuditLog,
        titles: dict[str, str],
        transcriber: Transcriber | None = None,
        speaker: Speaker | None = None,
    ) -> None:
        self.service = service
        self.audit = audit
        self.titles = titles
        self.transcriber = transcriber
        self.speaker = speaker


def load_sources() -> list[SourceDoc]:
    # Read through the model, not the ingest pipeline, so the API needs no PDF libraries.
    path = get_settings().data_dir / SOURCES_NAME
    return TypeAdapter(list[SourceDoc]).validate_json(path.read_bytes())


def get_state(request: Request) -> AppState:
    state: AppState = request.app.state.schemebot
    return state


StateDep = Annotated[AppState, Depends(get_state)]


def _default_limiter() -> AskLimiter:
    settings = get_settings()
    return AskLimiter(settings.ask_limit_per_client_per_minute, settings.ask_limit_total_per_day)


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


def _default_transcriber() -> Transcriber | None:
    return build_transcriber(get_settings())


def _default_speaker() -> Speaker | None:
    return build_speaker(get_settings())


def create_app(
    build_service: Callable[[], AnswerService] = _default_service,
    build_stt: Callable[[], Transcriber | None] = _default_transcriber,
    build_tts: Callable[[], Speaker | None] = _default_speaker,
    log_dir: Path | None = None,
    web_dir: Path | None = None,
    limiter: AskLimiter | None = None,
) -> FastAPI:
    ask_limiter = limiter or _default_limiter()

    def limit_asks(request: Request) -> None:
        client = request.client.host if request.client else "unknown"
        wait = ask_limiter.check(client)
        if wait is not None:
            raise HTTPException(
                status_code=429,
                detail="Too many questions. Wait a little and ask again.",
                headers={"Retry-After": str(math.ceil(wait))},
            )

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        configure_logging()
        audit_dir = log_dir or get_settings().log_dir
        titles = {d.doc_id: d.title or d.doc_id for d in load_sources()}
        app.state.schemebot = AppState(
            build_service(),
            AuditLog(audit_dir / AUDIT_LOG_NAME),
            titles,
            build_stt(),
            build_tts(),
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

    @app.post("/ask", dependencies=[Depends(limit_asks)])
    def ask(body: AskRequest, state: StateDep, request: Request) -> AskResponse:
        # Plain `def`: model inference blocks, so FastAPI runs this in its threadpool.
        answer = state.service.answer(body.question)
        state.audit.record(request.state.request_id, answer)
        return AskResponse.from_answer(answer, state.titles)

    @app.post("/ask/voice", dependencies=[Depends(limit_asks)])
    def ask_voice(
        audio: UploadFile,
        state: StateDep,
        request: Request,
        language: Annotated[VoiceLanguage, Form()] = "ta",
    ) -> VoiceAskResponse:
        """Spoken question: Gnani speech to text, then the same pipeline as `/ask`."""
        if state.transcriber is None:
            raise HTTPException(status_code=503, detail="Voice input is not set up on this server.")
        settings = get_settings()
        clip = audio.file.read(settings.stt_max_bytes + 1)
        filename = audio.filename or "question.wav"
        language_code = GNANI_LANGUAGE_CODES[language]

        started = time.perf_counter()
        try:
            check_audio(clip, filename, settings.stt_max_bytes, settings.stt_max_seconds)
            transcript = state.transcriber.transcribe(clip, filename, language_code)
        except SttError as error:
            raise HTTPException(status_code=error.status_code, detail=error.message) from error
        stt_ms = (time.perf_counter() - started) * 1000

        try:
            question = AskRequest(question=transcript).question
        except ValidationError as error:
            raise HTTPException(
                status_code=422, detail="Pakkam could not hear a question. Try again."
            ) from error

        answer = state.service.answer(question)
        state.audit.record(request.state.request_id, answer, {"stt": stt_ms})
        response = AskResponse.from_answer(answer, state.titles)
        response.timings_ms["stt"] = round(stt_ms, 1)
        return VoiceAskResponse(
            **response.model_dump(),
            transcript=question,
            stt_language_code=language_code,
            stt_ms=round(stt_ms, 1),
        )

    @app.post("/speak", dependencies=[Depends(limit_asks)])
    def speak(body: SpeakRequest, state: StateDep, request: Request) -> Response:
        """An answer read aloud by Gnani Timbre, as WAV. Only numbers are logged, never the
        text or the audio."""
        if state.speaker is None:
            raise HTTPException(status_code=503, detail="Spoken answers are not set up.")
        text = CITATION_MARKER.sub("", body.text).strip()
        if not text:
            raise HTTPException(status_code=422, detail="There is nothing to read aloud.")
        if len(text) > get_settings().tts_max_chars:
            raise HTTPException(status_code=413, detail="This answer is too long to read aloud.")
        language_code = language_code_for(body.language)
        started = time.perf_counter()
        try:
            audio = state.speaker.speak(text, language_code)
        except TtsError as error:
            raise HTTPException(status_code=error.status_code, detail=error.message) from error
        tts_ms = (time.perf_counter() - started) * 1000
        state.audit.record_speech(request.state.request_id, len(text), language_code, tts_ms)
        # Server-Timing is the standard header for this; browsers show it in dev tools.
        headers = {"Cache-Control": "no-store", "Server-Timing": f"tts;dur={tts_ms:.1f}"}
        return Response(content=audio, media_type="audio/wav", headers=headers)

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
