PhishGuardLOCAL — AI Evidence Reliability Patch

Purpose
- Tightens the Ollama prompt to prohibit unsupported sender-authenticity claims and invented facts.
- Requires AI evidence to be copied verbatim from the submitted sender, subject, or body.
- Filters evidence excerpts that do not occur in the submitted email fields.
- Uses a 90-second Ollama request timeout to reduce timeouts on slower local machines.
- Adds focused unit tests for evidence filtering and confidence clamping.

Files in this patch
- app/ollama_client.py
- tests/test_ollama_client.py

Apply on Windows
1. Stop Flask with Ctrl+C.
2. Make a backup copy of your current app/ollama_client.py.
3. Extract this ZIP into the project root (the folder containing run.py), keeping folder paths.
   Allow it to replace app/ollama_client.py.
4. From the activated project virtual environment, run:
       python -m pytest -q
5. Start the app again:
       python run.py
6. Repeat the delivery-fee test and prize-scam test. Compare the AI evidence to the exact
   sender, subject, and body you submitted.

Notes
- This patch does not verify domain ownership or independently validate sender identity.
- Evidence that is not an exact excerpt from the input is removed from the AI evidence list.
  AI reasons remain model-generated interpretations, so review them cautiously.
- If tests fail because pytest is not installed, run: python -m pip install pytest
