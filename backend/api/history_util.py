"""Map persisted Responses-style session items to simple chat messages for the UI."""

from __future__ import annotations

from typing import Any


def _content_to_text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        btype = str(content.get("type", ""))
        if btype in ("input_text", "output_text", "text") and "text" in content:
            return str(content.get("text", ""))
        if isinstance(content.get("text"), str):
            return str(content["text"])
        return ""
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict):
                btype = str(block.get("type", ""))
                if btype in ("input_text", "output_text"):
                    parts.append(str(block.get("text", "")))
                elif "text" in block:
                    parts.append(str(block["text"]))
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts)
    return str(content)


def session_items_to_chat(items: list[dict[str, Any]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for item in items:
        role = item.get("role")
        if role not in ("user", "assistant"):
            continue
        text = _content_to_text(item.get("content")).strip()
        if text:
            out.append({"role": str(role), "content": text})
    return out
