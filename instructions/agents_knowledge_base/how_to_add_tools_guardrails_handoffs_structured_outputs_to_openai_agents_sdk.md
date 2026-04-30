# how_to_add_tools_guardrails_handoffs_structured_outputs_to_openai_agents_sdk.md

This guide shows how to add tools, guardrails, handoffs, and structured outputs to agents using the OpenAI Agents SDK, based on your codebase patterns.

---

## 1. Tools

Define tools as Python functions and register them with your agent using `.as_tool()` or a decorator:

```python
from agents import Agent
from tools import get_target_contacts, build_mail_merge_plan

# Example tool function
def get_target_contacts(segment: str = "soc2_readiness") -> list:
    return [{"name": "Head of Engineering", "email": "eng-lead@example.com", "company": "Northwind"}]

# Register as tool
manager_tools = [
    get_target_contacts,
    build_mail_merge_plan,
]
```

---

## 2. Guardrails

Guardrails are async functions decorated with `@input_guardrail` or `@output_guardrail` and return a `GuardrailFunctionOutput`. Register them with your agent:

```python
from agents import input_guardrail, output_guardrail, GuardrailFunctionOutput

@input_guardrail
async def guardrail_against_personal_name(ctx, _agent, user_input):
    # Block if a personal name is detected
    blocked = "Michael" in user_input
    return GuardrailFunctionOutput(
        output_info={"name_check": {"blocked": blocked}},
        tripwire_triggered=blocked,
    )

# Register with agent
sales_manager = Agent(
    name="sales_manager",
    instructions="...",
    tools=manager_tools,
    input_guardrails=[guardrail_against_personal_name],
)
```

---

## 3. Handoffs

Handoffs are implemented by calling other agents as tools:

```python
review_tool = review_agent.as_tool(
    tool_name="review_agent",
    tool_description="Review drafts and select the best one."
)
manager_tools.append(review_tool)
```

---

## 4. Structured Outputs

Use Pydantic models to define structured outputs for agents and tools:

```python
from pydantic import BaseModel, Field
from typing import Literal

class ColdEmail(BaseModel):
    subject: str = Field(min_length=8, max_length=120)
    preview_text: str = Field(min_length=12, max_length=160)
    body_text: str = Field(min_length=80)
    cta: str = Field(min_length=8, max_length=120)
    tone: Literal["serious", "engaging", "concise", "playful"]

# Use as output_type
sales_agent = Agent(
    name="sales_agent",
    instructions="...",
    output_type=ColdEmail,
)
```

---

## Limitations

- Guardrails and structured outputs require async handling and careful schema design.
- Not all advanced handoff or orchestration patterns are supported in all SDK versions.
- Always check the [OpenAI Agents SDK docs](https://github.com/openai/openai-python) for updates.
