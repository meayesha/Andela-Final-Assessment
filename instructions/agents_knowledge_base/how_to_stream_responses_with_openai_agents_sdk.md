# how_to_stream_responses_with_openai_agents_sdk.md

This guide explains how to stream responses using the OpenAI Agents SDK, following the coding style and approach used in your agents folder notebooks. This is useful for real-time applications where you want to process or display partial results as they arrive.

## Required Imports

```python
# Example: import your Agent and Runner classes as used in your project
from agents import Agent, Runner
import asyncio
```

## Example: Streaming with OpenAI Agents SDK (Async)

```python
# Assume sales_agent1 is an Agent instance already configured
result = Runner.run_streamed(sales_agent1, input="Write a cold sales email")
async for event in result.stream_events():
    if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
        print(event.data.delta, end="", flush=True)
```

## Example: Running Multiple Agents in Parallel (Async)

```python
message = "Write a cold sales email"

with trace("Parallel cold emails"):
    results = await asyncio.gather(
        Runner.run(sales_agent1, message),
        Runner.run(sales_agent2, message),
        Runner.run(sales_agent3, message),
    )
```

## Notes

- The `Runner.run_streamed` method returns an async generator of events.
- Use `async for event in result.stream_events()` to process streamed events.
- Filter for `raw_response_event` and use `event.data.delta` for the streamed text.
- This pattern matches the approach used in your lab2 notebook.
- For more details, see your project’s agents folder and the OpenAI Agents SDK documentation.
