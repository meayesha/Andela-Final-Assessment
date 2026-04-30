# Example: Setting a Structured Output with output_type

You can enforce structured outputs by passing a Pydantic model as the `output_type` argument when creating an Agent:

```python
from agents import Agent
from pydantic import BaseModel, Field

class UserInfo(BaseModel):
 name: str = Field(...)
 email: str = Field(...)

agent = Agent(
 name="user_info_agent",
 instructions="Extract the user's name and email from the conversation.",
 model=your_model,
 output_type=UserInfo,  # Enforces structured output
)
```

## how_to_connect_to_openai_agents_sdk_using_openrouter.md

This guide explains how to connect to the OpenAI Agents SDK using OpenRouter, including required imports, environment variables, and example code snippets. This allows you to use OpenAI-compatible models via OpenRouter in your agent toolchains.

## Required Imports

```python
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel
import os
```

## Required Environment Variables

- `OPENROUTER_API_KEY`: Your OpenRouter API key (get from <https://openrouter.ai/>)

## Example Code: Registering an OpenAI Agent with OpenRouter

```python
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel
import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Create the OpenAI async client for OpenRouter
client = AsyncOpenAI(base_url=OPENROUTER_BASE_URL, api_key=OPENROUTER_API_KEY)

# Register the model with your agent system
model_name = "openai/gpt-4o"  # or any OpenRouter-supported model
agent_model = OpenAIChatCompletionsModel(model=model_name, openai_client=client)

# Use agent_model in your agent toolchain as needed
```

## Notes

- Make sure your `OPENROUTER_API_KEY` is set in your environment (e.g., in a `.env` file or system environment variables).
- You can use any OpenAI-compatible model available on OpenRouter by changing the `model_name` parameter.
- For advanced usage, see the [OpenRouter documentation](https://openrouter.ai/docs) and [OpenAI Python SDK docs](https://github.com/openai/openai-python).
