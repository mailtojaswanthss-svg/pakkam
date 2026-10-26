"""Builds a ready-to-use Answerer, and the LLM clients for each role, from settings."""

from typing import Literal

from schemebot.config import Effort, Settings
from schemebot.generate.answer import Answerer
from schemebot.generate.contacts import CONTACTS_NAME, load_contacts
from schemebot.generate.llm import ConfiguredJsonLlm
from schemebot.ingest.corrections import CORRECTIONS_NAME, load_corrections
from schemebot.retrieve.factory import build_retriever
from schemebot.retrieve.retriever import Retriever

LlmRole = Literal["answer", "verifier", "judge"]


def model_for(settings: Settings, role: LlmRole) -> str:
    if settings.llm_provider == "gemini":
        return {
            "answer": settings.gemini_model,
            "verifier": settings.gemini_verifier_model,
            "judge": settings.gemini_judge_model,
        }[role]
    return {
        "answer": settings.llm_model,
        "verifier": settings.verifier_model,
        "judge": settings.judge_model,
    }[role]


def build_llm(settings: Settings, role: LlmRole) -> ConfiguredJsonLlm:
    # The verifier only reads and judges, so a fast model at low effort is enough.
    effort: Effort = {"answer": settings.llm_effort, "verifier": "low", "judge": "medium"}[role]
    model = model_for(settings, role)
    limits = (settings.llm_timeout_seconds, settings.llm_retries)
    if settings.llm_provider == "gemini":
        from schemebot.generate.gemini import GeminiJsonLlm

        key = settings.gemini_api_key
        return GeminiJsonLlm(model, key.get_secret_value() if key else None, effort, *limits)

    from schemebot.generate.llm import ClaudeJsonLlm

    key = settings.anthropic_api_key
    return ClaudeJsonLlm(model, key.get_secret_value() if key else None, effort, *limits)


def build_answerer(settings: Settings, retriever: Retriever | None = None) -> Answerer:
    """`retriever` lets callers share already-loaded models instead of loading them twice."""
    verifier = build_llm(settings, "verifier") if settings.verify_answers else None
    contacts = load_contacts(settings.data_dir / CONTACTS_NAME)
    return Answerer(
        retriever or build_retriever(settings),
        build_llm(settings, "answer"),
        verifier,
        settings.refusal_threshold,
        contacts,
        load_corrections(settings.data_dir / CORRECTIONS_NAME),
    )
