# how_to_connect_to_openai_library_using_openrouter.md

This guide explains how to connect to the OpenAI library using OpenRouter, including required imports, environment variables, and example code snippets. This is useful for leveraging OpenAI-compatible models via the OpenRouter API in your agents.

## Required Imports

```python
from openai import OpenAI
import os
```

## Required Environment Variables

- `OPENROUTER_API_KEY`: Your OpenRouter API key (get from <https://openrouter.ai/>)

## Example: Setting a Structured Output (Pydantic)

You can use Pydantic models to enforce structured outputs for completions. For example:

```python
from pydantic import BaseModel, Field

class UserInfo(BaseModel):
    name: str = Field(...)
    email: str = Field(...)

# When calling OpenAI, you can validate the response:
response = ai.chat.completions.create(
    model="openai/gpt-4o",
    messages=[{"role": "user", "content": "My name is Michael and my email is michael@example.com"}],
)
user_info = UserInfo.model_validate_json(response.choices[0].message.content)
print(user_info)
```

```python
from openai import OpenAI
import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

ai = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

# Example: Chat completion
response = ai.chat.completions.create(
    model="openai/gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

## Example Code: Async Client

```python
from openai import AsyncOpenAI
import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

ai = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

# Example: Chat completion (async)
import asyncio
async def main():
    response = await ai.chat.completions.create(
        model="openai/gpt-4o",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print(response.choices[0].message.content)

asyncio.run(main())
```

## Notes

- Make sure your `OPENROUTER_API_KEY` is set in your environment (e.g., in a `.env` file or system environment variables).
- You can use any OpenAI-compatible model available on OpenRouter by changing the `model` parameter.
- For advanced usage, see the [OpenRouter documentation](https://openrouter.ai/docs) and [OpenAI Python SDK docs](https://github.com/openai/openai-python).
