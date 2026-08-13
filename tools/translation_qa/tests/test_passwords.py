import os

from translation_qa.passwords import load_pdf_passwords


def test_load_pdf_passwords_splits_and_dedupes(monkeypatch):
    monkeypatch.setenv("PDF_PASSWORDS", "alpha; beta ;; alpha;gamma")
    assert load_pdf_passwords(["gamma", "delta"]) == ["alpha", "beta", "gamma", "delta"]


def test_load_pdf_passwords_empty(monkeypatch):
    monkeypatch.delenv("PDF_PASSWORDS", raising=False)
    assert load_pdf_passwords() == []
