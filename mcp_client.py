"""Small synchronous bridge from Flask routes to the local MCP server."""
import asyncio
import json
import sys
from pathlib import Path

SERVER_PATH = Path(__file__).resolve().with_name("mcp_server.py")


async def _call_tool(tool_name: str, arguments: dict):
    # Import lazily so the web app and its fallback can still start before dependencies are installed.
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    params = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_PATH)],
        env=None,
    )
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments=arguments)
            if result.isError:
                raise RuntimeError(f"MCP tool failed: {tool_name}")
            # FastMCP tools return JSON-compatible dictionaries as text content
            # in SDK v1. Also support structuredContent if provided by the SDK.
            structured = getattr(result, "structuredContent", None)
            if isinstance(structured, dict):
                return structured
            for item in result.content:
                item_text = getattr(item, "text", None)
                if item_text:
                    try:
                        parsed = json.loads(item_text)
                        if isinstance(parsed, dict):
                            return parsed
                    except json.JSONDecodeError:
                        continue
            raise ValueError(f"MCP tool {tool_name} returned no JSON object")


def call_mcp_tool(tool_name: str, arguments: dict):
    """Call one MCP tool from a synchronous Flask request handler."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(_call_tool(tool_name, arguments))
    # Flask's normal WSGI request handlers do not have a running event loop.
    # If called from an async context, use a dedicated thread for the loop.
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        return executor.submit(asyncio.run, _call_tool(tool_name, arguments)).result()
