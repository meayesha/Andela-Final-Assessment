# how_to_chain_multiple_mcp_tools_for_a_workflow

This guide explains how to orchestrate multiple MCP servers and tools to solve complex, multi-step problems. It covers chaining tool calls, managing dependencies, and best practices for robust workflows.

---

## 1. Break Down the Problem

- Decompose the goal into sequential or parallel sub-tasks.
- Assign each sub-task to the most appropriate MCP server/tool (see how_to_select_the_right_mcp_server_for_a_problem.md).

---

## 2. Example: Chaining Tool Calls

```python
# Example: Research a stock, analyze, and notify
research_result = await researcher_server.call_tool("research", {"query": "AAPL"})
analysis_result = await analysis_server.call_tool("analyze", {"data": research_result["data"]})
await push_server.call_tool("push", {"message": analysis_result["summary"]})
```

---

## 3. Use Asyncio for Parallelism

- Use `asyncio.gather()` to run independent tool calls concurrently.

```python
results = await asyncio.gather(
    researcher_server.call_tool("research", {"query": "AAPL"}),
    market_server.call_tool("get_share_price", {"symbol": "AAPL"})
)
```

---

## 4. Handle Data Passing and Dependencies

- Pass outputs from one tool as inputs to the next as needed.
- Validate and transform data between steps if required.

---

## 5. Best Practices

- Log each step for traceability and debugging.
- Handle errors gracefully; retry or fallback as needed.
- Document the workflow for maintainability.
- Use config or workflow definitions for flexible orchestration.

---

## 6. Example: Config-Driven Workflow

```python
workflow = [
    {"server": researcher_server, "tool": "research", "args": {"query": "AAPL"}},
    {"server": analysis_server, "tool": "analyze", "args_from": "prev"},
    {"server": push_server, "tool": "push", "args_from": "prev.summary"}
]

result = None
for step in workflow:
    args = step["args"] if "args" in step else result
    result = await step["server"].call_tool(step["tool"], args)
```

---

## Summary

- Chain tool calls by passing outputs to inputs.
- Use asyncio for parallel steps.
- Log, handle errors, and document workflows for robust automation.
