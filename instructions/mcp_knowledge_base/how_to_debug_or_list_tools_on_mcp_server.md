# how_to_debug_or_list_tools_on_mcp_server

This guide explains how to print out, list, or debug the tools available on an MCP server. It covers both OpenAI Agents SDK and MCP Python SDK patterns, with code examples and best practices.

---

## 1. Using OpenAI Agents SDK (`MCPServerStdio`)

### Example: List Tools on a Server

```python
from agents.mcp import MCPServerStdio

params = {"command": "uv", "args": ["run", "accounts_server.py"]}

async with MCPServerStdio(params=params, client_session_timeout_seconds=30) as server:
    mcp_tools = await server.list_tools()
    print(mcp_tools)
```

- `mcp_tools` will be a list of available tools (with their names, descriptions, and schemas).
- You can inspect, print, or debug this list as needed.

---

## 2. Using MCP Python SDK (`stdio_client` and `ClientSession`)

### Example: List Tools

```python
import mcp
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters

params = StdioServerParameters(command="uv", args=["run", "accounts_server.py"], env=None)

async with stdio_client(params) as streams:
    async with mcp.ClientSession(*streams) as session:
        await session.initialize()
        tools_result = await session.list_tools()
        print(tools_result.tools)
```

---

## 3. Counting Tools Across Multiple Servers

```python
all_params = trader_mcp_server_params + researcher_mcp_server_params("ed")
count = 0
for each_params in all_params:
    async with MCPServerStdio(params=each_params, client_session_timeout_seconds=60) as server:
        mcp_tools = await server.list_tools()
        count += len(mcp_tools)
print(f"We have {len(all_params)} MCP servers, and {count} tools")
```

---

## 4. Debugging Tips

- If you get errors about missing positional arguments, check your SDK version and see if you need to use `await server.session.list_tools()` instead.
- Always inspect the returned tool objects for name, description, and schema.
- Use pretty-printing (`import pprint; pprint.pprint(mcp_tools)`) for better readability.
- For troubleshooting, print tool details in a loop:

```python
for tool in mcp_tools:
    print(tool.name, tool.description, tool.inputSchema)
```

---

## Summary

- Use `await server.list_tools()` to get available tools on an MCP server.
- Print or inspect the result for debugging.
- Use loops and pretty-printing for detailed inspection.
- Check SDK version if you encounter errors.
