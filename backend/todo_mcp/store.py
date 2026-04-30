"""SQLite persistence for todos (shared path via TODO_DB_PATH)."""

from __future__ import annotations

import os
import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

import aiosqlite
from pydantic import BaseModel


def get_db_path() -> Path:
    raw = os.environ.get("TODO_DB_PATH", "").strip()
    if raw:
        return Path(raw).expanduser().resolve()
    return (Path(__file__).resolve().parent.parent / "data" / "todos.db").resolve()


def _todo_user_id() -> str:
    """Set by the FastAPI layer per MCP subprocess (TODO_USER_ID); empty = legacy / anonymous."""
    return (os.environ.get("TODO_USER_ID") or "").strip()


class Todo(BaseModel):
    id: int
    title: str
    description: str = ""
    completed: bool
    created_at: str


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


async def _ensure_user_id_column(conn: aiosqlite.Connection) -> None:
    cur = await conn.execute("PRAGMA table_info(todos)")
    rows = await cur.fetchall()
    names = [r[1] for r in rows]
    if "user_id" not in names:
        await conn.execute("ALTER TABLE todos ADD COLUMN user_id TEXT NOT NULL DEFAULT ''")
        await conn.commit()


def _ensure_user_id_column_sync(conn: sqlite3.Connection) -> None:
    cur = conn.execute("PRAGMA table_info(todos)")
    rows = cur.fetchall()
    names = [r[1] for r in rows]
    if "user_id" not in names:
        conn.execute("ALTER TABLE todos ADD COLUMN user_id TEXT NOT NULL DEFAULT ''")
        conn.commit()


async def init_schema(conn: aiosqlite.Connection) -> None:
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            completed INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            user_id TEXT NOT NULL DEFAULT ''
        )
        """
    )
    await conn.commit()
    await _ensure_user_id_column(conn)


@asynccontextmanager
async def get_connection():
    """Single entry: ``async with get_connection() as conn`` (wraps ``aiosqlite.connect`` once)."""
    path = get_db_path()
    _ensure_parent(path)
    async with aiosqlite.connect(path) as conn:
        conn.row_factory = aiosqlite.Row
        await init_schema(conn)
        yield conn


def init_schema_sync(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            completed INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            user_id TEXT NOT NULL DEFAULT ''
        )
        """
    )
    conn.commit()
    _ensure_user_id_column_sync(conn)


def get_connection_sync() -> sqlite3.Connection:
    path = get_db_path()
    _ensure_parent(path)
    conn = sqlite3.connect(str(path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    init_schema_sync(conn)
    return conn


def _row_to_todo(row: sqlite3.Row | aiosqlite.Row) -> Todo:
    return Todo(
        id=int(row["id"]),
        title=str(row["title"]),
        description=str(row["description"] or ""),
        completed=bool(row["completed"]),
        created_at=str(row["created_at"]),
    )


class TodoRepository:
    """Async CRUD used by the MCP server (scoped by TODO_USER_ID env)."""

    @staticmethod
    async def create(title: str, description: str = "", *, user_id: str | None = None) -> Todo:
        uid = (user_id if user_id is not None else _todo_user_id()) or ""
        created = datetime.now(timezone.utc).isoformat()
        async with get_connection() as conn:
            cur = await conn.execute(
                "INSERT INTO todos (title, description, completed, created_at, user_id) VALUES (?, ?, 0, ?, ?)",
                (title.strip(), (description or "").strip(), created, uid),
            )
            await conn.commit()
            tid = cur.lastrowid
        if tid is None:
            raise RuntimeError("Insert did not return id")
        got = await TodoRepository.get_by_id(int(tid), user_id=uid)
        if got is None:
            raise RuntimeError("Failed to read todo after insert")
        return got

    @staticmethod
    async def get_by_id(todo_id: int, *, user_id: str | None = None) -> Todo | None:
        uid = (user_id if user_id is not None else _todo_user_id()) or ""
        async with get_connection() as conn:
            conn.row_factory = aiosqlite.Row
            cur = await conn.execute(
                "SELECT * FROM todos WHERE id = ? AND user_id = ?", (todo_id, uid)
            )
            row = await cur.fetchone()
        if row is None:
            return None
        return _row_to_todo(row)

    @staticmethod
    async def list_all(
        *,
        completed_filter: str | None = None,
        user_id: str | None = None,
    ) -> list[Todo]:
        uid = (user_id if user_id is not None else _todo_user_id()) or ""
        q = "SELECT * FROM todos WHERE user_id = ? ORDER BY id ASC"
        params: list[str | int] = [uid]
        if completed_filter == "completed":
            q = "SELECT * FROM todos WHERE user_id = ? AND completed = 1 ORDER BY id ASC"
        elif completed_filter == "incomplete":
            q = "SELECT * FROM todos WHERE user_id = ? AND completed = 0 ORDER BY id ASC"
        async with get_connection() as conn:
            conn.row_factory = aiosqlite.Row
            cur = await conn.execute(q, params)
            rows = await cur.fetchall()
        return [_row_to_todo(r) for r in rows]

    @staticmethod
    async def update(
        todo_id: int,
        *,
        title: str | None = None,
        description: str | None = None,
        user_id: str | None = None,
    ) -> Todo | None:
        uid = (user_id if user_id is not None else _todo_user_id()) or ""
        existing = await TodoRepository.get_by_id(todo_id, user_id=uid)
        if existing is None:
            return None
        new_title = existing.title if title is None else title.strip()
        new_desc = existing.description if description is None else description.strip()
        async with get_connection() as conn:
            await conn.execute(
                "UPDATE todos SET title = ?, description = ? WHERE id = ? AND user_id = ?",
                (new_title, new_desc, todo_id, uid),
            )
            await conn.commit()
        return await TodoRepository.get_by_id(todo_id, user_id=uid)

    @staticmethod
    async def delete(todo_id: int, *, user_id: str | None = None) -> bool:
        uid = (user_id if user_id is not None else _todo_user_id()) or ""
        async with get_connection() as conn:
            cur = await conn.execute(
                "DELETE FROM todos WHERE id = ? AND user_id = ?", (todo_id, uid)
            )
            await conn.commit()
            return cur.rowcount > 0

    @staticmethod
    async def set_completed(todo_id: int, completed: bool, *, user_id: str | None = None) -> Todo | None:
        uid = (user_id if user_id is not None else _todo_user_id()) or ""
        existing = await TodoRepository.get_by_id(todo_id, user_id=uid)
        if existing is None:
            return None
        async with get_connection() as conn:
            await conn.execute(
                "UPDATE todos SET completed = ? WHERE id = ? AND user_id = ?",
                (1 if completed else 0, todo_id, uid),
            )
            await conn.commit()
        return await TodoRepository.get_by_id(todo_id, user_id=uid)


def list_todos_for_api(user_id: str) -> list[dict]:
    """Synchronous read for the HTTP API (same DB as MCP)."""
    conn = get_connection_sync()
    try:
        cur = conn.execute(
            "SELECT id, title, description, completed, created_at FROM todos WHERE user_id = ? ORDER BY id ASC",
            (user_id,),
        )
        rows = cur.fetchall()
    finally:
        conn.close()
    return [
        {
            "id": int(r["id"]),
            "title": str(r["title"]),
            "description": str(r["description"] or ""),
            "completed": bool(r["completed"]),
            "created_at": str(r["created_at"]),
        }
        for r in rows
    ]
