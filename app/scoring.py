"""Conservative score combining rule evidence with the AI's cautious verdict."""


def calculate_score(rule_points, ai_result):
    """Calculate a bounded advisory score.

    AI reasons are not counted as extra risk points: a small local model can produce
    several weak or repetitive explanations, which previously inflated false positives.
    Concrete rule signals carry most of the score; AI verdict adds a limited adjustment.
    """
    try:
        rules = max(0, min(60, int(rule_points)))
    except (TypeError, ValueError):
        rules = 0

    verdict = (ai_result or {}).get("verdict", "Unable to determine")
    ai_points = {
        "Likely phishing": 28,
        "Suspicious": 12,
        "Likely legitimate": 0,
        "Unable to determine": 6,
    }.get(verdict, 6)

    score = max(0, min(100, rules + ai_points))
    if score <= 24:
        category = "Low"
    elif score <= 49:
        category = "Medium"
    elif score <= 74:
        category = "High"
    else:
        category = "Critical"

    if category in ("High", "Critical") or verdict == "Likely phishing":
        summary = "Treat this email as suspicious and verify it using a separate trusted channel."
    elif category == "Medium" or verdict == "Suspicious":
        summary = "Check the sender and any requests carefully before taking action."
    else:
        summary = "No strong warning was found, but this result cannot guarantee the email is safe."

    return {"score": score, "category": category, "summary": summary, "ai_points": ai_points}
