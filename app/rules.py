import re
from urllib.parse import urlparse

URGENT_TERMS = [
    "urgent", "immediately", "act now", "within 24 hours", "within 12 hours",
    "within the next 12 hours", "next 12 hours", "account suspended",
    "account will be closed", "final warning", "verify now", "limited time",
    "before your reward expires", "before it expires", "expires soon"
]
CREDENTIAL_TERMS = [
    "password", "one-time password", "otp", "login credentials", "security code",
    "confirm your identity", "verify your account"
]
PAYMENT_TERMS = [
    "wire transfer", "gift card", "payment overdue", "bank details",
    "send payment", "payment information", "payment required"
]
SENSITIVE_INFO_TERMS = [
    "personal information", "personal details", "identification documents",
    "identity documents", "bank account details", "banking details",
    "financial information", "submit your information"
]
PRIZE_TERMS = [
    "you have won", "you won", "cash prize", "prize money", "claim your prize",
    "claim your reward", "lucky winner", "selected to receive a prize",
    "reward expires", "prize expires"
]
SUSPICIOUS_DOMAIN_TERMS = [
    "verify", "claim", "reward", "account-alert", "secure-login",
    "paypa1", "micros0ft", "app1e"
]
URL_RE = re.compile(r"""(?i)\b(?:https?://|www\.)[^\s<>"']+""")
IP_HOST_RE = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")


def analyze_rules(sender, subject, body):
    text = f"{subject}\n{body}"
    lowered = text.lower()
    findings = []

    urls = URL_RE.findall(text)
    if urls:
        findings.append({
            "id": "links_present", "label": "Contains a link",
            "points": 8, "evidence": urls[:3],
            "explanation": "Links are not automatically malicious, but destinations should be checked carefully."
        })
    suspicious_urls = []
    for raw in urls:
        cleaned = raw.rstrip(".,);]")
        candidate = cleaned if cleaned.lower().startswith(("http://", "https://")) else "http://" + cleaned
        host = urlparse(candidate).hostname or ""
        if host and (IP_HOST_RE.match(host) or "xn--" in host.lower() or host.count(".") >= 4):
            suspicious_urls.append(cleaned)
    if suspicious_urls:
        findings.append({
            "id": "suspicious_url", "label": "Potentially suspicious URL format",
            "points": 22, "evidence": suspicious_urls[:3],
            "explanation": "An IP-address host, internationalized domain marker, or unusually deep subdomain can be a warning sign."
        })

    urgent = [term for term in URGENT_TERMS if term in lowered]
    if urgent:
        findings.append({
            "id": "urgency", "label": "Urgent or threatening language",
            "points": 12, "evidence": urgent[:4],
            "explanation": "Pressure to act quickly can be used to stop people from checking a message."
        })

    credentials = [term for term in CREDENTIAL_TERMS if term in lowered]
    if credentials:
        findings.append({
            "id": "credential_request", "label": "Account or credential language",
            "points": 20, "evidence": credentials[:4],
            "explanation": "Messages asking for passwords, OTPs, or account verification deserve extra caution."
        })

    payment = [term for term in PAYMENT_TERMS if term in lowered]
    if payment:
        findings.append({
            "id": "payment_request", "label": "Payment or financial request",
            "points": 16, "evidence": payment[:4],
            "explanation": "Unexpected payment or bank-detail requests should be verified through a trusted channel."
        })

    sensitive = [term for term in SENSITIVE_INFO_TERMS if term in lowered]
    if sensitive:
        findings.append({
            "id": "sensitive_information_request", "label": "Request for personal or financial information",
            "points": 16, "evidence": sensitive[:4],
            "explanation": "Requests for personal, identity, or banking information should be independently verified."
        })

    prize = [term for term in PRIZE_TERMS if term in lowered]
    if prize:
        findings.append({
            "id": "unexpected_prize_claim", "label": "Unexpected prize or reward claim",
            "points": 12, "evidence": prize[:4],
            "explanation": "Unexpected prize claims that ask for information or urgent action are a common scam pattern."
        })

    sender_match = re.search(r"<([^>]+)>", sender or "")
    sender_address = sender_match.group(1) if sender_match else (sender or "")
    sender_domain = sender_address.split("@")[-1].strip(" >").lower() if "@" in sender_address else ""
    domain_labels = sender_domain.split(".")
    domain_signal_terms = [term for term in SUSPICIOUS_DOMAIN_TERMS if term in sender_domain]
    if sender_domain and domain_signal_terms:
        findings.append({
            "id": "suspicious_sender_domain", "label": "Sender domain contains suspicious wording",
            "points": 12, "evidence": [sender_domain],
            "explanation": "Words such as claim, reward, or verify in a sender domain can be suspicious in context; this is a warning signal, not proof."
        })
    elif sender_domain and any(x in sender_domain for x in ["gmail.com", "outlook.com", "yahoo.com"]):
        organization_words = ["payroll", "security team", "it department", "your bank", "microsoft", "google"]
        if any(word in lowered for word in organization_words):
            findings.append({
                "id": "possible_sender_mismatch", "label": "Possible sender / organization mismatch",
                "points": 12, "evidence": [sender_domain],
                "explanation": "A free email domain paired with an organization claim may need verification; this is only a weak signal."
            })

    # Each rule contributes once, even when multiple phrases match it.
    # The total rule contribution is capped at 60 to preserve the 60/40 split.
    rule_points = min(60, sum(f["points"] for f in findings))
    return {"findings": findings, "rule_points": rule_points}
