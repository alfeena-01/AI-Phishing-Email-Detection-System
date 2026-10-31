# Part B — Student Questions and Viva Preparation

These are simple model answers to explain the project. Adjust them to match what you actually run and test; do not claim unverified test results.

## Q1. Problem definition

Phishing is a type of social engineering in which an attacker sends a message designed to trick someone into revealing information, paying money, or visiting a harmful website. This project helps a student or user review an email for warning signs. The user enters the sender, subject and body. The system combines transparent rules with a locally running Ollama model, produces a risk score and explanation, and saves a report locally. Its limitations are that rules may miss new attack styles, the AI may misunderstand context, and a low score cannot prove an email is safe. It does not inspect attachments or verify a website's real reputation.

## Q2. Architecture

The frontend is the HTML/CSS dashboard where users enter emails and read results. Flask validates input, coordinates the analysis and handles history/export routes. The MCP client connects Flask to the MCP server. The MCP server exposes tools and calls the rule engine, Ollama and scoring function. The rule engine finds known patterns deterministically. Ollama gives a contextual language assessment. The scoring function combines rule points and the AI verdict into a bounded 0–100 score. SQLite stores scan history. The MCP layer standardizes tool calls; it does not detect phishing on its own.

## Q3. Ollama integration

The app checks Ollama's local `/api/tags` endpoint to see whether the service responds and which models are available. It sends a prompt to `/api/generate` with the selected model and a timeout. The response is expected to contain JSON fields such as verdict, reasons, evidence, confidence, uncertainty and next steps. The code checks the verdict and validates that list fields are lists. If Ollama is unavailable or its response is invalid, the application should show a useful warning and rely on the rule-based fallback. During the demonstration, show the actual local model and the warning behavior when Ollama is stopped.

## Q4. Detection logic

The project checks at least these six indicator groups:

1. Link present: a link is not proof of phishing; it prompts caution. Example: `Please read the meeting notes at https://example.com/notes`.
2. Suspicious URL format: IP-address host, `xn--` internationalized-domain marker or unusually deep subdomain. Example: `http://192.0.2.10/login` (a documentation-only example address).
3. Urgency/threat: phrases such as “account suspended” or “act now”. Example: “Your account will be closed within 24 hours.”
4. Credential request: references to password, OTP or verification code. Example: “Reply with your one-time password.”
5. Payment request: phrases such as gift card, wire transfer or bank details. Example: “Send the overdue payment using gift cards.”
6. Possible sender mismatch: a free email domain paired with an organization claim. Example: `payroll-team@gmail.com` claiming to represent a company's payroll department.

Each category is added once per message rather than once per matching word, and total rule points are capped at 60. Link presence and suspicious URL format are separate because they represent different observations, but both should be described as warning signs rather than proof. Tests should cover both positive and negative examples.

## Q5. Risk score

The current example gives rules up to 60 points and the AI assessment up to 40 points. The rule score is the sum of configured indicator points, capped at 60. The AI contribution depends on the verdict: likely phishing starts at 32, suspicious at 22, likely legitimate at 0, and unable to determine at 10; suspicious verdicts with reasons can receive a small additional contribution, capped at 40. The total is clamped to 0–100. Categories are Low 0–24, Medium 25–49, High 50–74 and Critical 75–100.

Worked example: suspicious URL (22) + urgency (12) + credential request (20) = 54 rule points. If Ollama returns “Suspicious” with reasons, the AI contribution is 22 plus up to 8 extra points; with two reasons it is 26. Final score = 54 + 26 = 80, Critical. This is an illustrative scoring rule, not a scientifically validated probability. The risk score measures configured warning signals; model confidence is the model's own estimate about its assessment. They are not interchangeable.

## Q6. Web dashboard

The user opens the Analyze page, enters sender, subject and body, and submits the form. The results page displays the combined score, category, AI verdict, rule findings with evidence, AI reasons, uncertainty and recommended actions. It also warns that the result is advisory. A JSON report can be downloaded. During the viva, use synthetic examples and explain why each signal contributed points.

## Q7. History and database

SQLite stores the scan timestamp, sender, subject, score, category, verdict, rule findings and AI summary in a `scans` table. The history page can search sender or subject, filter by risk category, open a previous result, delete one record or clear all records after confirmation. SQL parameters are used for user-provided query values. The database is local and ignored by Git. A user can delete stored records through the history page.

## Q8. Security and privacy

The app requires all three fields and enforces length limits on the server. Flask/Jinja escapes normal template output, and SQL values are parameterized. The email text is sent to the local Ollama service rather than a paid cloud AI API, but local processing does not make the machine or database automatically secure. The app should not log email content, and the user should avoid entering real secrets or personal information. It never automatically opens URLs, downloads attachments or sends emails. Unexpected requests should be verified using a separate trusted channel. Before production use, add CSRF protection and more complete error handling if not already present.

## Q9. Testing

Unit tests check rule indicators and score boundaries. Route tests mock the AI/MCP result so tests do not depend on a running Ollama model. Before submission, also run tests for suspicious, likely legitimate and ambiguous messages; blank/malformed fields; oversized bodies; Ollama unavailable; invalid JSON/unsupported verdict; database failures; and MCP failures. Record the actual result of `pytest -q`; do not invent a passing result. The current small test suite is a starting point and does not cover every required case yet.

## Q10. GitHub delivery

I will create a repository named `ai-phishing-email-detector`, include the app, tests, requirements, `.env.example`, README, architecture guide and screenshots, and exclude the virtual environment, caches, local database and secrets. I will test the fresh setup, commit with meaningful messages, push the repository and share its URL with the instructor/group. I will never commit API keys, passwords or real email samples.

## Q11. Demonstration

I will create and activate a virtual environment, install `requirements.txt`, pull `llama3.2:3b` with Ollama, start the app using `python run.py`, and open `http://127.0.0.1:5000`. I will scan a synthetic suspicious email and a benign-looking example, explain their evidence and score, show the history and JSON export, and run `pytest -q`. I will also explain how to check Ollama status and what happens if Ollama or MCP is unavailable. I should verify the MCP path succeeds before presenting it as demonstrated.

## Q12. Reflection

Two key limitations are false positives (a legitimate email contains urgent language or a link) and false negatives (a carefully written phishing email has none of the configured patterns). Ollama can also misinterpret content. Three realistic improvements are adding a broader labelled test dataset and evaluating precision/recall, improving URL/domain analysis without opening links, and adding an authenticated multi-user dashboard or an email gateway integration only after a security review. Other useful improvements include plain-text export, CSRF protection, and clearer model confidence calibration.
