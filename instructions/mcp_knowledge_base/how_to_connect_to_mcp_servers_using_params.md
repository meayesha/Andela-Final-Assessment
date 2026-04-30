# how_to_connect_to_mcp_servers_using_params

This guide explains multiple ways to connect to MCP servers using parameter dictionaries, including both the OpenAI Agents SDK and the lower-level MCP Python SDK. It also lists requirements and dependencies for each approach, and now includes how to connect to remote/online MCP servers (e.g., Smithery, hosted MCPs).

## 1. Using OpenAI Agents SDK (`MCPServerStdio`)

This is the recommended way when working with OpenAI Agents and toolchains.

### Required Imports

```python
from contextlib import AsyncExitStack
from agents.mcp import MCPServerStdio
```

### Example Code (with context manager)

```python
async with AsyncExitStack() as stack:
    mcp_servers = [
        await stack.enter_async_context(
            MCPServerStdio(params, client_session_timeout_seconds=120)
        )
        for params in mcp_server_params
    ]
    # Use mcp_servers with your agents
```

### Example Code (direct instantiation)

This pattern is common in notebooks and scripts for quick experimentation:

```python
researcher_mcp_servers = [MCPServerStdio(params, client_session_timeout_seconds=30) for params in researcher_mcp_server_params]
trader_mcp_servers = [MCPServerStdio(params, client_session_timeout_seconds=30) for params in trader_mcp_server_params]
mcp_servers = trader_mcp_servers + researcher_mcp_servers
```

Note: For production or long-running code, prefer using async context managers to ensure proper resource cleanup.

### Dependencies

- `openai-agents`
- `mcp`
- `asyncio`
- MCP servers must be available (locally, network, or remote)
- Any required environment variables (API keys, etc)

---

## 2. Using MCP Python SDK (`stdio_client` and `ClientSession`)

This is a lower-level, direct way to connect to MCP servers, useful for custom clients or scripts.

### Required Imports

```python
import mcp
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters
```

### Example Code

```python
params = StdioServerParameters(command="uv", args=["run", "accounts_server.py"], env=None)
async with stdio_client(params) as streams:
    async with mcp.ClientSession(*streams) as session:
        await session.initialize()
        # Now you can call tools, read resources, etc.
```

### Dependencies

- `mcp`
- MCP servers must be available
- Any required environment variables

---

## 3. Connecting to Remote/Online MCP Servers (e.g., Smithery, Hosted MCPs)

You can connect to remote MCP servers using the same patterns as local servers, but the `params` dictionary must specify the remote server's identifier or endpoint. For Smithery and similar platforms, you typically use a string identifier for the remote server.

### Example: Connecting to a Smithery Remote MCP Server

```python
remote_params = {"server": "smithery/exa"}  # Replace 'exa' with the desired remote MCP server slug
async with MCPServerStdio(params=remote_params, client_session_timeout_seconds=60) as server:
    tools = await server.list_tools()
    # Use tools as needed
```

#### Instructions

1. Find the remote MCP server slug (e.g., `smithery/exa`, `smithery/gmail`, `smithery/notion`) from <https://smithery.ai/servers>.
2. Use the slug in the `params` dictionary as `{ "server": "smithery/<slug>" }`.
3. Use `MCPServerStdio` as shown above to connect and interact with the remote server.
4. If authentication is required, follow the Smithery or provider instructions to authorize your agent (see <https://smithery.ai/docs/use> and <https://smithery.ai/docs/build> for details).
5. You can list tools, call tools, and use the remote MCP server just like a local one.

#### Example: Connecting to Brave Search MCP on Smithery

```python
remote_params = {"server": "smithery/brave"}
async with MCPServerStdio(params=remote_params, client_session_timeout_seconds=60) as server:
    brave_tools = await server.list_tools()
    print(brave_tools)
```

#### Notes

- The connection pattern is the same as for local servers, but the `params` dictionary uses the remote server slug.
- For advanced usage, see Smithery's CLI and documentation for managing authentication and connections.
- You can mix local and remote MCP servers in your agent's `mcp_servers` list.

---

## 4. Running MCP Servers Directly (for testing or local use)

You can also run MCP servers directly as scripts, e.g.:

```sh
python accounts_server.py
python market_server.py
python push_server.py
```

Or using uv:

```sh
uv run accounts_server.py
```

---

## Notes

- Choose the approach that fits your use case: use MCPServerStdio for agent workflows, stdio_client/ClientSession for direct access, or run servers directly for testing.
- For remote MCP servers, use the server slug in the params dictionary.
- Always ensure all dependencies and environment variables are set up.
- For more, see the OpenAI Agents SDK, MCP Python SDK, and Smithery documentation.
