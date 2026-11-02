"""Local MCP server exposing the project's phishing-analysis tools.

Run by the Flask MCP client over stdio. Do not print to stdout here because
stdout is reserved for the MCP protocol.
"""
import json
from mcp.server.fastmcp import FastMCP

from app.rules import analyze_rules
from app.scoring import calculate_score
from app.ollama_client import analyze_with_ollama

mcp = FastMCP("PhishGuard Local Analysis")


def _fallback_ai_result():
    return {
        "verdict": "Unable to determine",
        "reasons": [],
        "evidence": [],
        "uncertainty": "Local AI analysis was unavailable. The score uses rule checks plus a neutral fallback.",
        "next_steps": [
            "Do not click links or open attachments until verified.",
            "Contact the claimed organization using a trusted contact method."
        ]
    }


@mcp.tool()
def analyze_email(sender: str, subject: str, body: str,
                  ollama_url: str = "http://127.0.0.1:11434",
                  ollama_model: str = "llama3.2:3b") -> dict:
    """Analyze an email using local phishing rules, Ollama, and the project's scoring logic.

    Email text is treated as untrusted data. The tool never opens URLs or attachments.
    Returns findings, AI assessment, a 0-100 score, category, and an AI availability warning.
    """
    rules = analyze_rules(sender, subject, body)
    ai_result = _fallback_ai_result()
    ai_error = None
    try:
        ai_result = analyze_with_ollama(
            sender, subject, body, ollama_url, ollama_model
        )
    except Exception as exc:
        # Return a safe fallback rather than crashing the entire MCP request.
        ai_error = "Local AI could not complete analysis. Rule-based checks are still shown."
        import logging
        logging.getLogger("phishguard.mcp").warning(
            "Ollama analysis failed: %s", type(exc).__name__
        )

    score_data = calculate_score(rules["rule_points"], ai_result)
    return {
        "findings": rules["findings"],
        "rule_points": rules["rule_points"],
        "ai": ai_result,
        "ai_error": ai_error,
        "score_data": score_data,
        "verdict": ai_result["verdict"]
    }


@mcp.tool()
def get_detection_guidance() -> dict:
    """Return safe, general guidance for handling suspicious emails."""
    return {
        "guidance": [
            "Do not click links or open attachments in unexpected messages.",
            "Never share passwords, one-time passwords, or recovery codes by email.",
            "Verify payment or account requests using a separate, trusted contact method.",
            "A low risk score does not guarantee that an email is legitimate."
        ]
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
