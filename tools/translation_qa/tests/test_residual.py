from translation_qa.checks.residual_english import check_residual_english


def test_flags_untranslated_english_run():
    text = "El libro dice the government must not steal from the people y luego sigue."
    findings = check_residual_english(text, "es")
    assert findings
    assert findings[0].check == "residual_english.run"


def test_ignores_english_source_language():
    assert check_residual_english("The government must not steal from the people.", "en") == []
