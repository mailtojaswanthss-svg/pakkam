"""Unit tests for Claude, Gemini, and Failover LLM provider backends.

All tests use mocked client responses to verify failure-case handling:
- 429 rate limits
- Connection timeouts
- Empty / non-JSON output
- Provider failover policies
Zero real network or LLM API calls are made.
"""

from types import SimpleNamespace
from typing import Any

import httpx
import pytest

from schemebot.config import Settings
from schemebot.generate.factory import build_llm
from schemebot.generate.gemini import GeminiJsonLlm
from schemebot.generate.llm import (
    ClaudeJsonLlm,
    FailoverJsonLlm,
    LlmDeclinedError,
    LlmUnavailableError,
)

SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "answerable": {"type": "boolean"},
        "sentences": {"type": "array", "items": {"type": "string"}},
    },
}


class MockClaudeClient:
    def __init__(self, response_or_exc: Any) -> None:
        self._response_or_exc = response_or_exc
        self.calls: list[dict[str, Any]] = []
        self.api_key = "test-anthropic-key"
        self.auth_token = None
        self.credentials = None
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self._create))

    def _create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        if isinstance(self._response_or_exc, Exception):
            raise self._response_or_exc
        return self._response_or_exc


# --- Claude Provider Tests ---


def test_claude_success() -> None:
    valid_text = '{"answerable": true, "sentences": ["Valid response."]}'
    resp = SimpleNamespace(
        content=[SimpleNamespace(type="text", text=valid_text)],
        stop_reason="end_turn",
    )
    llm = ClaudeJsonLlm("claude-opus-5-5", api_key="test-key", effort="low")
    llm._client = MockClaudeClient(resp)  # type: ignore[assignment]

    result = llm.complete_json("system", "user", SCHEMA)
    assert result == {"answerable": True, "sentences": ["Valid response."]}


def test_claude_429_rate_limit() -> None:
    import anthropic

    request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    response = httpx.Response(429, request=request)
    rate_limit_err = anthropic.RateLimitError(
        message="Rate limit exceeded", response=response, body={"error": "rate_limit"}
    )

    llm = ClaudeJsonLlm("claude-opus-5-5", api_key="test-key", effort="low")
    llm._client = MockClaudeClient(rate_limit_err)  # type: ignore[assignment]

    with pytest.raises(LlmUnavailableError, match="rate limit"):
        llm.complete_json("system", "user", SCHEMA)


def test_claude_timeout_and_connection_error() -> None:
    import anthropic

    request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    timeout_err = anthropic.APITimeoutError(request=request)

    llm = ClaudeJsonLlm("claude-opus-5-5", api_key="test-key", effort="low")
    llm._client = MockClaudeClient(timeout_err)  # type: ignore[assignment]

    with pytest.raises(LlmUnavailableError, match="could not reach"):
        llm.complete_json("system", "user", SCHEMA)


@pytest.mark.parametrize(
    "empty_resp",
    [
        SimpleNamespace(content=[], stop_reason="end_turn"),
        SimpleNamespace(content=[SimpleNamespace(type="image")], stop_reason="end_turn"),
        SimpleNamespace(content=[SimpleNamespace(type="text", text="")], stop_reason="end_turn"),
        SimpleNamespace(
            content=[SimpleNamespace(type="text", text="not a json string")],
            stop_reason="end_turn",
        ),
    ],
)
def test_claude_empty_or_invalid_output(empty_resp: Any) -> None:
    llm = ClaudeJsonLlm("claude-opus-5-5", api_key="test-key", effort="low")
    llm._client = MockClaudeClient(empty_resp)  # type: ignore[assignment]

    with pytest.raises(LlmUnavailableError):
        llm.complete_json("system", "user", SCHEMA)


# --- Gemini Provider Tests ---


