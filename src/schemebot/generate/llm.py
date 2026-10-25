"""Thin wrapper around the Claude API that returns schema-valid JSON.

Kept behind a small protocol so the answering logic can be tested with a fake and the
model provider can be swapped without touching it.
"""

import json
import logging
from typing import Any, Protocol, TypeVar

from pydantic import BaseModel, ValidationError

from schemebot.config import Effort

logger = logging.getLogger(__name__)

MAX_OUTPUT_TOKENS = 16000
FALLBACK_BETA = "server-side-fallback-2026-07-01"

# Models that accept the server-side refusal fallback (`fallbacks="default"`). Claude Haiku
# 5.5 has none, and sending the beta to a model without it is rejected, so the verifier
# must go through the plain endpoint.
FALLBACK_MODELS = frozenset(
    {"claude-fable-5-1", "claude-opus-5-5", "claude-opus-5", "claude-sonnet-5-5"}
)


class LlmDeclinedError(RuntimeError):
    """The model (and its server-side fallback) refused the request."""


class LlmUnavailableError(RuntimeError):
    """The API could not be reached or returned an error after retries."""


class JsonLlm(Protocol):
    def complete_json(
        self, system: str, user: str, schema: dict[str, object]
    ) -> dict[str, Any]: ...


class ConfiguredJsonLlm(JsonLlm, Protocol):
    @property
    def configured(self) -> bool:
        """Whether the client found credentials it can call the API with."""
        ...


ReplyT = TypeVar("ReplyT", bound=BaseModel)


def parse_reply(model: type[ReplyT], raw: dict[str, Any]) -> ReplyT:
    """Validate a JSON reply. Structured output should guarantee the shape, but a reply
    that still doesn't match is treated as a service failure rather than a crash."""
    try:
        return model.model_validate(raw)
    except ValidationError as error:
        raise LlmUnavailableError("the reply did not match the expected schema") from error


def has_credentials(client: Any) -> bool:
    """True if the SDK client resolved an API key, auth token or `ant auth login` profile."""
    return bool(client.api_key or client.auth_token or client.credentials is not None)


class ClaudeJsonLlm:
    def __init__(self, model: str, api_key: str | None, effort: Effort) -> None:
        import anthropic

        # api_key=None lets the SDK find credentials itself (env var or `ant auth login`).
        self._client = anthropic.Anthropic(api_key=api_key)
        self._anthropic = anthropic
        self._model = model
        self._effort = effort
        if not has_credentials(self._client):
            logger.warning(
                "No Claude API credentials found; questions that reach the LLM will be "
                "refused. Set SCHEMEBOT_ANTHROPIC_API_KEY in .env."
            )

    @property
    def configured(self) -> bool:
        """Whether the client found credentials it can call the API with."""
        return has_credentials(self._client)

    def complete_json(self, system: str, user: str, schema: dict[str, object]) -> dict[str, Any]:
        from anthropic.types.beta import BetaMessageParam, BetaOutputConfigParam

        # Without credentials the SDK raises a bare TypeError at request time; report it as
        # an unavailable service instead, without catching TypeError (which would also hide
        # genuine programming errors).
        if not has_credentials(self._client):
            raise LlmUnavailableError("no Claude API credentials configured")

        anthropic = self._anthropic
        messages: list[BetaMessageParam] = [{"role": "user", "content": user}]
        output_config: BetaOutputConfigParam = {
            "effort": self._effort,
            "format": {"type": "json_schema", "schema": schema},
        }
        # On a safety decline, the API retries on Anthropic's recommended fallback model.
        fallback: dict[str, Any] = (
            {"betas": [FALLBACK_BETA], "fallbacks": "default"}
            if self._model in FALLBACK_MODELS
            else {}
        )
        try:
            response = self._client.beta.messages.create(
                model=self._model,
                max_tokens=MAX_OUTPUT_TOKENS,
                system=system,
                messages=messages,
                output_config=output_config,
                **fallback,
            )
        except anthropic.APIConnectionError as error:
            raise LlmUnavailableError("could not reach the Claude API") from error
        except anthropic.RateLimitError as error:
            raise LlmUnavailableError("Claude API rate limit reached") from error
        except anthropic.APIStatusError as error:
            logger.error("Claude API error %s (request %s)", error.status_code, error.request_id)
            raise LlmUnavailableError(f"Claude API returned {error.status_code}") from error

        if response.stop_reason == "refusal":
            raise LlmDeclinedError("the model declined to answer")
        if response.stop_reason == "max_tokens":
            raise LlmUnavailableError("the answer was cut off at the token limit")

        text = next((block.text for block in response.content if block.type == "text"), None)
        if text is None:
            raise LlmUnavailableError("the response contained no text block")
        try:
            result: dict[str, Any] = json.loads(text)
        except json.JSONDecodeError as error:
            raise LlmUnavailableError("the response was not valid JSON") from error
        return result
