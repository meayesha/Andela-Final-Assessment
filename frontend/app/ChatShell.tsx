"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { UserButton } from "@clerk/nextjs";

type ChatMessage = { id: string; role: "user" | "assistant"; content: string };

type Todo = {
  id: number;
  title: string;
  description: string;
  completed: boolean;
  created_at: string;
};

const SESSION_KEY = "todo_mcp_session_id";

export function getOrCreateAnonymousSessionId(): string {
  if (typeof window === "undefined") return "";
  let id = sessionStorage.getItem(SESSION_KEY);
  if (!id) {
    id = crypto.randomUUID();
    sessionStorage.setItem(SESSION_KEY, id);
  }
  return id;
}

function apiBase(): string {
  return (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
}

async function parseSSEStream(
  reader: ReadableStreamDefaultReader<Uint8Array>,
  onToken: (t: string) => void,
  onDone: () => void,
  onError: (m: string) => void,
) {
  const dec = new TextDecoder();
  let buf = "";
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    const parts = buf.split("\n\n");
    buf = parts.pop() || "";
    for (const block of parts) {
      for (const line of block.split("\n")) {
        if (!line.startsWith("data: ")) continue;
        const raw = line.slice(6).trim();
        if (!raw) continue;
        let data: { type?: string; text?: string; message?: string };
        try {
          data = JSON.parse(raw);
        } catch {
          continue;
        }
        if (data.type === "token" && data.text) onToken(data.text);
        else if (data.type === "done") onDone();
        else if (data.type === "error" && data.message) onError(data.message);
      }
    }
  }
  onDone();
}

export type ChatShellProps = {
  sessionId: string;
  getAuthHeaders: () => Promise<Record<string, string>>;
  showUserButton?: boolean;
};

