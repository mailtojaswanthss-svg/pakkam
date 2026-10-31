"""Builds a ready-to-use Answerer, and the LLM clients for each role, from settings."""

from typing import Literal

from schemebot.config import Effort, LlmProvider, Settings
from schemebot.generate.answer import Answerer
from schemebot.generate.contacts import CONTACTS_NAME, load_contacts
from schemebot.generate.llm import ConfiguredJsonLlm
from schemebot.ingest.corrections import CORRECTIONS_NAME, load_corrections
from schemebot.retrieve.factory import build_retriever
from schemebot.retrieve.retriever import Retriever

LlmRole = Literal["answer", "verifier", "judge"]


def model_for_provider(settings: Settings, role: LlmRole, provider: LlmProvider) -> str:
    if provider == "gemini":
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


def model_for(settings: Settings, role: LlmRole) -> str:
    return model_for_provider(settings, role, settings.llm_provider)


def _build_provider_llm(
    settings: Settings, role: LlmRole, provider: LlmProvider
) -> ConfiguredJsonLlm:
    from schemebot.generate.budget import shared_llm_budget

    budget = shared_llm_budget(
        settings.data_dir / "llm-calls.json",
        settings.max_daily_llm_calls,
        settings.llm_reset_time,
    )
    effort: Effort = {"answer": settings.llm_effort, "verifier": "low", "judge": "medium"}[role]
    model = model_for_provider(settings, role, provider)
    limits = (settings.llm_timeout_seconds, settings.llm_retries)
    if provider == "gemini":
        from schemebot.generate.gemini import GeminiJsonLlm

        key = settings.gemini_api_key
        return GeminiJsonLlm(
            model, key.get_secret_value() if key else None, effort, *limits, budget=budget
        )

    from schemebot.generate.llm import ClaudeJsonLlm

    key = settings.anthropic_api_key
    return ClaudeJsonLlm(
        model, key.get_secret_value() if key else None, effort, *limits, budget=budget
    )


def build_llm(settings: Settings, role: LlmRole) -> ConfiguredJsonLlm:
    primary = _build_provider_llm(settings, role, settings.llm_provider)
    if not settings.llm_fallback_enabled:
        return primary

    secondary_provider: LlmProvider = "claude" if settings.llm_provider == "gemini" else "gemini"
    secondary = _build_provider_llm(settings, role, secondary_provider)
    from schemebot.generate.llm import FailoverJsonLlm

    return FailoverJsonLlm(primary, secondary, fallback_enabled=True)


def build_answerer(settings: Settings, retriever: Retriever | None = None) -> Answerer:
    """`retriever` lets callers share already-loaded models instead of loading them twice."""
    from schemebot.generate.fact_cards import FactCardMatcher, load_verified_cards

    retriever_obj = retriever or build_retriever(settings)
    verifier = build_llm(settings, "verifier") if settings.verify_answers else None
    contacts = load_contacts(settings.data_dir / CONTACTS_NAME)
    cards_path = settings.data_dir / "fact_cards.json"
    cards = load_verified_cards(cards_path)
    matcher = None
    if (
        cards
        and hasattr(retriever_obj, "_first_stage")
        and hasattr(retriever_obj._first_stage, "_encoder")
    ):
        matcher = FactCardMatcher(cards, encoder=retriever_obj._first_stage._encoder)

    alias_path = settings.data_dir / "scheme_aliases.json"
    alias_matcher = None
    if alias_path.is_file():
        from schemebot.retrieve.aliases import AliasMatcher

        alias_matcher = AliasMatcher.load(alias_path)

    return Answerer(
        retriever_obj,
        build_llm(settings, "answer"),
        verifier,
        settings.refusal_threshold,
        contacts,
        load_corrections(settings.data_dir / CORRECTIONS_NAME),
        fact_cards=matcher,
        alias_matcher=alias_matcher,
        rewriter=build_llm(settings, "verifier") if settings.rewrite_unclear_questions else None,
    )
