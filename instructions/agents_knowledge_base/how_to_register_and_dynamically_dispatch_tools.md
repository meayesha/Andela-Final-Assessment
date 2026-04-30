# How to Register and Dynamically Dispatch Tools

You can define tool schemas, register them, and dispatch tool calls dynamically from agent responses.

## Example: Tool Registration and Dispatch

```python
tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json},
]

def handle_tool_call(tool_calls):
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        tool = globals().get(tool_name)
        result = tool(**arguments) if tool else {}
        # ... handle result ...
```
