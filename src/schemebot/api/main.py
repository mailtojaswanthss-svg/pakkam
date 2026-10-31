"""HTTP API: `POST /ask` and `GET /health`.

Run with `uv run fastapi run` (entrypoint is set in pyproject.toml). The embedding and
reranker models load once at startup; requests then reuse them.
"""

import json
import logging
import math
import mimetypes
import re
import time
import uuid
from collections import OrderedDict
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Any, Protocol

from fastapi import Depends, FastAPI, Form, HTTPException, Request, Response, UploadFile
from fastapi.responses import JSONResponse
from pydantic import TypeAdapter, ValidationError

from schemebot.api.audit import AuditLog
from schemebot.api.ratelimit import AskLimiter
from schemebot.api.schemas import (
    AskRequest,
    AskResponse,
    AskSourcesResponse,
    FallbackPassage,
    FeedbackRequest,
    FeedbackResponse,
    HealthResponse,
    SourceOut,
    SpeakRequest,
    TranscribeResponse,
    VoiceAskResponse,
)
from schemebot.config import PROJECT_ROOT, get_settings
from schemebot.generate.answer import Answer, FollowUp
from schemebot.ingest.models import SourceDoc
from schemebot.voice.audio import convert_to_wav16k, wav_to_opus
from schemebot.voice.numbers import phone_numbers_as_digits, spell_amounts
from schemebot.voice.stt import (
    GNANI_LANGUAGE_CODES,
    SttError,
    Transcriber,
    VoiceLanguage,
    build_transcriber,
)
from schemebot.voice.tts import Speaker, TtsError, build_speaker, language_code_for

SOURCES_NAME = "sources.json"
CITATION_MARKER = re.compile(r"\s*\[\d+\]")

# Windows' MIME table has no entry for WebP, so photos would be served as octet-stream.
mimetypes.add_type("image/webp", ".webp")

logger = logging.getLogger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"
TOO_MANY_TEXT = "Too many questions. Wait a minute and ask again."
DAILY_LIMIT_TEXT = (
    "Pakkam has answered as many questions as it can today. Please come back tomorrow."
)
AUDIT_LOG_NAME = "requests.jsonl"


class AnswerService(Protocol):
    def answer(self, question: str, voice_mode: bool = False) -> Answer: ...


SPOKEN_CACHE_SIZE = 64
"""Spoken sentences kept in memory, so replaying an answer costs no new Gnani call."""
CONFIRM_BAND = (0.30, 0.40)
"""Voice: a retrieval match in this band is uncertain, so Pakkam asks "I heard X, right?"."""


def _voice_confirmation(answer: Answer, stt_confidence: float | None = None) -> str | None:
    """'I heard <scheme>. Is that right?' when a spoken question was matched uncertainly."""
    uncertain = CONFIRM_BAND[0] <= answer.confidence <= CONFIRM_BAND[1]
    low_stt = stt_confidence is not None and stt_confidence < 0.60
    if not (uncertain or low_stt):
        return None
    scheme: str | None = None
    if answer.candidate_schemes:
        scheme = answer.candidate_schemes[0]
    elif answer.passages:
        scheme = answer.passages[0].chunk.scheme
    elif answer.citations:
        scheme = answer.citations[0].scheme
    elif answer.contact:
        scheme = answer.contact.scheme
    if not scheme:
        return None
    from schemebot.generate.messages import confirmation_text

    return confirmation_text(scheme, answer.language)


