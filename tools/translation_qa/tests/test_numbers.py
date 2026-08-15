from translation_qa.checks.numbers import check_numbers_and_refs


def test_missing_year_is_a_defect():
    findings = check_numbers_and_refs("The law was passed in 1973.", "La ley fue aprobada.")
    assert any(item.check == "numbers.missing" for item in findings)


def test_missing_scripture_is_a_defect():
    findings = check_numbers_and_refs("See John 3:16.", "Vea el evangelio.")
    assert any(item.check == "numbers.scripture_missing" for item in findings)


def test_matching_numbers_pass():
    findings = check_numbers_and_refs("In 1973 about 50 states reacted.", "En 1973 unos 50 estados reaccionaron.")
    assert findings == []
