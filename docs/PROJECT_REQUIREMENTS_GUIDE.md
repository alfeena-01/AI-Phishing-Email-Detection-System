# Project Requirements and Completion Guide (Parts A, C and D)

This guide maps the student brief to the current MCP-enabled project. It is deliberately honest about what is implemented and what still needs to be verified or added before submission.

## Part A — Functional requirements

### Email analysis form
The dashboard asks for sender, subject and body. Flask trims whitespace, requires all three fields and rejects a body longer than 12,000 characters. The HTML form also has length limits. The server remains the authority for validation; browser limits alone are not security controls.

### Ollama integration
`app/ollama_client.py` checks the local Ollama `/api/tags` endpoint, sends an email-analysis prompt to `/api/generate`, sets a request timeout, and validates the returned JSON and allowed verdict. The AI response contains reasons, evidence, confidence, uncertainty and next steps. Confidence is displayed separately from the final risk score and is not treated as proof of correctness. Ollama is optional for rule-only fallback, but the final demonstration should show the configured model running locally.

### Rule-based checks
`app/rules.py` includes indicators for links, potentially suspicious URL formats (IP-address hosts, internationalized-domain marker, unusually deep subdomains), urgency/threatening language, credential/account-verification language, payment requests and possible sender/organization mismatch. Each indicator group is emitted once per email, with a points value, evidence and explanation. The overall rule contribution is capped at 60. Link presence and suspicious URL format are separate signals: one means a link exists; the other means the URL format matches a configured warning pattern. Neither proves maliciousness.

### AI and risk scoring
`app/scoring.py` caps rule points at 60 and assigns up to 40 points based on the AI verdict and whether the AI provides reasons. The final score is clamped to 0–100. Categories are Low (0–24), Medium (25–49), High (50–74) and Critical (75–100). These are illustrative project thresholds, not a validated security standard. The AI's self-reported confidence is displayed separately and does not change the risk score.

### Dashboard and reports
The project has a new-scan form, results page with score/category/verdict/rule evidence/AI reasons/uncertainty/next steps, and a visible advisory warning. The submit button changes to a waiting label during a request. JSON report download is implemented. A separate plain-text export is not currently implemented; JSON satisfies the brief's “text/JSON” alternative only if the instructor accepts JSON, otherwise add text export.

### History and database
`app/db.py` creates a SQLite `scans` table. `app/routes.py` stores sender, subject, timestamp, score, category, verdict, rule findings and AI summary. The history page supports searching sender/subject, filtering by category, opening a saved result, deleting one record and clearing all records with a confirmation prompt. SQL values use parameterized queries. The database is stored under `instance/` and excluded from Git.

### Tests and docs
The current test files cover core rule signals, a clean example, score boundaries, a mocked analysis route and missing form fields. This is not yet the complete test matrix required by the brief. Before submission, add/run tests for ambiguous email, malformed fields, oversized input, Ollama unavailable, invalid model JSON, database errors and MCP server failure. Save actual screenshots after running the project on your machine.

## Part C — How the tool works

1. The user submits a sender, subject and body in the Flask dashboard.
2. Flask trims and validates the input.
3. `mcp_client.py` launches `mcp_server.py` as a subprocess and establishes a local MCP stdio session.
4. The MCP `analyze_email` tool calls the rule engine and the local Ollama analysis function, then calls the scoring function.
5. The MCP server returns structured findings, AI assessment, score and category to Flask.
6. Flask stores the result in SQLite and renders the result page.
7. The user can revisit history, search/filter it, delete records or download a JSON report.

The tool never automatically opens links, downloads attachments or sends emails. If MCP fails, the Flask route attempts a logged fallback path. For a viva, show that a successful MCP call is actually happening; do not describe a fallback result as proof of MCP operation.

## Part D — Installation, testing and GitHub checklist

### Fresh setup on Windows

1. Install Python 3.11 or newer.
2. Install Ollama from its official website if AI analysis is required.
3. Open PowerShell in the project directory.
4. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   ```

5. Install packages:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

6. Pull the configured local model:

   ```powershell
   ollama pull llama3.2:3b
   ```

7. Start the app:

   ```powershell
   python run.py
   ```

8. Open `http://127.0.0.1:5000`.
9. In a second terminal, check the configured model with `ollama list`; use `/health` to inspect app and Ollama status.
10. Run tests:

   ```powershell
   pytest -q
   ```

The first model download can be large. Ollama and the model run locally, so no paid AI API key is required. Package/model downloads require internet access.

### Test cases to demonstrate

Use only synthetic examples. Record the expected and actual outcome in a test-results document.

- Clearly suspicious: an unexpected account suspension message asking for a password and directing the reader to an IP-address URL.
- Likely legitimate: a routine meeting follow-up with no link or credential/payment request.
- Ambiguous: a legitimate-looking notification with an ordinary link.
- Malformed: blank sender, subject or body.
- Oversized: body longer than 12,000 characters.
- Ollama unavailable: stop Ollama and confirm the UI shows an availability warning and rule-based fallback.
- Invalid model output: mock a response that is not valid JSON or has an unsupported verdict.
- Database failure: simulate a database write error and ensure the app gives a controlled error rather than exposing sensitive internals.
- MCP unavailable: simulate an MCP client exception and verify the documented fallback; separately verify the normal MCP path.

### GitHub delivery

1. Create a repository named `ai-phishing-email-detector` (or a similarly clear name).
2. Include source code, tests, README, `.env.example`, architecture documentation and screenshots.
3. Do not commit `.env`, real emails, credentials, local SQLite databases, `.venv`, `__pycache__` or `.pytest_cache`.
4. Review `.gitignore` before committing.
5. Use meaningful commits such as `Add local MCP analysis server` and `Add phishing rule tests`.
6. Push to GitHub, verify the repository opens correctly, and share its URL with the instructor/group. If private, invite the required people.
7. Only claim tests passed after running `pytest -q` locally and recording the actual output.

### Still required before submission

- Run the complete app from a fresh environment on your computer.
- Verify the MCP path succeeds and the fallback path is distinguishable in logs.
- Complete the missing tests listed above and record actual results.
- Capture real screenshots of the dashboard, a result, and scan history; place them in `docs/screenshots/` and reference them from README.
- If required by your instructor, add plain-text report export and stronger CSRF protection for state-changing forms.
- Review README/setup steps, then push the final project to GitHub.
