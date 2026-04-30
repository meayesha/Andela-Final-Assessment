# How to Build a Gradio UI for Agent Chat

You can wrap agent chat logic in a Gradio interface for interactive web demos.

## Example: Gradio Chat Interface

```python
import gradio as gr

def chat_fn(message, history):
    # ... agent chat logic ...
    return agent_response

gr.ChatInterface(chat_fn, type="messages").launch()
```

Or, for streaming output:

```python
with gr.Blocks() as ui:
    prompt_box = gr.Textbox(label="Prompt")
    run_button = gr.Button("Run")
    output = gr.Markdown()
    run_button.click(fn=run_campaign, inputs=prompt_box, outputs=output)

ui.launch()
```
