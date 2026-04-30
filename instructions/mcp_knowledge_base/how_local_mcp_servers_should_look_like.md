# how_local_mcp_servers_should_look_like

This guide describes how to implement local MCP servers for use with MCPServerStdio, stdio_client, or direct execution. It covers best practices, required structure, and example code for typical local MCP servers. For deploying MCP servers to Vercel (or other cloud platforms), see the deployment_knowledge_base/how_to_deploy_mcp_servers_to_vercel.md guide.

## General Structure

- Use `FastMCP` from `mcp.server.fastmcp` to define your server.
- Register tools using the `@mcp.tool()` decorator.
- Place server startup logic under `if __name__ == "__main__":` and call `mcp.run(transport="stdio")`.
- Load environment variables if needed (e.g., with `dotenv`).
- Use Pydantic models for structured tool arguments if appropriate.
- For HTTP-based deployment (e.g., Vercel), expose a FastAPI/Flask app as your entry point. See deployment_knowledge_base/how_to_deploy_mcp_servers_to_vercel.md for details.

---

## Example: Accounts MCP Server

```python
from mcp.server.fastmcp import FastMCP
from accounts import Account

mcp = FastMCP("accounts_server")

@mcp.tool()
async def get_balance(name: str) -> float:
    return Account.get(name).balance

@mcp.tool()
async def get_holdings(name: str) -> dict[str, int]:
    return Account.get(name).holdings

@mcp.tool()
async def buy_shares(name: str, symbol: str, quantity: int, rationale: str) -> float:
    return Account.get(name).buy_shares(symbol, quantity, rationale)

@mcp.tool()
async def sell_shares(name: str, symbol: str, quantity: int, rationale: str) -> float:
    return Account.get(name).sell_shares(symbol, quantity, rationale)

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

---

## Example: Market MCP Server

```python
from mcp.server.fastmcp import FastMCP
from market import get_share_price

mcp = FastMCP("market_server")

@mcp.tool()
async def lookup_share_price(symbol: str) -> float:
    return get_share_price(symbol)

if __name__ == "__main__":
    mcp.run(transport='stdio')
```

---

## Deploying to Vercel or Cloud
- For HTTP-based deployment (e.g., Vercel), see deployment_knowledge_base/how_to_deploy_mcp_servers_to_vercel.md for a step-by-step guide.
- Ensure your MCP server exposes a FastAPI/Flask app as the entry point for Vercel compatibility.
- For other deployment types, see additional guides in deployment_knowledge_base.

---

## Best Practices

- Always use `if __name__ == "__main__":` for server startup.
- Use `transport="stdio"` for compatibility with MCP clients.
- Register all tools with clear docstrings and type annotations.
- Use environment variables for secrets and API keys.
- Use Pydantic models for complex tool arguments.
- Keep server logic modular and testable.

---

## Summary

A local MCP server should:

- Use FastMCP
- Register tools with `@mcp.tool()`
- Start with `mcp.run(transport="stdio")`
- Load environment variables as needed
- Use Pydantic for structured arguments
- Be modular and well-documented
