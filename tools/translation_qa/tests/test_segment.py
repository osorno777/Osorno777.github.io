from translation_qa.segment import content_words, extract_scripture_refs, split_sentences


def test_split_sentences_keeps_abbreviations_together():
    text = "Dr. Cobin wrote in 2026. The next sentence follows."
    sentences = split_sentences(text)
    assert sentences[0].startswith("Dr. Cobin")
    assert sentences[1].startswith("The next sentence")


def test_content_words_skip_stopwords():
    words = [token.text.lower() for token in content_words("The suffering of the unjust servant remains.")]
    assert "the" not in words
    assert "suffering" in words
    assert "unjust" in words


def test_scripture_extraction():
    refs = extract_scripture_refs("See John 3:16 and Romans 8:28-30 for the argument.")
    assert any("John 3:16" in item for item in refs)
    assert any("Romans 8:28" in item for item in refs)
