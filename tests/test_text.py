from schemebot.text import normalize_for_search


def test_tamil_and_devanagari_digits_become_ascii() -> None:
    tamil_two_point_five = chr(0x0BE8) + "." + chr(0x0BEB)  # ௨.௫
    devanagari_sixty = chr(0x0966 + 6) + chr(0x0966)  # ६०

    assert normalize_for_search(f"{tamil_two_point_five} லட்சம்") == "2.5 லட்சம்"
    assert normalize_for_search(f"{devanagari_sixty} वर्ष") == "60 वर्ष"


def test_invisible_characters_and_extra_spaces_are_removed() -> None:
    zwnj = chr(0x200C)

    assert normalize_for_search(f"  தகுதி{zwnj}   என்ன ") == "தகுதி என்ன"


def test_ascii_text_is_unchanged() -> None:
    assert normalize_for_search("Who is eligible for PM-KISAN?") == "Who is eligible for PM-KISAN?"
