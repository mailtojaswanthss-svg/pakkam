from types import SimpleNamespace
from typing import Any

import pytest

pytest.importorskip("google.genai")

from google.genai import errors, types  # noqa: E402

from schemebot.config import Settings  # noqa: E402
from schemebot.generate.factory import build_llm, model_for  # noqa: E402
from schemebot.generate.gemini import GeminiJsonLlm  # noqa: E402
from schemebot.generate.llm import (  # noqa: E402
    ClaudeJsonLlm,
    LlmDeclinedError,
    LlmUnavailableError,
)

SCHEMA: dict[str, object] = {"type": "object", "properties": {"ok": {"type": "boolean"}}}


def response(
    text: str | None = '{"ok": true}',
    finish: types.FinishReason = types.FinishReason.STOP,
    block: types.BlockedReason | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        prompt_feedback=SimpleNamespace(block_reason=block) if block else None,
        candidates=[SimpleNamespace(finish_reason=finish)],
        text=text,
    )


class FakeModels:
    def __init__(self, reply: object) -> None:
        self.calls: list[dict[str, Any]] = []
        self._reply = reply

    def generate_content(self, **kwargs: Any) -> object:
        self.calls.append(kwargs)
        if isinstance(self._reply, Exception):
            raise self._reply
        return self._reply


def llm_replying(reply: object, effort: Any = "medium") -> tuple[GeminiJsonLlm, FakeModels]:
    llm = GeminiJsonLlm("gemini-test", api_key="test-key", effort=effort)
    models = FakeModels(reply)
    llm._client = SimpleNamespace(models=models)
    return llm, models


def test_returns_the_json_and_sends_schema_system_and_thinking_level() -> None:
    llm, models = llm_replying(response())

    assert llm.complete_json("be brief", "question", SCHEMA) == {"ok": True}

    call = models.calls[0]
    assert call["model"] == "gemini-test"
    assert call["contents"] == "question"
    config = call["config"]
    assert config.system_instruction == "be brief"
    assert config.response_mime_type == "application/json"
    assert config.response_json_schema == SCHEMA
    assert config.thinking_config.thinking_level == types.ThinkingLevel.MEDIUM


def test_a_blocked_prompt_is_a_decline() -> None:
    llm, _ = llm_replying(response(text=None, block=types.BlockedReason.SAFETY))

    with pytest.raises(LlmDeclinedError):
        llm.complete_json("system", "user", SCHEMA)


def test_an_answer_stopped_for_safety_is_a_decline() -> None:
    llm, _ = llm_replying(response(finish=types.FinishReason.SAFETY))

    with pytest.raises(LlmDeclinedError):
        llm.complete_json("system", "user", SCHEMA)


@pytest.mark.parametrize(
    "reply",
    [
        response(finish=types.FinishReason.MAX_TOKENS),
        response(text="not json"),
        response(text="[1, 2]"),
        response(text=""),
        SimpleNamespace(prompt_feedback=None, candidates=[], text=None),
    ],
)
def test_unusable_replies_are_unavailable(reply: object) -> None:
    llm, _ = llm_replying(reply)

    with pytest.raises(LlmUnavailableError):
        llm.complete_json("system", "user", SCHEMA)


def test_api_errors_after_retries_are_unavailable() -> None:
    quota = errors.ClientError(
        429, {"error": {"code": 429, "message": "quota", "status": "RESOURCE_EXHAUSTED"}}
    )
    llm, _ = llm_replying(quota)

    with pytest.raises(LlmUnavailableError, match="429"):
        llm.complete_json("system", "user", SCHEMA)


def test_missing_key_is_unavailable_without_calling_the_api(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    llm = GeminiJsonLlm("gemini-test", api_key=None, effort="low")

    assert not llm.configured
    with pytest.raises(LlmUnavailableError, match="key"):
        llm.complete_json("system", "user", SCHEMA)


def test_provider_setting_picks_the_client_and_models() -> None:
    gemini = Settings(llm_provider="gemini", gemini_api_key="test-key")  # type: ignore[arg-type]
    claude = Settings(anthropic_api_key="test-key")  # type: ignore[arg-type]

    assert isinstance(build_llm(gemini, "answer"), GeminiJsonLlm)
    assert isinstance(build_llm(claude, "answer"), ClaudeJsonLlm)
    assert model_for(gemini, "verifier") == gemini.gemini_verifier_model
    assert model_for(gemini, "judge") != model_for(gemini, "answer")
    assert model_for(claude, "answer") == claude.llm_model
