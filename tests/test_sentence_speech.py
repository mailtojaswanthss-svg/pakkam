"""Unit tests for sentence-by-sentence speech synthesis and stop control.

Verifies:
- Sentence boundary splitting (Tamil, Hindi, English).
- Spelled-out Indic currency numbers via voice/numbers.py.
- Pipelined synthesis order and timings.
- Immediate stop control / early termination.
All tests use mock speakers with 0 real Gnani or network calls.
"""


from schemebot.voice.sentence_speaker import SentenceSpeaker, split_sentences

FAKE_WAV = b"RIFF....WAVEfmt "


class MockSpeaker:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def speak(self, text: str, language_code: str) -> bytes:
        self.calls.append((text, language_code))
        return FAKE_WAV


class MockStopFlag:
    def __init__(self, stop_at_index: int) -> None:
        self.stop_at_index = stop_at_index
        self.current = 0

    def is_stopped(self) -> bool:
        return self.current >= self.stop_at_index


def test_split_sentences_tamil_and_english() -> None:
    en_text = "The amount is Rs. 1000. [1] It is given every month. [2] Apply online."
    en_sentences = split_sentences(en_text)
    assert len(en_sentences) == 3
    assert en_sentences[0] == "The amount is Rs. 1000."
    assert en_sentences[1] == "It is given every month."
    assert en_sentences[2] == "Apply online."

    ta_text = "மாதம் ரூ. 1,000 உரிமைத் தொகையாக வழங்கப்படுகிறது. [1] குடும்பத் தலைவிகள் விண்ணப்பிக்கலாம்."
    ta_sentences = split_sentences(ta_text)
    assert len(ta_sentences) == 2
    assert "1,000" in ta_sentences[0]
    assert "[1]" not in ta_sentences[0]


def test_sentence_speaker_spells_indic_numbers() -> None:
    speaker = MockSpeaker()
    sentence_speaker = SentenceSpeaker(speaker, spell_numbers=True)

    # Tamil amount spelling
    spoken, audio, ms = sentence_speaker.synthesize_sentence(
        "மாதம் ரூ. 1,000 வழங்கப்படுகிறது.", "ta"
    )
    assert audio == FAKE_WAV
    assert ms >= 0.0
    assert len(speaker.calls) == 1
    assert "ஆயிரம் ரூபாய்" in spoken
    assert speaker.calls[0][1] == "ta-IN"

    # Hindi amount spelling
    spoken_hi, _, _ = sentence_speaker.synthesize_sentence(
        "प्रति माह रु. 6,000 की वित्तीय सहायता मिलती है.", "hi"
    )
    assert "छह हज़ार रुपये" in spoken_hi
    assert speaker.calls[1][1] == "hi-IN"


def test_stream_sentences_pipelining() -> None:
    speaker = MockSpeaker()
    sentence_speaker = SentenceSpeaker(speaker, spell_numbers=True)

    text = "Sentence one. Sentence two. Sentence three."
    results = list(sentence_speaker.stream_sentences(text, "en"))

    assert len(results) == 3
    assert len(speaker.calls) == 3
    indices = [r[0] for r in results]
    assert indices == [0, 1, 2]
    assert results[0][1] == "Sentence one."
    assert results[1][1] == "Sentence two."
    assert results[2][1] == "Sentence three."


def test_stream_sentences_stop_control() -> None:
    speaker = MockSpeaker()
    sentence_speaker = SentenceSpeaker(speaker, spell_numbers=True)

    class CustomStop:
        def __init__(self) -> None:
            self.count = 0

        def is_stopped(self) -> bool:
            # Stop after 1 sentence has yielded
            return self.count >= 1

    stop_control = CustomStop()

    text = "First sentence here. Second sentence here. Third sentence here."
    items = []
    for idx, spoken, _audio, _ms in sentence_speaker.stream_sentences(
        text, "en", stop_flag=stop_control
    ):
        items.append((idx, spoken))
        stop_control.count += 1

    # Should only produce the first sentence and halt before sentence two
    assert len(items) == 1
    assert items[0][0] == 0
    assert len(speaker.calls) == 1
