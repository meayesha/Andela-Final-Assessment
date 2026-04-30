"use client";

import { RedirectToSignIn, SignedIn, SignedOut, useAuth } from "@clerk/nextjs";
import { useCallback, useEffect, useState } from "react";
import { ChatShell, getOrCreateAnonymousSessionId } from "./ChatShell";

function ChatClerk() {
  const { isLoaded, userId, getToken } = useAuth();
  const [sessionId, setSessionId] = useState("");

  useEffect(() => {
    if (isLoaded && userId) setSessionId(userId);
  }, [isLoaded, userId]);

  const getAuthHeaders = useCallback(async (): Promise<Record<string, string>> => {
    const t = await getToken();
    if (!t) return {};
    return { Authorization: `Bearer ${t}` };
  }, [getToken]);

  if (!isLoaded || !sessionId) {
    return (
      <div style={{ padding: 24, color: "var(--muted)" }}>
        Loading…
      </div>
    );
  }

  return <ChatShell sessionId={sessionId} getAuthHeaders={getAuthHeaders} showUserButton />;
}

function ChatAnon() {
  const [sessionId, setSessionId] = useState("");
  useEffect(() => {
    setSessionId(getOrCreateAnonymousSessionId());
  }, []);
  const getAuthHeaders = useCallback(async () => ({}), []);

  if (!sessionId) {
    return (
      <div style={{ padding: 24, color: "var(--muted)" }}>
        Loading…
      </div>
    );
  }

  return <ChatShell sessionId={sessionId} getAuthHeaders={getAuthHeaders} />;
}

export default function HomePage() {
  const pk = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;
  if (!pk) {
    return <ChatAnon />;
  }
  return (
    <>
      <SignedIn>
        <ChatClerk />
      </SignedIn>
      <SignedOut>
        <RedirectToSignIn />
      </SignedOut>
    </>
  );
}
