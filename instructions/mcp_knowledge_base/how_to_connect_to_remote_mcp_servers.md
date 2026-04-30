
## 8. Connecting to Remote MCP Servers via SSE in FastAPI & OpenAI Agents SDK

You can connect to remote MCP servers using SSE (Server-Sent Events) in a FastAPI application and register that connection with the OpenAI Agents SDK. This is useful for integrating remote toolboxes into agent-powered APIs and chatbots.

### Required Libraries

- `fastapi`
- `mcp`
- `openai-agents`

Install with:

```sh
pip install fastapi mcp openai-agents
```

### A. Connecting to a Remote MCP Server in FastAPI (SSE)

```python
from fastapi import FastAPI
from mcp import ClientSession
from mcp.client.sse import sse_client
from contextlib import asynccontextmanager

REMOTE_MCP_URL = "https://your-remote-mcp-server.com/sse"

@asynccontextmanager
async def lifespan(app: FastAPI):
  async with sse_client(REMOTE_MCP_URL) as (read, write):
    async with ClientSession(read, write) as session:
      await session.initialize()
      app.state.mcp_session = session
      yield

app = FastAPI(lifespan=lifespan)
```

---

### B. Passing MCP Tools to OpenAI Agents SDK

#### Method 1: Using MCPServerStreamableHttp (Recommended)

```python
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp

@app.get("/ask-agent")
async def ask_agent(query: str):
  remote_server = MCPServerStreamableHttp(
    name="RemoteToolbox",
    params={
      "url": "https://your-remote-mcp-server.com/sse",
      "headers": {"Authorization": "Bearer YOUR_TOKEN"}
    }
  )

  agent = Agent(
    name="Assistant",
    instructions="Use the tools from the RemoteToolbox to answer questions.",
    mcp_servers=[remote_server]
  )

  result = await Runner.run(agent, query)
  return {"response": result.final_output}
```

#### Method 2: Using HostedMCPTool

```python
from agents.tool import HostedMCPTool

mcp_tool = HostedMCPTool(
  url="https://mcp.provider.com/tools",
  api_key="your-api-key"
)

agent = Agent(
  name="Specialized Agent",
  tools=[mcp_tool]
)
```

---

### Key Integration Differences

| Feature      | mcp Client (Manual)         | OpenAI Agents SDK (mcp_servers) |
| ------------ | --------------------------- | ------------------------------- |
| Best For     | Custom logic outside LLM    | Seamless "Agent-to-Tool"        |
| Tool Loading | Manual session.list_tools() | Automatic discovery             |
| Execution    | Manual session.call_tool()  | Managed by Agent reasoning loop |
| Transports   | sse_client or stdio_client  | MCPServerStreamableHttp         |

---

### Best Practices

- Use async context managers for all connections.
- Store credentials in environment variables or `.env` files.
- For authentication, see `how_to_handle_authentication_for_remote_mcp_servers.md`.
- For error handling, see `how_to_handle_errors_when_connecting_to_or_using_mcp_servers.md`.

---

### Troubleshooting

- Ensure all required libraries are installed and up to date.
- Check server and FastAPI logs for errors if connection fails.
- For Smithery, consult <https://smithery.ai/docs/use> for the latest instructions.

# How to Connect to Remote MCP Servers (Python, Node.js, HTTP, Smithery, etc.)

This guide explains how to connect to remote MCP servers of different types and protocols, including Python (stdio), Node.js (npx), HTTP, and Smithery-managed servers. It lists required libraries and provides code snippets consistent with MCP knowledge base conventions.

---

## 1. Required Libraries

- **Python stdio MCP servers:**
  - `mcp-server-stdio` (install with `pip install mcp-server-stdio` or `uv pip install mcp-server-stdio`)
- **Node.js MCP servers:**
  - `npx` (comes with Node.js)
- **Model Context Protocol utilities:**
  - `modelcontextprotocol` (install with `pip install modelcontextprotocol` or `uv pip install modelcontextprotocol`)
- **Smithery (managed MCPs):**
  - Smithery CLI (`npm install -g @smithery/cli`)

---

## 2. Connecting to Python stdio MCP Servers

```python
from agents.mcp import MCPServerStdio

params = {"command": "uvx", "args": ["mcp-server-stdio"]}
async with MCPServerStdio(params, client_session_timeout_seconds=60) as server:
    tools = await server.list_tools()
```

---

## 3. Connecting to Node.js MCP Servers

```python
from agents.mcp import MCPServerStdio

params = {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/sandbox"]}
async with MCPServerStdio(params, client_session_timeout_seconds=60) as server:
    tools = await server.list_tools()
```

---

## 4. Connecting to HTTP MCP Servers

Some MCP servers expose an HTTP API. Use `httpx` or `requests` to interact with them, or use a compatible MCP client if available.

```python
import httpx

response = httpx.post("https://your-mcp-server.com/tool", json={"input": "..."})
print(response.json())
```

---

## 5. Connecting to Smithery-Managed MCP Servers

1. **Install Smithery CLI:**

   ```sh
   npm install -g @smithery/cli
   smithery auth login
   smithery mcp add <server-slug>
   smithery tool list
   ```

2. **Connect from Python:**

   ```python
   from agents.mcp import MCPServerStdio
   params = {"server": "smithery/<slug>"}
   async with MCPServerStdio(params, client_session_timeout_seconds=60) as server:
       tools = await server.list_tools()
   ```

---

## 6. Best Practices

- Always use async context managers for resource cleanup.
- Store credentials (API keys, tokens) in environment variables or `.env` files.
- For authentication, see `how_to_handle_authentication_for_remote_mcp_servers.md`.
- For error handling, see `how_to_handle_errors_when_connecting_to_or_using_mcp_servers.md`.

---

## 7. Troubleshooting

- Ensure all required libraries are installed and up to date.
- Check server logs for errors if connection fails.
- For Smithery, consult <https://smithery.ai/docs/use> for the latest instructions.
