"""stdio MCP server exposing todo CRUD tools (SQLite via TodoRepository)."""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from todo_mcp.store import Todo, TodoRepository

mcp = FastMCP(
    "Todo MCP",
    instructions="Tools to create, list, update, delete todos and toggle completion.",
)


def _todo_json(t: Todo) -> str:
    return json.dumps(t.model_dump(), indent=2)


@mcp.tool()
async def create_todo(title: str, description: str = "") -> str:
    """Create a new todo. Title is required; description is optional."""
    if not title or not title.strip():
        return "Error: title is required."
    todo = await TodoRepository.create(title=title, description=description or "")
    return f"Created todo.\n{_todo_json(todo)}"


@mcp.tool()
async def list_todos(filter_status: str = "all") -> str:
    """List todos. filter_status must be one of: all, completed, incomplete."""
    fs = (filter_status or "all").strip().lower()
    if fs not in ("all", "completed", "incomplete"):
        return "Error: filter_status must be 'all', 'completed', or 'incomplete'."
    key = None if fs == "all" else fs
    todos = await TodoRepository.list_all(completed_filter=key)
    if not todos:
        return "No todos found."
    lines = [_todo_json(t) for t in todos]
    return "\n\n".join(lines)


@mcp.tool()
async def update_todo(
    todo_id: int,
    title: str | None = None,
    description: str | None = None,
) -> str:
    """Update a todo by id. Provide at least one of title or description."""
    if title is None and description is None:
        return "Error: provide title and/or description to update."
    updated = await TodoRepository.update(todo_id, title=title, description=description)
    if updated is None:
        return f"Error: no todo with id {todo_id}."
    return f"Updated todo.\n{_todo_json(updated)}"


@mcp.tool()
async def delete_todo(todo_id: int) -> str:
    """Delete a todo by id."""
    ok = await TodoRepository.delete(todo_id)
    if not ok:
        return f"Error: no todo with id {todo_id}."
    return f"Deleted todo {todo_id}."


@mcp.tool()
async def set_todo_completed(todo_id: int, completed: bool) -> str:
    """Mark a todo as completed (true) or incomplete (false)."""
    todo = await TodoRepository.set_completed(todo_id, completed)
    if todo is None:
        return f"Error: no todo with id {todo_id}."
    return f"Todo {todo_id} marked {'completed' if completed else 'incomplete'}.\n{_todo_json(todo)}"
