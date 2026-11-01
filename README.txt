PhishGuardLOCAL — AI analysis logic patch

Files to copy into the matching folders of your existing project:
- app/ollama_client.py: stronger balanced prompt to reduce false positives and require relevant, source-backed evidence.
- app/scoring.py: removes the extra score bonus for the number of AI reasons; reduces the AI-only suspicious adjustment.
- tests/test_scoring_ai_logic.py: tests for the updated scoring behavior.

Backup app/ollama_client.py and app/scoring.py before replacing them. Do not replace the entire project or database.

After copying, run from the project root:
  python -m pytest -q

Expected scoring changes: a Suspicious AI verdict with zero rule points now contributes 12 points rather than 22–30; Likely legitimate with zero rule points contributes 0. Concrete rule signals remain important. This is a conservative heuristic, not a validated security standard. Re-test representative emails after applying.
