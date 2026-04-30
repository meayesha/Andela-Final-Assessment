"use client";

import { useEffect, useRef, useState } from "react";
import { UserButton } from "@clerk/nextjs";
import {
  clientApiRequestUrl,
  getPublicApiBase,
  publicApiBaseIsInvalidHubUrl,
} from "../lib/api-request-url";

type ChatMessage = { id: string; role: "user" | "assistant"; content: string };

const SESSION_KEY = "meridian_support_session_id";

export function getOrCreateAnonymousSessionId(): string {
  if (typeof window === "undefined") return "";
  let id = sessionStorage.getItem(SESSION_KEY);
  if (!id) {
    id = crypto.randomUUID();
    sessionStorage.setItem(SESSION_KEY, id);
  }
  return id;
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
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [vercelApiIssue, setVercelApiIssue] = useState<
    "missing" | "self" | "proxy503" | "hfGitUrl" | null
  >(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;
    if (publicApiBaseIsInvalidHubUrl()) {
      setVercelApiIssue("hfGitUrl");
      return;
    }
    const host = window.location.hostname;
    if (!host.endsWith("vercel.app")) {
      setVercelApiIssue(null);
      return;
    }
    const b = getPublicApiBase();
    if (b === window.location.origin) {
      setVercelApiIssue("self");
      return;
    }
    if (b) {
      setVercelApiIssue(null);
      return;
    }
    void fetch(clientApiRequestUrl("/api/health"), { method: "GET" })
      .then(async (r) => {
        if (r.ok) {
          setVercelApiIssue(null);
          return;
        }
        if (r.status === 503) {
          setVercelApiIssue("proxy503");
          return;
        }
        setVercelApiIssue("missing");
      })
      .catch(() => setVercelApiIssue("missing"));
  }, []);

  useEffect(() => {
    if (!sessionId) return;
    void (async () => {
      const auth = await getAuthHeaders();
      const res = await fetch(
        clientApiRequestUrl(`/api/session/${encodeURIComponent(sessionId)}/history`),
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
  }, [sessionId, getAuthHeaders]);

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
    const res = await fetch(clientApiRequestUrl("/api/chat/stream"), {
      method: "POST",
      headers: { "Content-Type": "application/json", ...auth },
      body: JSON.stringify({ message: text, session_id: sessionId }),
    });

    if (!res.ok || !res.body) {
      const hint =
        res.status === 404
          ? "404: /api/chat/stream is not running on this host. On Vercel use Root Directory = frontend, leave Output Directory empty, remove STATIC_EXPORT from env, set API_PROXY_ORIGIN (or NEXT_PUBLIC_API_URL), redeploy."
          : `Request failed (${res.status}).`;
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
    <>
      {vercelApiIssue === "hfGitUrl" ? (
        <div
          role="alert"
          style={{
            padding: "12px 16px",
            background: "var(--surface-hover)",
            borderBottom: "1px solid var(--border)",
            color: "var(--text)",
            fontSize: 14,
            textAlign: "center",
          }}
        >
          <code style={{ fontSize: 13 }}>NEXT_PUBLIC_API_URL</code> must not be{" "}
          <code style={{ fontSize: 13 }}>huggingface.co/spaces/…</code> — use your Space{" "}
          <code style={{ fontSize: 13 }}>*.hf.space</code> URL or <code style={{ fontSize: 13 }}>API_PROXY_ORIGIN</code>.
        </div>
      ) : null}
      {vercelApiIssue === "proxy503" ? (
        <div role="status" style={{ padding: "12px 16px", borderBottom: "1px solid var(--border)", fontSize: 14 }}>
          Set <code>API_PROXY_ORIGIN</code> or <code>NEXT_PUBLIC_API_URL</code> on Vercel (Production + Preview), then redeploy.
        </div>
      ) : null}
      {vercelApiIssue === "missing" ? (
        <div role="status" style={{ padding: "12px 16px", borderBottom: "1px solid var(--border)", fontSize: 14 }}>
          Chat needs the FastAPI backend. Set <code>NEXT_PUBLIC_API_URL</code> or server-only <code>API_PROXY_ORIGIN</code>, then redeploy.
        </div>
      ) : null}
      {vercelApiIssue === "self" ? (
        <div role="status" style={{ padding: "12px 16px", borderBottom: "1px solid var(--border)", fontSize: 14 }}>
          <code>NEXT_PUBLIC_API_URL</code> must be your API origin (e.g. <code>https://…hf.space</code>), not this Vercel URL.
        </div>
      ) : null}
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
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "space-between",
            gap: 16,
          }}
        >
          <div>
            <h1 style={{ margin: 0, fontSize: "1.2rem", fontWeight: 700 }}>Meridian Electronics</h1>
            <h2 style={{ margin: "6px 0 0", fontSize: "1rem", fontWeight: 500 }}>Customer support</h2>
            <p style={{ margin: "8px 0 0", fontSize: 13, color: "var(--muted)", maxWidth: 560 }}>
              Hi there! I am Meridian&apos;s customer support assistant. How can I help you today?
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
              Examples: product search, order status, or account verification — the assistant uses Meridian&apos;s order
              tools.
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
    </>
  );
}
