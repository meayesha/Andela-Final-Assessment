# how_to_compile_mcp_server_params

This guide explains how to compile MCP server parameters for use with agents in an OpenAI Agents + MCP project.

## How to "Coin" MCP Server Params

When you see code like:

```python
fetch_params = {"command": "uvx", "args": ["mcp-server-fetch"]}
playwright_params = {"command": "npx","args": [ "@playwright/mcp@latest"]}
sandbox_path = os.path.abspath(os.path.join(os.getcwd(), "sandbox"))
files_params = {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", sandbox_path]}
```

The writers of these code snippets aren't guessing; they are following the specific CLI (Command Line Interface) requirements of the tools they are trying to run.

To "coin" these parameters, you look at two things: the package manager rules and the MCP server's documentation.

### 1. The "Executor" (uvx vs. npx)

- **uvx (Python):** Use this when the MCP server is a Python package. `uvx` finds the package on PyPI, creates a temporary environment, and runs it immediately.
- **npx (Node.js/JavaScript):** Use this for JavaScript packages. `npx` downloads and executes the package from npm without a permanent install.

### 2. The "Arguments" (args list)

The `args` list is the command you would type in a terminal, split into a list of strings.

**Example:**

```python
files_params = {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", sandbox_path]}
```

This needs three arguments because:

- `-y`: Tells npx to auto-confirm downloads.
- `@modelcontextprotocol/server-filesystem`: The npm package name.
- `sandbox_path`: The path required by the server (from its documentation).

### 3. How to Find These "Recipes"

If you want to write your own MCP server params, follow this workflow:

| Step | Action               | Where to Find It                                                      |
| ---- | -------------------- | --------------------------------------------------------------------- |
| 1    | Identify language    | Check the repo for `package.json` (Node) or `pyproject.toml` (Python) |
| 2    | Find the entry point | Look in the README's Installation section                             |
| 3    | Check required flags | See the Configuration/Usage section of the README                     |

#### Pro-tip: Smithery & Official MCP Resources

Most developers use [Smithery.ai](https://smithery.ai/) or the [Official MCP Servers GitHub](https://mcp.so) to get ready-made setup blocks (connection strings) for each tool.

When you see `os.path.join(os.getcwd(), "sandbox")`, that's a best practice: it programmatically restricts the MCP server's access to a safe folder in your project, not your whole computer.

### More Resources

- [MCP.so](https://mcp.so)
- [Glama MCP](https://glama.ai/mcp)
- [Smithery.ai](https://smithery.ai/)
- [Top 11 Essential MCP Libraries (HuggingFace)](https://huggingface.co/blog/LLMhacker/top-11-essential-mcp-libraries)
- [HuggingFace Community Article](https://huggingface.co/blog/Kseniase/mcp)

## Description

MCP server parameters are Python dictionaries that specify how to launch or connect to MCP servers (such as for accounts, market data, push notifications, etc). These parameters are used to configure agents with the correct tool endpoints.

## Required Imports

```python
import os
from dotenv import load_dotenv
from market import is_paid_polygon, is_realtime_polygon
```

## Example Code

```python
load_dotenv(override=True)

polygon_api_key = os.getenv("POLYGON_API_KEY")

if is_paid_polygon or is_realtime_polygon:
    market_mcp = {
        "command": "uvx",
        "args": ["--from", "git+https://github.com/polygon-io/mcp_polygon@v0.1.0", "mcp_polygon"],
        "env": {"POLYGON_API_KEY": polygon_api_key},
    }
else:
    market_mcp = {"command": "uv", "args": ["run", "market_server.py"]}

trader_mcp_server_params = [
    {"command": "uv", "args": ["run", "accounts_server.py"]},
    {"command": "uv", "args": ["run", "push_server.py"]},
    market_mcp,
]

def researcher_mcp_server_params(name: str):
    brave_env = {"BRAVE_API_KEY": os.getenv("BRAVE_API_KEY")}
    return [
        {"command": "uvx", "args": ["mcp-server-fetch"]},
        {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-brave-search"],
            "env": brave_env,
        },
        {
            "command": "npx",
            "args": ["-y", "mcp-memory-libsql"],
            "env": {"LIBSQL_URL": f"file:./memory/{name}.db"},
        },
    ]
```

- `trader_mcp_server_params` is a list of MCP server parameter dicts for the trader agent.
- `researcher_mcp_server_params(name)` returns a list of MCP server parameter dicts for the researcher agent, including memory and search tools.

---

Update this file if you add new MCP server types or change the parameter structure.
