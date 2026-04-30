# how_to_equip_agents_with_tools

This guide explains how to equip OpenAI Agents with tools, including best practices and code patterns for both direct tool lists and dynamic tool generation. It covers both simple and advanced use cases.

---

## 1. Assigning Tools Directly to Agents

You can pass a list of tools to the `tools` argument when creating an `Agent`:

```python
from agents import Agent

agent = Agent(
    name="Trader",
    instructions="...",
    model="gpt-4o-mini",
    tools=[tool1, tool2],
    mcp_servers=mcp_servers,
)
```

---

## 2. Creating Tools from Other Agents

You can turn an Agent into a Tool using `.as_tool()` and then provide it to another Agent:

```python
researcher = Agent(
    name="Researcher",
    instructions="...",
    model="gpt-4.1-mini",
    mcp_servers=mcp_servers,
)
researcher_tool = researcher.as_tool(tool_name="Researcher", tool_description="...")

trader = Agent(
    name="Trader",
    instructions="...",
    model="gpt-4o-mini",
    tools=[researcher_tool],
    mcp_servers=trader_mcp_servers,
)
```

---

## 3. Dynamic Tool Generation

You can dynamically generate tools from MCP servers or other sources:

```python
async def get_accounts_tools_openai():
    openai_tools = []
    for tool in await list_accounts_tools():
        schema = {**tool.inputSchema, "additionalProperties": False}
        openai_tool = FunctionTool(
            name=tool.name,
            description=tool.description,
            params_json_schema=schema,
            on_invoke_tool=lambda ctx, args, toolname=tool.name: call_accounts_tool(toolname, json.loads(args))
        )
        openai_tools.append(openai_tool)
    return openai_tools
```

---

## 4. Best Practices

- Use `.as_tool()` to wrap agents as tools for other agents.
- Pass all required tools in the `tools` list when creating an agent.
- Use clear names and descriptions for tools.
- For advanced use cases, dynamically generate tools from MCP servers or other registries.
- Always ensure tools are compatible with the agent's workflow and model.

---

## 5. Example: Trader Agent with Researcher Tool

```python
async def get_researcher_tool(mcp_servers, model_name) -> Tool:
    researcher = await get_researcher(mcp_servers, model_name)
    return researcher.as_tool(tool_name="Researcher", tool_description=research_tool())

class Trader:
    ...
    async def create_agent(self, trader_mcp_servers, researcher_mcp_servers) -> Agent:
        tool = await get_researcher_tool(researcher_mcp_servers, self.model_name)
        self.agent = Agent(
            name=self.name,
            instructions=trader_instructions(self.name),
            model=get_model(self.model_name),
            tools=[tool],
            mcp_servers=trader_mcp_servers,
        )
        return self.agent
```

---

## Summary

- Equip agents by passing a list of tools to the `tools` argument.
- Use `.as_tool()` to wrap agents as tools for others.
- Dynamically generate tools for advanced scenarios.
- Always document tool usage and agent configuration for maintainability.
