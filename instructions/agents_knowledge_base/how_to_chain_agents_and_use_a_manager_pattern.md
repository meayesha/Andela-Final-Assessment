# How to Chain Agents and Use a Manager Pattern

You can orchestrate multiple agents (e.g., sales agents, review agent, guardrails) using a manager class for multi-step workflows.

## Example: Manager Pattern

```python
from agents import Runner

class EmailCampaignManager:
    async def run(self, prompt: str):
        result = await Runner.run(sales_manager, prompt, max_turns=20)
        return result.final_output
```
