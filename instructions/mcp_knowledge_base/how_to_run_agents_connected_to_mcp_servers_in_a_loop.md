# how_to_run_agents_connected_to_mcp_servers_in_a_loop

This guide explains how to run agents connected to MCP servers in a loop, controlled by intervals or configuration, to achieve ongoing or scheduled goals. It includes best practices, code patterns, and configuration options.

---

## 1. Using Async Loops and Intervals

You can run agents in a loop using `asyncio` and `asyncio.sleep()` to control the interval between runs.

### Example: Running Agents Every N Minutes

```python
import asyncio
import os
from trading_floor import create_traders, is_market_open

RUN_EVERY_N_MINUTES = int(os.getenv("RUN_EVERY_N_MINUTES", "60"))
RUN_EVEN_WHEN_MARKET_IS_CLOSED = os.getenv("RUN_EVEN_WHEN_MARKET_IS_CLOSED", "false").strip().lower() == "true"

async def run_every_n_minutes():
    traders = create_traders()
    while True:
        if RUN_EVEN_WHEN_MARKET_IS_CLOSED or is_market_open():
            await asyncio.gather(*[trader.run() for trader in traders])
        else:
            print("Market is closed, skipping run")
        await asyncio.sleep(RUN_EVERY_N_MINUTES * 60)

if __name__ == "__main__":
    print(f"Starting scheduler to run every {RUN_EVERY_N_MINUTES} minutes")
    asyncio.run(run_every_n_minutes())
```

---

## 2. Controlling Behavior with Configs and Environment Variables

- Use environment variables or config files to control interval, agent selection, and run conditions.
- Example config options:
  - `RUN_EVERY_N_MINUTES`: How often to run the agents.
  - `RUN_EVEN_WHEN_MARKET_IS_CLOSED`: Whether to run when the market is closed.
  - `USE_MANY_MODELS`: Whether to use multiple models for agents.

---

## 3. Best Practices

- Use `asyncio.gather()` to run multiple agents concurrently.
- Use `asyncio.sleep()` for interval control.
- Check conditions (e.g., market open/closed) before running agents.
- Log or trace each run for monitoring and debugging.
- Make interval and run conditions configurable for flexibility.

---

## 4. Example: Agent Run Method

```python
class Trader:
    ...
    async def run(self):
        try:
            await self.run_with_trace()
        except Exception as e:
            print(f"Error running trader {self.name}: {e}")
        self.do_trade = not self.do_trade
```

---

## Summary

- Use async loops and `asyncio.sleep()` to schedule agent runs.
- Control timing and conditions with environment variables or configs.
- Run agents concurrently with `asyncio.gather()`.
- Check conditions and log each run for robust, maintainable automation.
