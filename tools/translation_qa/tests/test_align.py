from translation_qa.align import align_sentences


def test_align_one_to_one():
    english = "The cross is central. Suffering can be unjust."
    spanish = "La cruz es central. El sufrimiento puede ser injusto."
    pairs = align_sentences(english, spanish)
    assert len(pairs) == 2
    assert "cross" in pairs[0].english.lower()
    assert "cruz" in pairs[0].translated.lower()


def test_align_handles_empty():
    assert align_sentences("", "texto") == []
    assert align_sentences("Hello.", "") == []
