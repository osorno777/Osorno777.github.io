from translation_qa.checks.refusals import check_refusals
from translation_qa.models import Severity


def test_detects_english_refusal():
    findings = check_refusals("I cannot assist with that translation as an AI.")
    assert any(item.severity == Severity.REFUSAL for item in findings)


def test_detects_placeholder():
    findings = check_refusals("Chapter 4\n[unable to translate]\n")
    assert any(item.check == "refusal.placeholder" for item in findings)


def test_clean_text_has_no_refusal():
    findings = check_refusals("El sufrimiento injusto no anula la esperanza cristiana.")
    assert findings == []
