from app.scoring import calculate_score


def test_legitimate_verdict_without_rule_signals_stays_low():
    result = calculate_score(0, {"verdict": "Likely legitimate", "reasons": ["Formal tone"]})
    assert result["score"] == 0
    assert result["category"] == "Low"


def test_suspicious_verdict_without_rule_signals_does_not_get_reason_bonus():
    result = calculate_score(0, {"verdict": "Suspicious", "reasons": ["Generic greeting"] * 5})
    assert result["score"] == 12
    assert result["category"] == "Low"


def test_rule_signals_remain_main_score_contributor():
    result = calculate_score(40, {"verdict": "Suspicious", "reasons": ["Urgency"]})
    assert result["score"] == 52
    assert result["category"] == "High"


def test_phishing_verdict_adds_limited_ai_contribution():
    result = calculate_score(40, {"verdict": "Likely phishing", "reasons": ["Credential request"]})
    assert result["score"] == 68
    assert result["category"] == "High"
