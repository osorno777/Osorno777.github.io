import os

from translation_qa.checks.llm_judge import _provider_config


def test_default_xai_model_is_grok_46(monkeypatch):
    monkeypatch.setenv("TRANSLATION_QA_JUDGE", "xai")
    monkeypatch.setenv("XAI_API_KEY", "test-key")
    monkeypatch.delenv("XAI_MODEL", raising=False)
    provider, _key, model, url = _provider_config()
    assert provider == "xai"
    assert model == "grok-4.6"
    assert url.startswith("https://api.x.ai/")


def test_explicit_judge_wins(monkeypatch):
    monkeypatch.setenv("TRANSLATION_QA_JUDGE", "xai")
    monkeypatch.setenv("XAI_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "other-key")
    provider, _, model, _ = _provider_config()
    assert provider == "xai"
    assert model == os.environ.get("XAI_MODEL", "grok-4.6")
