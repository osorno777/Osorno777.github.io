from translation_qa.checks.word_coverage import check_word_coverage


def test_missing_proper_name():
    findings = check_word_coverage(
        "Later, Cobin argued that persecution can be unjust.",
        "Mas tarde se argumento que la persecucion puede ser injusta.",
    )
    assert any(item.word == "Cobin" for item in findings)


def test_omitted_sentence():
    findings = check_word_coverage("The servant suffered unjustly.", "")
    assert any(item.check == "word.omission" for item in findings)


def test_kept_name_passes():
    findings = check_word_coverage(
        "Later, Cobin argued the point.",
        "Mas tarde, Cobin argumento el punto.",
    )
    assert not any(item.word == "Cobin" for item in findings)