class MockGeminiModels:
    def __init__(self, response_or_exc: Any) -> None:
        self._response_or_exc = response_or_exc
        self.calls: list[dict[str, Any]] = []

    def generate_content(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        if isinstance(self._response_or_exc, Exception):
            raise self._response_or_exc
        return self._response_or_exc


def test_gemini_success() -> None:
    resp = SimpleNamespace(
        prompt_feedback=None,
        candidates=[SimpleNamespace(finish_reason="STOP")],
        text='{"answerable": true, "sentences": ["Gemini response."]}',
    )
    llm = GeminiJsonLlm("gemini-3.8-flash", api_key="test-key", effort="low")
    llm._client = SimpleNamespace(models=MockGeminiModels(resp))

    result = llm.complete_json("system", "user", SCHEMA)
    assert result == {"answerable": True, "sentences": ["Gemini response."]}


def test_gemini_429_rate_limit() -> None:
    from google.genai import errors

    quota_err = errors.ClientError(
        429,
        {"error": {"code": 429, "message": "Resource exhausted", "status": "RESOURCE_EXHAUSTED"}},
    )
    llm = GeminiJsonLlm("gemini-3.8-flash", api_key="test-key", effort="low")
    llm._client = SimpleNamespace(models=MockGeminiModels(quota_err))

    with pytest.raises(LlmUnavailableError, match="429"):
        llm.complete_json("system", "user", SCHEMA)


def test_gemini_timeout_and_connection_error() -> None:
    request = httpx.Request("POST", "https://generativelanguage.googleapis.com/")
    timeout_err = httpx.TimeoutException("Read timed out", request=request)

    llm = GeminiJsonLlm("gemini-3.8-flash", api_key="test-key", effort="low")
    llm._client = SimpleNamespace(models=MockGeminiModels(timeout_err))

    with pytest.raises(LlmUnavailableError, match="could not reach"):
        llm.complete_json("system", "user", SCHEMA)


@pytest.mark.parametrize(
    "empty_resp",
    [
        SimpleNamespace(prompt_feedback=None, candidates=[], text=None),
        SimpleNamespace(
            prompt_feedback=None,
            candidates=[SimpleNamespace(finish_reason="STOP")],
            text="",
        ),
        SimpleNamespace(
            prompt_feedback=None,
            candidates=[SimpleNamespace(finish_reason="STOP")],
            text="invalid json",
        ),
    ],
)
def test_gemini_empty_or_invalid_output(empty_resp: Any) -> None:
    llm = GeminiJsonLlm("gemini-3.8-flash", api_key="test-key", effort="low")
    llm._client = SimpleNamespace(models=MockGeminiModels(empty_resp))

    with pytest.raises(LlmUnavailableError):
        llm.complete_json("system", "user", SCHEMA)


# --- Failover Provider Tests ---


class FakeStubLlm:
    def __init__(
        self,
        name: str,
        result: dict[str, Any] | Exception,
        is_configured: bool = True,
    ) -> None:
        self.name = name
        self._result = result
        self._is_configured = is_configured
        self.call_count = 0

    @property
    def configured(self) -> bool:
        return self._is_configured

    def complete_json(self, system: str, user: str, schema: dict[str, object]) -> dict[str, Any]:
        self.call_count += 1
        if isinstance(self._result, Exception):
            raise self._result
        return self._result


def test_failover_triggers_on_unavailable_when_enabled() -> None:
    primary = FakeStubLlm("gemini", LlmUnavailableError("Gemini API returned 429"))
    secondary = FakeStubLlm("claude", {"answerable": True, "sentences": ["Fallback answer"]})

    failover = FailoverJsonLlm(primary, secondary, fallback_enabled=True)  # type: ignore[arg-type]
    result = failover.complete_json("system", "user", SCHEMA)

    assert result == {"answerable": True, "sentences": ["Fallback answer"]}
    assert primary.call_count == 1
    assert secondary.call_count == 1


def test_failover_does_not_trigger_when_disabled() -> None:
    primary = FakeStubLlm("gemini", LlmUnavailableError("Gemini API returned 429"))
    secondary = FakeStubLlm("claude", {"answerable": True})

    failover = FailoverJsonLlm(primary, secondary, fallback_enabled=False)  # type: ignore[arg-type]

    with pytest.raises(LlmUnavailableError, match="429"):
        failover.complete_json("system", "user", SCHEMA)

    assert primary.call_count == 1
    assert secondary.call_count == 0


def test_failover_does_not_trigger_on_model_decline() -> None:
    """Safety/refusal policy decisions must never fail over to another model."""
    primary = FakeStubLlm("gemini", LlmDeclinedError("the model declined to answer"))
    secondary = FakeStubLlm("claude", {"answerable": True})

    failover = FailoverJsonLlm(primary, secondary, fallback_enabled=True)  # type: ignore[arg-type]

    with pytest.raises(LlmDeclinedError, match="declined"):
        failover.complete_json("system", "user", SCHEMA)

    assert primary.call_count == 1
    assert secondary.call_count == 0


def test_failover_re_raises_if_secondary_unconfigured() -> None:
    primary = FakeStubLlm("gemini", LlmUnavailableError("Primary timed out"))
    secondary = FakeStubLlm("claude", {"answerable": True}, is_configured=False)

    failover = FailoverJsonLlm(primary, secondary, fallback_enabled=True)  # type: ignore[arg-type]

    with pytest.raises(LlmUnavailableError, match="Primary timed out"):
        failover.complete_json("system", "user", SCHEMA)

    assert primary.call_count == 1
    assert secondary.call_count == 0


def test_build_llm_respects_fallback_setting() -> None:
    no_fallback = Settings(
        llm_provider="gemini",
        llm_fallback_enabled=False,
        gemini_api_key="gkey",  # type: ignore[arg-type]
        anthropic_api_key="ckey",  # type: ignore[arg-type]
    )
    llm1 = build_llm(no_fallback, "answer")
    assert isinstance(llm1, GeminiJsonLlm)

    with_fallback = Settings(
        llm_provider="gemini",
        llm_fallback_enabled=True,
        gemini_api_key="gkey",  # type: ignore[arg-type]
        anthropic_api_key="ckey",  # type: ignore[arg-type]
    )
    llm2 = build_llm(with_fallback, "answer")
    assert isinstance(llm2, FailoverJsonLlm)
    assert llm2.configured
