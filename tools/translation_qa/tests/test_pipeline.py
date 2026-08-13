from translation_qa.models import Severity
from translation_qa.pipeline import audit_texts


def test_pipeline_flags_refusal_and_omission():
    english = (
        "Christ suffered unjustly in 33. See John 19:16. "
        "The church must not bless state theft."
    )
    translated = (
        "I cannot assist with that religious content. "
        "Cristo sufrió. La iglesia no debe bendecir el robo estatal."
    )
    result = audit_texts(english, translated, "es", word_by_word=True, use_llm=False)
    severities = {item.severity for item in result.findings}
    assert Severity.REFUSAL in severities
    assert result.words_checked > 0
    assert any(item.check.startswith("numbers.") or item.check.startswith("word.") for item in result.findings)


def test_pipeline_accepts_close_spanish():
    english = "Suffering can be unjust. The cross remains central."
    translated = "El sufrimiento puede ser injusto. La cruz sigue siendo central."
    result = audit_texts(english, translated, "es", word_by_word=True, use_llm=False)
    assert result.sentences_compared == 2
    assert result.counts.get("refusal", 0) == 0
    assert result.counts.get("critical", 0) == 0
