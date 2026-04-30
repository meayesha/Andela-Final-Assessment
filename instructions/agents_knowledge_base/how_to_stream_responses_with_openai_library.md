# how_to_stream_responses_with_openai_library.md

This guide explains how to stream responses from the OpenAI library (including OpenRouter) using the same coding style as in your agents folder notebooks. Streaming allows you to receive partial results as they are generated, which is useful for chatbots and real-time applications.

## Required Imports

```python
from openai import OpenAI, AsyncOpenAI
import os
```

## Required Environment Variables

- `OPENROUTER_API_KEY`: Your OpenRouter API key (if using OpenRouter)

---

## Example: Streaming with OpenAI Library (Synchronous)

```python
from openai import OpenAI
import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
openai = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")

def stream_brochure(company_name, url):
    stream = openai.chat.completions.create(
        model="gpt-4.1-mini",  # or your preferred model
        messages=[
            {"role": "system", "content": brochure_system_prompt},
            {"role": "user", "content": get_brochure_user_prompt(company_name, url)}
        ],
        stream=True
    )
    response = ""
    for chunk in stream:
        response += chunk.choices[0].delta.content or ''
        print(response, end="\r", flush=True)  # Or update your UI here
    print()  # Newline after stream

# Usage
stream_brochure("HuggingFace", "https://huggingface.co")
```

## Example: Streaming with OpenAI Library (Async)

```python
from openai import AsyncOpenAI
import os
import asyncio

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
openai = AsyncOpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")

async def stream_brochure(company_name, url):
    stream = await openai.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": brochure_system_prompt},
            {"role": "user", "content": get_brochure_user_prompt(company_name, url)}
        ],
        stream=True
    )
    response = ""
    async for chunk in stream:
        response += chunk.choices[0].delta.content or ''
        print(response, end="\r", flush=True)
    print()

# Usage
asyncio.run(stream_brochure("HuggingFace", "https://huggingface.co"))
```

---

## Notes

- The `stream=True` parameter enables streaming.
- Each `chunk` contains a partial response. Concatenate `chunk.choices[0].delta.content` to build the full message.
- The code style matches the approach used in your lab and day5 notebooks.
- Works with both OpenAI and OpenRouter endpoints.
- For more details, see the [OpenAI Python SDK docs](https://github.com/openai/openai-python) and [OpenRouter docs](https://openrouter.ai/docs).
