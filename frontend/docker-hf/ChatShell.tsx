"use client";

import { useEffect, useRef, useState } from "react";
import { clientApiRequestUrl } from "../lib/api-request-url";

type ChatMessage = { id: string; role: "user" | "assistant"; content: string };

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
  threadId?: string;
  getAuthHeaders: () => Promise<Record<string, string>>;
};

export function ChatShell({ sessionId, threadId, getAuthHeaders }: ChatShellProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!sessionId) return;
    void (async () => {
      const auth = await getAuthHeaders();
      const q =
        threadId != null && threadId !== ""
          ? `?thread_id=${encodeURIComponent(threadId)}`
          : "";
      const res = await fetch(
        clientApiRequestUrl(`/api/session/${encodeURIComponent(sessionId)}/history${q}`),
        { headers: { ...auth } },
      );
      if (!res.ok) return;
      const data = (await res.json()) as { messages: { role: string; content: string }[] };
      const mapped: ChatMessage[] = (data.messages || []).map((m, i) => ({
        id: `h-${i}`,
        role: m.role === "assistant" ? "assistant" : "user",
        content: m.content,
      }));
      setMessages(mapped);
    })();
  }, [sessionId, threadId, getAuthHeaders]);

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

    const auth = await getAuthHeaders();
    const payload =
      threadId != null && threadId !== ""
        ? { message: text, session_id: sessionId, thread_id: threadId }
        : { message: text, session_id: sessionId };
    const res = await fetch(clientApiRequestUrl("/api/chat/stream"), {
      method: "POST",
      headers: { "Content-Type": "application/json", ...auth },
      body: JSON.stringify(payload),
    });

    if (!res.ok || !res.body) {
      const hint =
        res.status === 404
          ? "Chat is temporarily unavailable. Please try again in a moment."
          : `Something went wrong (${res.status}). Please try again.`;
      setMessages((prev) => prev.map((m) => (m.id === asstId ? { ...m, content: hint } : m)));
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
      () => setLoading(false),
      (msg) => {
        setMessages((prev) =>
          prev.map((m) => (m.id === asstId ? { ...m, content: `Error: ${msg}` } : m)),
        );
        setLoading(false);
      },
    );
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        maxWidth: 920,
        margin: "0 auto",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <header
        style={{
          padding: "16px 20px",
          borderBottom: "1px solid var(--border)",
          background: "var(--surface)",
        }}
      >
        <h1 style={{ margin: 0, fontSize: "1.2rem", fontWeight: 700 }}>Meridian Electronics</h1>
        <h2 style={{ margin: "6px 0 0", fontSize: "1rem", fontWeight: 500 }}>Customer support</h2>
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
          placeholder="Describe what you need help with…"
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
    </div>
  );
}
