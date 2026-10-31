# Architecture (MCP-enabled version)

The web interface is a Flask application. It validates the sender, subject, and email body, then calls a local MCP client. The MCP client launches `mcp_server.py` as a separate local process and communicates with it using the MCP stdio transport.

The MCP server exposes `analyze_email`. That tool calls the project's existing rule engine, asks the locally installed Ollama model for a structured assessment when available, and uses the existing scoring function to produce the risk score and category. The tool returns findings, the AI assessment, the score, and any AI availability warning to Flask. Flask stores the result in SQLite and renders the result page.

The MCP server also exposes `get_detection_guidance`, which returns safe general advice for handling suspicious messages. The tools do not open URLs or attachments. Email content is treated as untrusted data.

SQLite history, filtering, deletion, and JSON export remain handled by the Flask application's existing database layer. This avoids maintaining two competing database implementations. MCP is used for the analysis-tool boundary; it does not itself detect phishing or guarantee that a result is correct.

## Data flow

1. User submits an email in the Flask dashboard.
2. Flask validates the input.
3. Flask MCP client starts the local MCP server and calls `analyze_email`.
4. MCP tool runs the rule engine, optional Ollama analysis, and scoring function.
5. MCP returns a structured result to Flask.
6. Flask stores the result in SQLite and displays it.

If the MCP process cannot start, the Flask route logs the issue and uses a local fallback so the dashboard can remain usable. For a submission or demonstration, verify the MCP path works and review the application logs; the fallback is for resilience, not proof that MCP was used.