export function ChatShell({ sessionId, getAuthHeaders, showUserButton }: ChatShellProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [todos, setTodos] = useState<Todo[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const fetchTodos = useCallback(async () => {
    const base = apiBase();
    const auth = await getAuthHeaders();
    const res = await fetch(`${base}/api/todos`, { headers: { ...auth } });
    if (!res.ok) return;
    setTodos(await res.json());
  }, [getAuthHeaders]);

  useEffect(() => {
    if (!sessionId) return;
    void fetchTodos();
    const base = apiBase();
    void (async () => {
      const auth = await getAuthHeaders();
      const res = await fetch(`${base}/api/session/${encodeURIComponent(sessionId)}/history`, {
        headers: { ...auth },
      });
      if (!res.ok) return;
      const data = (await res.json()) as { messages: { role: string; content: string }[] };
      const mapped: ChatMessage[] = (data.messages || []).map((m, i) => ({
        id: `h-${i}`,
        role: m.role === "assistant" ? "assistant" : "user",
        content: m.content,
      }));
      setMessages(mapped);
    })();
  }, [sessionId, fetchTodos, getAuthHeaders]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function sendMessage() {
    const text = input.trim();
    if (!text || loading || !sessionId) return;
    setInput("");
    const userMsg: ChatMessage = { id: `u-${Date.now()}`, role: "user", content: text };
    const asstId = `a-${Date.now()}`;
    setMessages((prev) => [...prev, userMsg, { id: asstId, role: "assistant", content: "" }]);
    setLoading(true);

    const base = apiBase();
    const auth = await getAuthHeaders();
    const res = await fetch(`${base}/api/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...auth },
      body: JSON.stringify({ message: text, session_id: sessionId }),
    });

    if (!res.ok || !res.body) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === asstId ? { ...m, content: `Request failed (${res.status}).` } : m,
        ),
      );
      setLoading(false);
      return;
    }

    const reader = res.body.getReader();
    await parseSSEStream(
      reader,
      (token) => {
        setMessages((prev) =>
          prev.map((m) => (m.id === asstId ? { ...m, content: m.content + token } : m)),
        );
      },
      () => {
        setLoading(false);
        void fetchTodos();
      },
      (msg) => {
        setMessages((prev) =>
          prev.map((m) => (m.id === asstId ? { ...m, content: `Error: ${msg}` } : m)),
        );
        setLoading(false);
        void fetchTodos();
      },
    );
  }

  return (
    <div
      className="app-grid"
      style={{
        display: "grid",
        gridTemplateColumns: "minmax(260px, 320px) 1fr",
        minHeight: "100vh",
        maxWidth: 1200,
        margin: "0 auto",
        gap: 0,
      }}
    >
      <aside
        style={{
          borderRight: "1px solid var(--border)",
          background: "var(--surface)",
          display: "flex",
          flexDirection: "column",
          padding: 16,
        }}
      >
        <h1 style={{ fontSize: "1.1rem", margin: "0 0 4px", fontWeight: 600 }}>Your todos</h1>
        <p style={{ margin: "0 0 16px", fontSize: 12, color: "var(--muted)" }}>
          Synced from the MCP server (SQLite), scoped to your account when signed in.
        </p>
        <button
          type="button"
          onClick={() => void fetchTodos()}
          style={{
            marginBottom: 12,
            padding: "8px 12px",
            borderRadius: 8,
            border: "1px solid var(--border)",
            background: "var(--surface-hover)",
            color: "var(--text)",
            cursor: "pointer",
            fontSize: 13,
          }}
        >
          Refresh list
        </button>
        <ul style={{ listStyle: "none", margin: 0, padding: 0, overflowY: "auto", flex: 1 }}>
          {todos.length === 0 ? (
            <li style={{ color: "var(--muted)", fontSize: 14 }}>No todos yet. Ask the assistant.</li>
          ) : (
            todos.map((t) => (
              <li
                key={t.id}
                style={{
                  padding: "10px 12px",
                  marginBottom: 8,
                  borderRadius: "var(--radius)",
                  background: "var(--bg)",
                  border: "1px solid var(--border)",
                  fontSize: 14,
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                  <span
                    style={{
                      fontSize: 11,
                      fontWeight: 600,
                      color: t.completed ? "var(--success)" : "var(--muted)",
                    }}
                  >
                    {t.completed ? "Done" : "Open"}
                  </span>
                  <span style={{ color: "var(--muted)", fontSize: 11 }}>#{t.id}</span>
                </div>
                <div style={{ fontWeight: 500 }}>{t.title}</div>
                {t.description ? (
                  <div style={{ color: "var(--muted)", fontSize: 12, marginTop: 4 }}>{t.description}</div>
                ) : null}
              </li>
            ))
          )}
        </ul>
      </aside>

      <main style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
        <header
          style={{
            padding: "16px 20px",
            borderBottom: "1px solid var(--border)",
            background: "var(--surface)",
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "space-between",
            gap: 16,
          }}
        >
          <div>
            <h2 style={{ margin: 0, fontSize: "1.15rem" }}>Todo assistant</h2>
            <p style={{ margin: "6px 0 0", fontSize: 13, color: "var(--muted)" }}>
              Natural language is routed through an agent that calls MCP todo tools.
            </p>
          </div>
          {showUserButton ? (
            <div style={{ flexShrink: 0 }}>
              <UserButton afterSignOutUrl="/" />
            </div>
          ) : null}
        </header>

        <div
          style={{
            flex: 1,
            overflowY: "auto",
            padding: 20,
            display: "flex",
            flexDirection: "column",
            gap: 12,
          }}
        >
          {messages.length === 0 ? (
            <p style={{ color: "var(--muted)" }}>
              Try: &quot;Add a todo to buy groceries&quot;, &quot;List my incomplete tasks&quot;, or
              &quot;Mark todo 1 as complete&quot;.
            </p>
          ) : null}
          {messages.map((m) => (
            <div
              key={m.id}
              style={{
                alignSelf: m.role === "user" ? "flex-end" : "flex-start",
                maxWidth: "min(92%, 640px)",
                padding: "12px 16px",
                borderRadius: "var(--radius)",
                background: m.role === "user" ? "var(--user-bg)" : "var(--assistant-bg)",
                border: "1px solid var(--border)",
                whiteSpace: "pre-wrap",
                fontSize: 15,
                lineHeight: 1.5,
              }}
            >
              {m.content || (loading && m.role === "assistant" ? "…" : "")}
            </div>
          ))}
          <div ref={bottomRef} />
        </div>

        <div
          style={{
            padding: 16,
            borderTop: "1px solid var(--border)",
            background: "var(--surface)",
            display: "flex",
            gap: 10,
          }}
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                void sendMessage();
              }
            }}
            placeholder="Message the assistant…"
            disabled={loading}
            style={{
              flex: 1,
              padding: "12px 14px",
              borderRadius: 10,
              border: "1px solid var(--border)",
              background: "var(--bg)",
              color: "var(--text)",
              fontSize: 15,
            }}
          />
          <button
            type="button"
            onClick={() => void sendMessage()}
            disabled={loading || !input.trim()}
            style={{
              padding: "12px 20px",
              borderRadius: 10,
              border: "none",
              background: loading ? "var(--border)" : "var(--accent-dim)",
              color: "#fff",
              fontWeight: 600,
              cursor: loading ? "not-allowed" : "pointer",
            }}
          >
            Send
          </button>
        </div>
      </main>
    </div>
  );
}
