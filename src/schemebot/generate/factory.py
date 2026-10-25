"""Builds a ready-to-use Answerer from settings."""

from schemebot.config import Settings
from schemebot.generate.answer import Answerer
from schemebot.generate.contacts import CONTACTS_NAME, load_contacts
from schemebot.generate.llm import ClaudeJsonLlm
from schemebot.retrieve.factory import build_retriever
from schemebot.retrieve.retriever import Retriever


def build_answerer(settings: Settings, retriever: Retriever | None = None) -> Answerer:
    """`retriever` lets callers share already-loaded models instead of loading them twice."""
    api_key = settings.anthropic_api_key.get_secret_value() if settings.anthropic_api_key else None
    llm = ClaudeJsonLlm(settings.llm_model, api_key, effort=settings.llm_effort)
    # The verifier only reads and judges, so a fast model at low effort is enough.
    verifier = (
        ClaudeJsonLlm(settings.verifier_model, api_key, effort="low")
        if settings.verify_answers
        else None
    )
    contacts = load_contacts(settings.data_dir / CONTACTS_NAME)
    return Answerer(
        retriever or build_retriever(settings),
        llm,
        verifier,
        settings.refusal_threshold,
        contacts,
    )
