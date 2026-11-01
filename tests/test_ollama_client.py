import json
import requests

from app.ollama_client import analyze_with_ollama, _keep_source_backed_evidence


def test_evidence_filter_removes_invented_sender_and_link():
    evidence = [
        "winner@free-prize-claim.example.com",
        "within 12 hours",
        "http://not-present.example/path",
        "cash prize",
    ]
    result = _keep_source_backed_evidence(
        evidence,
        "winner@free-prize-claim.example.com",
        "Congratulations",
        "Claim your cash prize within 12 hours",
    )
    assert result == [
        "winner@free-prize-claim.example.com",
        "within 12 hours",
        "cash prize",
    ]


def test_ollama_client_filters_unsupported_evidence(monkeypatch):
    payload = {
        "verdict": "Suspicious",
        "reasons": ["The message creates urgency"],
        "evidence": ["within 24 hours", "http://invented.example/verify", "verified official sender"],
        "confidence": 0.8,
        "uncertainty": "Sender is not independently verified",
        "next_steps": ["Verify through a trusted channel"],
    }

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"response": json.dumps(payload)}

    def fake_post(*args, **kwargs):
        assert kwargs["timeout"] == 90
        assert "never call a sender" in kwargs["json"]["prompt"].lower()
        return FakeResponse()

    monkeypatch.setattr(requests, "post", fake_post)
    result = analyze_with_ollama(
        "security@example.com", "Account warning", "Act within 24 hours", "http://localhost:11434", "llama3.2:3b"
    )
    assert result["evidence"] == ["within 24 hours"]
    assert result["verdict"] == "Suspicious"


def test_ollama_client_clamps_confidence(monkeypatch):
    payload = {
        "verdict": "Likely legitimate", "reasons": [], "evidence": [],
        "confidence": 2, "uncertainty": "unknown", "next_steps": []
    }

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"response": json.dumps(payload)}

    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: FakeResponse())
    result = analyze_with_ollama("a@example.com", "Hello", "Hi", "http://localhost:11434", "llama3.2:3b")
    assert result["confidence"] == 1.0
