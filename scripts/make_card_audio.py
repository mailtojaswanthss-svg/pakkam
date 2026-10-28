"""Pre-generate TTS audio for verified fact cards using Gnani Timbre.

Caches audio files in data/audio_cache/ (gitignored).
Generates Tamil audio first, staying strictly under the daily Gnani cap.
"""

import json
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from schemebot.config import get_settings
from schemebot.generate.fact_cards import load_verified_cards
from schemebot.voice.numbers import spell_amounts
from schemebot.voice.tts import build_speaker, language_code_for

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("make_card_audio")

AUDIO_CACHE_DIR = PROJECT_ROOT / "data" / "audio_cache"


def main():
    settings = get_settings()
    cards_path = PROJECT_ROOT / "data" / "fact_cards.json"
    cards = load_verified_cards(cards_path)
    
    if not cards:
        logger.warning("No verified fact cards found in %s", cards_path)
        return

    # Sort so Tamil cards come first
    sorted_cards = sorted(cards, key=lambda c: (0 if c.language == "ta" else 1, c.card_id))
    
    AUDIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Read current budget status
    calls_file = settings.log_dir / "gnani-calls.json"
    current_calls = 0
    if calls_file.is_file():
        try:
            current_calls = json.loads(calls_file.read_text(encoding="utf-8")).get("calls", 0)
        except Exception:
            pass

    calls_needed = len(sorted_cards)
    logger.info("Current Gnani calls today: %d / %d", current_calls, settings.gnani_max_calls_per_day)
    logger.info("TTS calls required for %d verified cards: %d calls", len(sorted_cards), calls_needed)

    if current_calls + calls_needed > settings.gnani_max_calls_per_day:
        logger.error("Generating audio would exceed daily Gnani cap! Aborting.")
        return

    speaker = build_speaker(settings)
    if speaker is None:
        logger.error("No Gnani API key configured (settings.gnani_api_key is None). Aborting.")
        return

    logger.info("Generating audio with Timbre model: %s", settings.tts_model)
    generated = 0
    for card in sorted_cards:
        out_file = AUDIO_CACHE_DIR / f"{card.card_id}.wav"
        if out_file.exists():
            logger.info("Audio already exists for card %s at %s, skipping", card.card_id, out_file)
            continue

        # Spoken text: numbers spelled out for natural pronunciation
        spoken_text = spell_amounts(card.answer_text, card.language) # type: ignore
        lang_code = language_code_for(card.language)

        logger.info("Calling Timbre TTS for card %s (%s, %s)...", card.card_id, card.language, lang_code)
        try:
            audio_bytes = speaker.speak(spoken_text, lang_code)
            out_file.write_bytes(audio_bytes)
            generated += 1
            logger.info("Saved %d bytes to %s", len(audio_bytes), out_file)
        except Exception as err:
            logger.error("Failed to generate audio for card %s: %s", card.card_id, err)

    logger.info("Finished. Generated %d audio files in %s", generated, AUDIO_CACHE_DIR)


if __name__ == "__main__":
    main()
