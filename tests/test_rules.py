from app.rules import analyze_rules
from app.scoring import calculate_score


def test_urgent_credential_email_gets_signals():
    result = analyze_rules(
        "help@example.com",
        "Urgent: verify now",
        "Your account is suspended. Enter your password and OTP immediately."
    )
    ids = {x["id"] for x in result["findings"]}
    assert "urgency" in ids
    assert "credential_request" in ids
    assert result["rule_points"] > 0


def test_plain_email_no_signals():
    result = analyze_rules(
        "colleague@company.example",
        "Meeting notes",
        "Hello, attached are the notes from our meeting."
    )
    assert result["findings"] == []
    assert result["rule_points"] == 0


def test_prize_scam_email_gets_multiple_rule_signals():
    result = analyze_rules(
        "winner@free-reward-claim.example.com",
        "Congratulations! You Have Won ₹50,00,000",
        (
            "Your email address has been selected to receive a cash prize. "
            "Complete verification within the next 12 hours. Submit your "
            "personal information, bank account details, and identification documents. "
            "Claim your reward before it expires."
        )
    )
    ids = {item["id"] for item in result["findings"]}
    assert "urgency" in ids
    assert "sensitive_information_request" in ids
    assert "unexpected_prize_claim" in ids
    assert "suspicious_sender_domain" in ids
    assert result["rule_points"] >= 40


def test_paypal_lookalike_sender_domain_gets_signal():
    result = analyze_rules(
        "security-alert@paypa1-account-verify.com",
        "URGENT: Your PayPal Account Has Been Suspended!",
        "Verify your account immediately."
    )
    ids = {item["id"] for item in result["findings"]}
    assert "urgency" in ids
    assert "credential_request" in ids
    assert "suspicious_sender_domain" in ids


def test_score_category_is_bounded():
    result = calculate_score(
        60,
        {"verdict": "Likely phishing", "reasons": ["Urgency", "Credential request"]}
    )
    assert 0 <= result["score"] <= 100
    assert result["category"] in {"Low", "Medium", "High", "Critical"}
