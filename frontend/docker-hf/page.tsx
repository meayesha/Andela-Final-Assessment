"use client";

import { useCallback, useEffect, useState } from "react";
import { ChatShell } from "./ChatShell";

export default function HomePage() {
  const [sessionId, setSessionId] = useState("");
  useEffect(() => {
    setSessionId(crypto.randomUUID());
  }, []);
  const getAuthHeaders = useCallback(async (): Promise<Record<string, string>> => ({}), []);

  if (!sessionId) {
    return (
      <div style={{ padding: 24, color: "var(--muted)" }}>
        Loading…
      </div>
    );
  }

  return <ChatShell sessionId={sessionId} getAuthHeaders={getAuthHeaders} />;
}
