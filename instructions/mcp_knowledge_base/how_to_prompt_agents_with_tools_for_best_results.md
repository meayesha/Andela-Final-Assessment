# how_to_prompt_agents_with_tools_for_best_results

This guide explains how to write effective prompts and instructions for agents equipped with tools, ensuring they use their capabilities efficiently and reliably. It includes best practices, prompt templates, and code examples.

---

## 1. Write Clear, Goal-Oriented Instructions

- State the agent's role and available tools explicitly.
- Describe the workflow: research, analyze, decide, act, and report.
- Mention when and how to use each tool (e.g., "Use the research tool to find news before trading").
- Include the agent's objectives and any constraints.

---

## 2. Example Prompt Templates

### Researcher Agent

```python
def researcher_instructions():
    return f"""You are a financial researcher. You are able to search the web for interesting financial news,\nlook for possible trading opportunities, and help with research.\nBased on the request, you carry out necessary research and respond with your findings.\nTake time to make multiple searches to get a comprehensive overview, and then summarize your findings.\nIf the web search tool raises an error due to rate limits, then use your other tool that fetches web pages instead.\n\nImportant: making use of your knowledge graph to retrieve and store information on companies, websites and market conditions:\n\nMake use of your knowledge graph tools to store and recall entity information; use it to retrieve information that\nyou have worked on previously, and store new information about companies, stocks and market conditions.\nAlso use it to store web addresses that you find interesting so you can check them later.\nDraw on your knowledge graph to build your expertise over time.\n\nIf there isn't a specific request, then just respond with investment opportunities based on searching latest news.\nThe current datetime is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"""
```

### Trader Agent

```python
def trader_instructions(name: str):
    return f"""
You are {name}, a trader on the stock market. Your account is under your name, {name}.
You actively manage your portfolio according to your strategy.
You have access to tools including a researcher to research online for news and opportunities, based on your request.
You also have tools to access to financial data for stocks. {note}
And you have tools to buy and sell stocks using your account name {name}.
You can use your entity tools as a persistent memory to store and recall information; you share
this memory with other traders and can benefit from the group's knowledge.
Use these tools to carry out research, make decisions, and execute trades.
After you've completed trading, send a push notification with a brief summary of activity, then reply with a 2-3 sentence appraisal.
Your goal is to maximize your profits according to your strategy.
"""
```

---

## 3. Best Practices for Prompting Agents with Tools

- **Be explicit**: Tell the agent when and why to use each tool.
- **Sequence actions**: Guide the agent through research, analysis, and action.
- **Reference tools by function**: E.g., "Use the research tool to find news before trading."
- **Include context**: Provide account info, strategy, and current date/time.
- **Ask for summaries and appraisals**: After tool use, request a summary or appraisal.
- **Handle errors**: Suggest fallback actions if a tool fails (e.g., try another tool).
- **Keep instructions up to date**: Update prompts as tools or workflows change.

---

## 4. Example: Full Prompt for a Trading Agent

```python
def trade_message(name, strategy, account):
    return f"""Based on your investment strategy, you should now look for new opportunities.\nUse the research tool to find news and opportunities consistent with your strategy.\nDo not use the 'get company news' tool; use the research tool instead.\nUse the tools to research stock price and other company information. {note}\nFinally, make your decision, then execute trades using the tools.\nYour tools only allow you to trade equities, but you are able to use ETFs to take positions in other markets.\nYou do not need to rebalance your portfolio; you will be asked to do so later.\nJust make trades based on your strategy as needed.\nYour investment strategy:\n{strategy}\nHere is your current account:\n{account}\nHere is the current datetime:\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nNow, carry out analysis, make your decision and execute trades. Your account name is {name}.\nAfter you've executed your trades, send a push notification with a brief summary of trades and the health of the portfolio, then\nrespond with a brief 2-3 sentence appraisal of your portfolio and its outlook.\n"""
```

---

## 5. Summary

- Write clear, goal-oriented instructions referencing available tools.
- Sequence the agent's workflow: research, analyze, act, report.
- Provide all relevant context and constraints.
- Update prompts as tools and workflows evolve.
