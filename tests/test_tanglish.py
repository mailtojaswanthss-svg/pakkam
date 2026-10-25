from schemebot.retrieve.tanglish import gloss_tanglish


def test_question_words_and_particles_become_english() -> None:
    assert gloss_tanglish("ujjwala gas connection ku enna documents venum") == (
        "ujjwala gas connection for what documents needed"
    )


def test_case_endings_joined_to_a_known_word_are_glossed() -> None:
    assert gloss_tanglish("breakfast scheme endha class pasangalukku") == (
        "breakfast scheme which class for children"
    )


def test_scheme_names_and_unknown_words_pass_through_unchanged() -> None:
    assert gloss_tanglish("magalir urimai thogai Pudhumai Penn") == (
        "magalir urimai thogai Pudhumai Penn"
    )


def test_a_suffix_alone_does_not_gloss_an_unknown_stem() -> None:
    # "kisan" ends in "an", not a case ending; "ujjwalaku" has an unknown stem.
    assert gloss_tanglish("kisan ujjwalaku") == "kisan ujjwalaku"


def test_dropped_particles_leave_no_double_spaces_and_punctuation_is_kept() -> None:
    assert gloss_tanglish("idhu free dhaan ah?") == "idhu free ?"
