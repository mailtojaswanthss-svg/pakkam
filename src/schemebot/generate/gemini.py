"""Gemini through the google-genai SDK, behind the same JsonLlm interface as Claude.

The alternative provider (SCHEMEBOT_LLM_PROVIDER=gemini). It asks for JSON that follows the
same schemas and reports failures as the same two errors, so the answer pipeline, the
guardrail and the evaluation run unchanged.
"""

import json
import logging
from typing import Any

import httpx

from schemebot.config import Effort
from schemebot.generate.llm import MAX_OUTPUT_TOKENS, LlmDeclinedError, LlmUnavailableError

logger = logging.getLogger(__name__)

THINKING_LEVEL: dict[Effort, str] = {
    "low": "LOW",
    "medium": "MEDIUM",
    "high": "HIGH",
    "xhigh": "HIGH",
    "max": "HIGH",
}

# The free tier allows only a few requests per minute. Rate-limited and server errors are
# retried with backoff (2, 4, 8 ... capped at 60 s; about three minutes in all) before the
# call counts as unavailable.
RETRY_ATTEMPTS = 8
RETRY_INITIAL_DELAY_S = 2.0
RETRY_MAX_DELAY_S = 60.0
REQUEST_TIMEOUT_MS = 120_000

BLOCKED = frozenset(
    {"SAFETY", "BLOCKLIST", "PROHIBITED_CONTENT", "SPII", "RECITATION", "JAILBREAK", "OTHER"}
)
"""Finish or block reasons that mean the model would not answer."""


def _name(value: object) -> str:
    """Enum member name, or the raw value for reasons newer than the installed SDK."""
    return str(getattr(value, "name", value))


class GeminiJsonLlm:
    def __init__(self, model: str, api_key: str | None, effort: Effort) -> None:
        from google import genai
        from google.genai import errors, types

        self._types: Any = types
        self._errors: Any = errors
        self._model = model
        self._effort = effort
        options = types.HttpOptions(
            timeout=REQUEST_TIMEOUT_MS,
            retry_options=types.HttpRetryOptions(
                attempts=RETRY_ATTEMPTS,
                initial_delay=RETRY_INITIAL_DELAY_S,
                max_delay=RETRY_MAX_DELAY_S,
            ),
        )
        # api_key=None lets the SDK use GEMINI_API_KEY or GOOGLE_API_KEY. With none of
        # them it raises at construction; keep going so the app can still start and refuse.
        self._client: Any
        try:
            self._client = genai.Client(api_key=api_key, http_options=options)
        except ValueError:
            self._client = None
            logger.warning(
                "No Gemini API key found; questions that reach the LLM will be refused. "
                "Set SCHEMEBOT_GEMINI_API_KEY in .env."
            )

    @property
    def configured(self) -> bool:
        return self._client is not None

    def complete_json(self, system: str, user: str, schema: dict[str, object]) -> dict[str, Any]:
        if self._client is None:
            raise LlmUnavailableError("no Gemini API key configured")

        types = self._types
        config = types.GenerateContentConfig(
            system_instruction=system,
            response_mime_type="application/json",
            response_json_schema=schema,
            max_output_tokens=MAX_OUTPUT_TOKENS,
            thinking_config=types.ThinkingConfig(thinking_level=THINKING_LEVEL[self._effort]),
        )
        try:
            response = self._client.models.generate_content(
                model=self._model, contents=user, config=config
            )
        except self._errors.APIError as error:
            logger.error("Gemini API error %s %s", error.code, error.status)
            raise LlmUnavailableError(f"Gemini API returned {error.code}") from error
        except httpx.HTTPError as error:  # connection failures and timeouts
            raise LlmUnavailableError("could not reach the Gemini API") from error

        return _json_from(response)


def _json_from(response: Any) -> dict[str, Any]:
    feedback = response.prompt_feedback
    if feedback is not None and feedback.block_reason is not None:
        raise LlmDeclinedError(f"Gemini blocked the request ({_name(feedback.block_reason)})")
    if not response.candidates:
        raise LlmUnavailableError("Gemini returned no answer")

    reason = _name(response.candidates[0].finish_reason)
    if reason in BLOCKED:
        raise LlmDeclinedError(f"Gemini stopped the answer ({reason})")
    if reason == "MAX_TOKENS":
        raise LlmUnavailableError("the answer was cut off at the token limit")

    text = response.text
    if not text:
        raise LlmUnavailableError("the response contained no text")
    try:
        result = json.loads(text)
    except json.JSONDecodeError as error:
        raise LlmUnavailableError("the response was not valid JSON") from error
    if not isinstance(result, dict):
        raise LlmUnavailableError("the response was not a JSON object")
    return result
