# how_to_handle_authentication_for_remote_mcp_servers

This guide explains how to handle authentication and authorization when connecting to remote/online MCP servers (e.g., Smithery, cloud MCPs). It covers best practices, example flows, and troubleshooting tips.

---

## 1. Understand Auth Requirements

- Some remote MCP servers require OAuth, API keys, or other credentials.
- Check the provider's documentation (e.g., https://smithery.ai/docs/use) for auth requirements.

---

## 2. Smithery Example: Auth Flow

- Use the Smithery CLI to authenticate and authorize your agent:

```sh
npm install -g @smithery/cli
smithery auth login
smithery mcp add <server-slug>
# Follow the URL to authorize
smithery tool list
```

- After auth, you can connect from your agent as usual:

```python
params = {"server": "smithery/<slug>"}
async with MCPServerStdio(params=params, client_session_timeout_seconds=60) as server:
    tools = await server.list_tools()
```

---

## 3. API Keys and Env Vars

- For servers requiring API keys, set them in your `.env` file or environment variables.
- Example:

```sh
export BRAVE_API_KEY=your_key_here
```

- Use `dotenv` to load them in Python.

---

## 4. Best Practices

- Never hardcode secrets in code; use env vars or secret managers.
- Document required credentials for each server.
- Handle auth errors gracefully and provide clear error messages.
- For cloud/hosted MCPs, follow provider-specific onboarding and troubleshooting guides.

---

## 5. Troubleshooting

- If you get auth errors, re-run the CLI login or check your API keys.
- For Smithery, see https://smithery.ai/docs/use and https://smithery.ai/docs/build.
- For other providers, consult their docs or support.

---

## Summary

- Use CLI or API key auth as required by the remote MCP server.
- Store credentials securely.
- Follow provider docs for onboarding and troubleshooting.
