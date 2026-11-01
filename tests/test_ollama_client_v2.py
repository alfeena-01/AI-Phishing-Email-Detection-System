import json
import requests
import pytest

from app.ollama_client import (
    _keep_source_backed_evidence,
    _validate_result,
    analyze_with_ollama,
)


def test_evidence_keeps_only_exact_source_backed_items():
    evidence = [
        "URGENT: Verify your account",
        "http://example.test/login",
        "The website is nonexistent",
    ]
    result = _keep_source_backed_evidence(
        evidence,
        "security@example.test",
        "URGENT: Verify your account",
        "Open http://example.test/login",
    )
    assert result == ["URGENT: Verify your account", "http://example.test/login"]


def test_validation_sanitizes_malformed_fields_and_confidence():
    result = _validate_result(
        {
            "verdict": "Suspicious",
            "reasons": ["Payment is requested.", {"made_up": "value"}],
            "evidence": ["Pay ₹149 now", "This website is fake"],
            "confidence": float("nan"),
            "uncertainty": None,
            "next_steps": [
                "Contact the sender through a trusted channel.",
                "Report this to the Federal Trade Commission (FTC).",
            ],
        },
        "delivery@example.test",
        "Delivery fee",
        "Please pay ₹149 now",
    )
    assert result["reasons"] == ["Payment is requested."]
    assert result["evidence"] == ["Pay ₹149 now"]
    assert result["confidence"] == 0.5
    assert result["uncertainty"] == "AI output may be wrong."
    assert result["next_steps"] == ["Contact the sender through a trusted channel."]


def test_validation_rejects_invalid_verdict():
    with pytest.raises(ValueError):
        _validate_result(
            {"verdict": "Definitely safe"},
            "sender@example.test",
            "Hello",
            "Message body",
        )


def test_analyze_with_ollama_uses_sanitized_response(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "response": json.dumps({
                    "verdict": "Suspicious",
                    "reasons": ["The email requests payment."],
                    "evidence": ["Pay now", "The website does not exist"],
                    "confidence": 0.8,
                    "uncertainty": "The sender is not independently verified.",
                    "next_steps": ["Visit the known official website independently."],
                })
            }

    def fake_post(*args, **kwargs):
        assert kwargs["timeout"] == 90
        assert kwargs["json"]["format"] == "json"
        return FakeResponse()

    monkeypatch.setattr(requests, "post", fake_post)
    result = analyze_with_ollama(
        "billing@example.test",
        "Delivery fee",
        "Please Pay now",
        "http://127.0.0.1:11434",
        "llama3.2:3b",
    )
    assert result["evidence"] == ["Pay now"]
    assert result["verdict"] == "Suspicious"
    assert result["next_steps"] == ["Visit the known official website independently."]