def _ask_service(
    service: "AnswerService", question: str, voice_mode: bool, follow_up: FollowUp | None
) -> Answer:
    """Pass only the options that are set, so services that take just the question work."""
    options: dict[str, Any] = {}
    if voice_mode:
        options["voice_mode"] = True
    if follow_up is not None:
        options["follow_up"] = follow_up
    return service.answer(question, **options)


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
        doc_dates: dict[str, str | None] | None = None,
    ) -> None:
        self.service = service
        self.audit = audit
        self.titles = titles
        self.doc_dates = doc_dates or {}
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
    from schemebot.generate.cache import CachedAnswerer, answer_fingerprint
    from schemebot.generate.factory import build_answerer, model_for

    settings = get_settings()
    if settings.answer_cache_size == 0:
        return build_answerer(settings)
    # Hashed before the index is opened, so the store's own lock file is not read.
    fingerprint = answer_fingerprint(
        settings, model_for(settings, "answer"), model_for(settings, "verifier")
    )
    return CachedAnswerer(
        build_answerer(settings),
        settings.answer_cache_size,
        settings.answer_cache_ttl_seconds,
        fingerprint,
    )


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
    transcribe_limiter: AskLimiter | None = None,
    sources_limiter: AskLimiter | None = None,
    speak_limiter: AskLimiter | None = None,
    feedback_limiter: AskLimiter | None = None,
) -> FastAPI:
    ask_limiter = limiter or _default_limiter()
    # Its own counter, so a voice question (/transcribe, then /ask) counts once on each.
    stt_limiter = transcribe_limiter or _default_limiter()
    # The cheap endpoints get their own, larger counters: showing sources, reading an answer
    # aloud sentence by sentence and sending feedback must not use up the question limit.
    source_limiter = sources_limiter or AskLimiter(30, 5000)
    tts_limiter = speak_limiter or AskLimiter(60, 5000)
    feedback_limit = feedback_limiter or AskLimiter(20, 5000)
    spoken: OrderedDict[tuple[str, str], bytes] = OrderedDict()
    log_dir_for_feedback = log_dir or get_settings().log_dir

    def check_limit(limiter: AskLimiter, request: Request) -> None:
        client = request.client.host if request.client else "unknown"
        wait = limiter.check(client)
        if wait is not None:
            raise HTTPException(
                status_code=429,
                detail=DAILY_LIMIT_TEXT if wait.daily else TOO_MANY_TEXT,
                headers={"Retry-After": str(math.ceil(wait.seconds))},
            )

    def limit_asks(request: Request) -> None:
        check_limit(ask_limiter, request)

    def limit_transcribe(request: Request) -> None:
        check_limit(stt_limiter, request)

    def limit_sources(request: Request) -> None:
        check_limit(source_limiter, request)

    def limit_speak(request: Request) -> None:
        check_limit(tts_limiter, request)

    def limit_feedback(request: Request) -> None:
        check_limit(feedback_limit, request)

    def heard_question(
        state: AppState, audio: UploadFile, language: VoiceLanguage
    ) -> tuple[str, str, float, float | None]:
        """Gnani STT for one clip: (question, lang code, stt ms, confidence)."""
        if state.transcriber is None:
            raise HTTPException(status_code=503, detail="Voice input is not set up on this server.")
        settings = get_settings()
        clip = audio.file.read(settings.stt_max_bytes + 1)
        if len(clip) == 0:
            raise HTTPException(status_code=422, detail="Audio file is empty.")
        if len(clip) > settings.stt_max_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"Audio file exceeds maximum size of {settings.stt_max_bytes} bytes.",
            )
        filename = audio.filename or "question.wav"
        language_code = GNANI_LANGUAGE_CODES[language]

        started = time.perf_counter()
        try:
            converted_clip = convert_to_wav16k(clip, filename, settings.stt_max_seconds)
            transcript = state.transcriber.transcribe(converted_clip, filename, language_code)
        except SttError as error:
            raise HTTPException(status_code=error.status_code, detail=error.message) from error
        stt_ms = (time.perf_counter() - started) * 1000
        stt_conf: float | None = getattr(state.transcriber, "last_confidence", None)

        try:
            question = AskRequest(question=transcript).question
        except ValidationError as error:
            raise HTTPException(
                status_code=422, detail="Pakkam could not hear a question. Try again."
            ) from error
        return question, language_code, stt_ms, stt_conf

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        configure_logging()
        audit_dir = log_dir or get_settings().log_dir
        sources_list = load_sources()
        titles = {d.doc_id: d.title or d.doc_id for d in sources_list}
        doc_dates = {d.doc_id: d.doc_date.isoformat() if d.doc_date else None for d in sources_list}
        preload_status: str = "pending"
        service = build_service()
        if hasattr(service, "preload"):
            try:
                service.preload()
                preload_status = "warmed"
            except Exception as exc:
                logger.warning("Startup model preload skipped: %s", exc)
                preload_status = "failed"
        app.state.preload_status = preload_status
        app.state.schemebot = AppState(
            service,
            AuditLog(audit_dir / AUDIT_LOG_NAME),
            titles,
            build_stt(),
            build_tts(),
            doc_dates,
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

    settings = get_settings()
    if settings.cors_origins:
        from fastapi.middleware.cors import CORSMiddleware

        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
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
    def health(state: StateDep) -> HealthResponse:
        app_settings = get_settings()
        from schemebot.generate.budget import shared_llm_budget
        from schemebot.generate.factory import model_for
        from schemebot.generate.llm import LAST_ERRORS

        budget = shared_llm_budget(
            app_settings.data_dir / "llm-calls.json",
            app_settings.max_daily_llm_calls,
            app_settings.llm_reset_time,
        )
        quota_stats = budget.stats()
        answer_model = model_for(app_settings, "answer")
        models_info = {
            "answer": answer_model,
            "embedding": app_settings.embedding_model,
            "reranker": app_settings.reranker_model,
        }
        retrieval_ok = True
        try:
            if hasattr(state.service, "_retriever"):
                retrieval_ok = state.service._retriever is not None
        except Exception:
            retrieval_ok = True

        gnani_ok = state.transcriber is not None
        preload = getattr(app.state, "preload_status", "warmed")
        is_degraded = (not retrieval_ok) or (quota_stats["remaining_today"] <= 0)
        return HealthResponse(
            status="degraded" if is_degraded else "ok",
            models=models_info,
            retrieval_ready=retrieval_ok,
            gnani_voice_ready=gnani_ok,
            preload_status=preload,
            quota=quota_stats,
            llm_errors=dict(LAST_ERRORS),
        )

    @app.post("/ask", dependencies=[Depends(limit_asks)])
    def ask(body: AskRequest, state: StateDep, request: Request) -> AskResponse:
        q = body.question.strip()
        if not q:
            raise HTTPException(status_code=422, detail="Question cannot be empty or whitespace.")
        app_settings = get_settings()
        if len(q) > app_settings.max_question_length:
            msg = f"Question exceeds maximum length of {app_settings.max_question_length} chars."
            raise HTTPException(status_code=422, detail=msg)
        follow_up = (
            FollowUp(body.follow_up.question, body.follow_up.scheme)
            if body.follow_up and (body.follow_up.question or body.follow_up.scheme)
            else None
        )
        # Plain `def`: model inference blocks, so FastAPI runs this in its threadpool.
        answer = _ask_service(state.service, body.question, body.voice_mode, follow_up)
        state.audit.record(request.state.request_id, answer)
        response = AskResponse.from_answer(answer, state.titles, state.doc_dates)
        if body.voice_mode:
            response.confirmation_text = _voice_confirmation(answer)
            response.needs_confirmation = response.confirmation_text is not None
        return response

    @app.post("/ask/sources", dependencies=[Depends(limit_sources)])
    def ask_sources(body: AskRequest, state: StateDep) -> AskSourcesResponse:
        """The pages a question matches, in well under a second and with no LLM call, shown
        while the answer is written. Searches exactly what /ask will search (cleaned query,
        aliases, follow-up scheme), and /ask then reuses this result instead of searching
        again."""
        started = time.perf_counter()
        follow_up = (
            FollowUp(body.follow_up.question, body.follow_up.scheme) if body.follow_up else None
        )
        sources = getattr(state.service, "sources", None)
        if sources is not None:
            retrieval = sources(body.question, follow_up)
        else:
            retriever = getattr(state.service, "retriever", None)
            if retriever is None or not hasattr(retriever, "retrieve"):
                raise HTTPException(status_code=503, detail="Retriever not available")
            retrieval = retriever.retrieve(body.question)
        total_ms = (time.perf_counter() - started) * 1000
        timings = {"retrieval": round(total_ms, 1), "total": round(total_ms, 1)}
        passages = [
            FallbackPassage(
                scheme=p.chunk.scheme,
                doc_id=p.chunk.doc_id,
                document=state.titles.get(p.chunk.doc_id, p.chunk.doc_id),
                page=p.chunk.page_start,
                text=p.chunk.text,
                source_url=str(p.chunk.source_url),
            )
            for p in retrieval.passages[:3]
        ]
        return AskSourcesResponse(passages=passages, timings_ms=timings)

    @app.post("/ask/voice", dependencies=[Depends(limit_asks)])
    def ask_voice(
        audio: UploadFile,
        state: StateDep,
        request: Request,
        language: Annotated[VoiceLanguage, Form()] = "ta",
    ) -> VoiceAskResponse:
        """Spoken question: Gnani speech to text, then the same pipeline as `/ask`.

        The chat page uses `/transcribe` and then `/ask` instead, to show the transcript
        before the answer is ready. This one-call route stays for scripts and the API."""
        question, language_code, stt_ms, stt_conf = heard_question(state, audio, language)
        answer = state.service.answer(question, voice_mode=True)
        state.audit.record(request.state.request_id, answer, {"stt": stt_ms})
        response = AskResponse.from_answer(answer, state.titles, state.doc_dates)
        response.timings_ms["stt"] = round(stt_ms, 1)

        # Uncertain match (retrieval in the confirm band, or low speech-to-text confidence):
        # ask "I heard X, is that right?" before people act on the answer.
        confirm_text = _voice_confirmation(answer, stt_conf)
        response.needs_confirmation = confirm_text is not None

        return VoiceAskResponse(
            **response.model_dump(exclude={"confirmation_text"}),
            transcript=question,
            stt_language_code=language_code,
            stt_ms=round(stt_ms, 1),
            stt_confidence=stt_conf,
            confirmation_text=confirm_text,
        )

    @app.post("/feedback", dependencies=[Depends(limit_feedback)])
    def feedback(body: FeedbackRequest, state: StateDep) -> FeedbackResponse:
        """Citizen feedback loop: records ratings, status, language, timings.
        Text only saved if opted in.
        """
        log_dir = log_dir_for_feedback
        log_dir.mkdir(parents=True, exist_ok=True)
        fb_path = log_dir / "feedback.jsonl"
        entry: dict[str, object] = {
            "timestamp": time.time(),
            "status": body.status,
            "language": body.language,
            "thumbs": body.thumbs,
            "timings_ms": body.timings_ms,
            "include_text": body.include_text,
        }
        if body.include_text:
            if body.question is not None:
                entry["question"] = body.question
            if body.reason is not None:
                entry["reason"] = body.reason
        with open(fb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return FeedbackResponse()

    @app.post("/transcribe", dependencies=[Depends(limit_transcribe)])
    def transcribe(
        audio: UploadFile,
        state: StateDep,
        request: Request,
        language: Annotated[VoiceLanguage, Form()] = "ta",
    ) -> TranscribeResponse:
        """Speech to text only (1 Gnani call), so the page can show what it heard at once
        and then send that text to `/ask`."""
        question, language_code, stt_ms, _ = heard_question(state, audio, language)
        state.audit.record_transcript(request.state.request_id, language_code, stt_ms)
        return TranscribeResponse(
            transcript=question, stt_language_code=language_code, stt_ms=round(stt_ms, 1)
        )

    @app.post("/speak", dependencies=[Depends(limit_speak)])
    def speak(body: SpeakRequest, state: StateDep, request: Request) -> Response:
        """An answer read aloud by Gnani Timbre, as WAV. Only numbers are logged, never the
        text or the audio."""
        if state.speaker is None:
            raise HTTPException(status_code=503, detail="Spoken answers are not set up.")
        text = CITATION_MARKER.sub("", body.text).strip()
        if not text:
            raise HTTPException(status_code=422, detail="There is nothing to read aloud.")
        settings = get_settings()
        if len(text) > settings.tts_max_chars:
            raise HTTPException(status_code=413, detail="This answer is too long to read aloud.")
        language_code = language_code_for(body.language)
        text = phone_numbers_as_digits(text)
        if settings.tts_spell_amounts:
            text = spell_amounts(text, language_code)
        started = time.perf_counter()
        key = (language_code, text)
        audio = spoken.get(key)
        if audio is not None:
            spoken.move_to_end(key)
        else:
            try:
                audio = state.speaker.speak(text, language_code)
            except TtsError as error:
                raise HTTPException(status_code=error.status_code, detail=error.message) from error
            spoken[key] = audio
            while len(spoken) > SPOKEN_CACHE_SIZE:
                spoken.popitem(last=False)
        tts_ms = (time.perf_counter() - started) * 1000
        state.audit.record_speech(request.state.request_id, len(text), language_code, tts_ms)
        # Server-Timing is the standard header for this; browsers show it in dev tools.
        headers = {"Cache-Control": "no-store", "Server-Timing": f"tts;dur={tts_ms:.1f}"}
        # Pages that can play Ogg/Opus ask for it: about 10x smaller than WAV on a slow phone.
        if "audio/ogg" in request.headers.get("accept", ""):
            opus = wav_to_opus(audio)
            if opus is not None:
                return Response(content=opus, media_type="audio/ogg", headers=headers)
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
