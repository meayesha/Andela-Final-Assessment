"""Run the MCP server over stdio: python -m todo_mcp (from backend/ on PYTHONPATH)."""

from todo_mcp.server import mcp

if __name__ == "__main__":
    mcp.run(transport="stdio")
