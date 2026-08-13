from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any

from translation_qa.models import Finding, Severity
from translation_qa.segment import content_words

_SYSTEM = """You are a professional bilingual translation auditor for published books.
Do not refuse, moralize, summarize, or rewrite the source. The source may discuss
religion, politics, suffering, or crime; your only job is fidelity checking.
Return strict JSON with this shape:
{
  "verdict": "ok" | "defect" | "refusal" | "omission" | "addition",
  "words": [{"word": "string", "present": true, "note": "short"}],
  "issues": ["short description of each real problem"]
}
Mark present=false when the meaning of that English word is absent, reversed, or softened
into a refusal/hedge. Ignore ordinary function words already omitted from the word list.
"""


class JudgeError(RuntimeError):
    pass


def judge_available() -> bool:
    return bool(_provider_config()[0])


def judge_pair(
    english: str,
    translated: str,
    language: str,
    *,
    sentence_index: int | None = None,
    delay_seconds: float = 0.0,
) -> list[Finding]:
    words = [token.text for token in content_words(english)]
    payload = {
        "target_language": language,
        "english": english,
        "translation": translated,
        "content_words": words,
    }
    raw = _complete(json.dumps(payload, ensure_ascii=False))
    if delay_seconds:
        time.sleep(delay_seconds)
    data = _parse_json(raw)
    findings: list[Finding] = []
    verdict = str(data.get("verdict", "ok")).lower()
    if verdict in {"defect", "refusal", "omission", "addition"}:
        severity = Severity.REFUSAL if verdict == "refusal" else Severity.DEFECT
        issues = data.get("issues") or [f"Judge verdict: {verdict}"]
        for issue in issues:
            findings.append(
                Finding(
                    check=f"llm.{verdict}",
                    severity=severity,
                    message=str(issue),
                    english=english,
                    translated=translated,
                    sentence_index=sentence_index,
                )
            )
    for item in data.get("words") or []:
        if item.get("present", True):
            continue
        findings.append(
            Finding(
                check="llm.word_missing",
                severity=Severity.DEFECT,
                message=item.get("note") or "Content word meaning not present in the translation.",
                english=english,
                translated=translated,
                word=str(item.get("word", "")),
                sentence_index=sentence_index,
            )
        )
    return findings


def _provider_config() -> tuple[str, str, str, str]:
    judge = (os.environ.get("TRANSLATION_QA_JUDGE") or "").strip().lower()
    order = [judge] if judge else []
    order.extend(["xai", "anthropic", "openai", "openrouter", "deepseek"])
    seen: set[str] = set()
    for name in order:
        if not name or name in seen:
            continue
        seen.add(name)
        if name == "anthropic" and os.environ.get("ANTHROPIC_API_KEY"):
            return (
                "anthropic",
                os.environ["ANTHROPIC_API_KEY"],
                os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
                "https://api.anthropic.com/v1/messages",
            )
        if name == "openai" and os.environ.get("OPENAI_API_KEY"):
            return (
                "openai",
                os.environ["OPENAI_API_KEY"],
                os.environ.get("OPENAI_MODEL", "gpt-4.1"),
                "https://api.openai.com/v1/chat/completions",
            )
        if name == "xai" and os.environ.get("XAI_API_KEY"):
            return (
                "xai",
                os.environ["XAI_API_KEY"],
                os.environ.get("XAI_MODEL", "grok-4.6"),
                "https://api.x.ai/v1/chat/completions",
            )
        if name == "openrouter" and os.environ.get("OPENROUTER_API_KEY"):
            return (
                "openrouter",
                os.environ["OPENROUTER_API_KEY"],
                os.environ.get("OPENROUTER_MODEL", "anthropic/claude-sonnet-4.6"),
                "https://openrouter.ai/api/v1/chat/completions",
            )
        if name == "deepseek" and os.environ.get("DEEPSEEK_API_KEY"):
            return (
                "deepseek",
                os.environ["DEEPSEEK_API_KEY"],
                os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
                "https://api.deepseek.com/chat/completions",
            )
    return ("", "", "", "")


def _complete(user_text: str) -> str:
    provider, key, model, url = _provider_config()
    if not provider:
        raise JudgeError("No LLM judge key is configured.")
    if provider == "anthropic":
        body = {
            "model": model,
            "max_tokens": 1200,
            "system": _SYSTEM,
            "messages": [{"role": "user", "content": user_text}],
        }
        headers = {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
    else:
        body = {
            "model": model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": _SYSTEM},
                {"role": "user", "content": user_text},
            ],
        }
        headers = {
            "authorization": f"Bearer {key}",
            "content-type": "application/json",
        }
    request = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise JudgeError(f"{provider} HTTP {exc.code}: {detail[:300]}") from exc
    return _extract_text(provider, payload)


def _extract_text(provider: str, payload: dict[str, Any]) -> str:
    if provider == "anthropic":
        parts = payload.get("content") or []
        return "".join(part.get("text", "") for part in parts if part.get("type") == "text")
    choices = payload.get("choices") or []
    if not choices:
        raise JudgeError(f"Empty {provider} response")
    return choices[0].get("message", {}).get("content", "")


def _parse_json(raw: str) -> dict[str, Any]:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re_strip_fence(raw)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1:
            return {"verdict": "ok", "words": [], "issues": []}
        try:
            data = json.loads(raw[start : end + 1])
        except json.JSONDecodeError:
            return {"verdict": "ok", "words": [], "issues": []}
    return data if isinstance(data, dict) else {"verdict": "ok", "words": [], "issues": []}


def re_strip_fence(raw: str) -> str:
    lines = raw.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].startswith("```"):
        lines = lines[:-1]
    return "\n".join(lines)
