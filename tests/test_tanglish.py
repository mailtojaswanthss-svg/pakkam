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


def test_word_pairs_are_glossed_as_phrases() -> None:
    assert gloss_tanglish("atal pension la join panna age evlo") == (
        "atal pension in to join what age"
    )


def test_phrases_ignore_case_and_leave_the_rest_to_the_word_pass() -> None:
    assert gloss_tanglish("Apply Panna enna venum") == "to apply what needed"


def test_verbs_from_the_dev_misses_are_known() -> None:
    assert gloss_tanglish("CM health insurance card ku income evlo irukanum") == (
        "CM health insurance card for income how much must be"
    )
    assert gloss_tanglish("11th padikra BC MBC pasangalukku free cycle tharaangala") == (
        "11th studying BC MBC for children free cycle do they give"
    )
    assert gloss_tanglish(
        "govt school la padicha ponnunga college ponaa maasam evlo kudupaanga"
    ) == ("govt school in studied girls college goes to month how much they give")
