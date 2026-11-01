import json
from app import create_app

class FakeResponse:
    def raise_for_status(self): pass
    def json(self):
        return {"response": json.dumps({
            "verdict": "Suspicious", "reasons": ["Urgent language"],
            "evidence": ["act now"], "confidence": 0.72, "uncertainty": "Could be legitimate.",
            "next_steps": ["Verify with the sender through a known contact method."]
        })}

def test_home_and_analysis(monkeypatch, tmp_path):
    import app.routes as routes
    monkeypatch.setattr(routes, "check_ollama", lambda *a, **k: {"available": True, "models": ["llama3.2:3b"]})
    monkeypatch.setattr(routes, "call_mcp_tool", lambda tool, args: {
        "findings": [{"id": "urgency", "label": "Urgent language", "points": 12,
                      "evidence": ["act now"], "explanation": "Pressure can be suspicious."}],
        "rule_points": 12,
        "ai": {"verdict": "Suspicious", "reasons": ["Urgent language"],
               "evidence": ["act now"], "confidence": 0.72, "uncertainty": "Could be legitimate.",
               "next_steps": ["Verify through a known contact."]},
        "ai_error": None,
        "score_data": {"score": 34, "category": "Medium", "summary": "Check the sender carefully.", "ai_points": 22},
        "verdict": "Suspicious"
    })
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.sqlite3")})
    client = app.test_client()
    assert client.get("/").status_code == 200
    response = client.post("/analyze", data={
        "sender": "security@example.com", "subject": "Act now",
        "body": "Please verify your account immediately."
    })
    assert response.status_code == 200
    assert b"Scan results" in response.data
    assert client.get("/history").status_code == 200

def test_missing_fields_rejected(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test2.sqlite3")})
    response = app.test_client().post("/analyze", data={"sender": "", "subject": "", "body": ""}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Please fill in" in response.data


def test_dashboard_statistics_are_read_from_database(tmp_path, monkeypatch):
    import app.routes as routes
    monkeypatch.setattr(routes, "check_ollama", lambda *a, **k: {"available": True, "models": ["llama3.2:3b"]})
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "stats.sqlite3")})
    client = app.test_client()
    with app.app_context():
        from app.db import get_db
        db = get_db()
        db.executemany(
            "INSERT INTO scans (sender, subject, score, category, verdict, findings_json, ai_summary) VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                ("a@example.test", "Test phishing", 88, "Critical", "Likely phishing", "{}", "test"),
                ("b@example.test", "Test suspicious", 60, "High", "Suspicious", "{}", "test"),
                ("c@example.test", "Test normal", 4, "Low", "Likely legitimate", "{}", "test"),
            ],
        )
        db.commit()
    response = client.get("/")
    assert response.status_code == 200
    assert b'>3</div><div class="stat-label">Total scans</div>' in response.data
    assert b'>1</div><div class="stat-label">Likely phishing</div>' in response.data
    assert b'>1</div><div class="stat-label">Suspicious emails</div>' in response.data
    assert b'>2</div><div class="stat-label">High-risk scans</div>' in response.data
