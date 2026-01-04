"use client";

import { useEffect, useMemo, useState } from "react";

type Health = { status: string };
type ChatMessage = { role: "user" | "assistant"; text: string };
type A2UIAction = { type: string; [k: string]: unknown };

function newRequestId(): string {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const cryptoAny = globalThis.crypto as any;
  if (cryptoAny?.randomUUID) return cryptoAny.randomUUID();
  return String(Date.now());
}

export default function HomePage() {
  const apiBaseUrl = useMemo(
    () => process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000",
    []
  );
  const wsUrl = useMemo(
    () => process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/realtime",
    []
  );

  const [apiHealth, setApiHealth] = useState<Health | null>(null);
  const [wsState, setWsState] = useState<string>("disconnected");
  const [sessionId, setSessionId] = useState<string>("");
  const [input, setInput] = useState<string>("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [actions, setActions] = useState<A2UIAction[]>([]);

  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    let cancelled = false;

    fetch(`${apiBaseUrl}/health`)
      .then((r) => r.json())
      .then((data) => {
        if (!cancelled) setApiHealth(data);
      })
      .catch(() => {
        if (!cancelled) setApiHealth({ status: "error" });
      });

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;
    ws.onopen = () => {
      setWsState("connected");
      ws.send(JSON.stringify({ type: "ping", requestId: newRequestId() }));
    };

    ws.onmessage = (event) => {
      const raw = String(event.data);
      try {
        const payload = JSON.parse(raw) as { type?: string; [k: string]: unknown };
        const type = payload.type;
        if (type === "session.created" && typeof payload.sessionId === "string") {
          setSessionId(payload.sessionId);
          return;
        }
        if (type === "chat.message" && typeof payload.message === "string") {
          setMessages((prev) => [...prev, { role: "assistant", text: payload.message }]);
          return;
        }
        if (type === "a2ui.action" && payload.action && typeof payload.action === "object") {
          setActions((prev) => [...prev, payload.action as A2UIAction]);
          return;
        }
      } catch {
        // ignore non-JSON
      }
    };

    ws.onerror = () => setWsState("error");
    ws.onclose = () => setWsState("closed");

    return () => {
      cancelled = true;
      ws.close();
      wsRef.current = null;
    };
  }, [apiBaseUrl, wsUrl]);

  function sendChat() {
    const ws = wsRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    const text = input.trim();
    if (!text) return;

    setMessages((prev) => [...prev, { role: "user", text }]);
    setInput("");

    ws.send(
      JSON.stringify({
        type: "chat.send",
        sessionId: sessionId || undefined,
        message: text,
        requestId: newRequestId(),
      })
    );
  }

  return (
    <main>
      <h1>trainer2 — Phase 0/003 (WS ready)</h1>
      <p>
        API health: <strong>{apiHealth?.status ?? "loading"}</strong>
      </p>
      <p>
        WS state: <strong>{wsState}</strong>
      </p>
      <p>
        Session: <strong>{sessionId || "(none yet)"}</strong>
      </p>

      <div style={{ marginTop: 16, maxWidth: 720 }}>
        <h2>Chat</h2>
        <div
          style={{
            border: "1px solid #ddd",
            padding: 12,
            minHeight: 160,
            marginBottom: 12,
            whiteSpace: "pre-wrap",
          }}
        >
          {messages.length === 0 ? (
            <div style={{ color: "#666" }}>Send a message to test.</div>
          ) : (
            messages.map((m, idx) => (
              <div key={idx} style={{ marginBottom: 8 }}>
                <strong>{m.role}:</strong> {m.text}
              </div>
            ))
          )}
        </div>

        <div style={{ display: "flex", gap: 8 }}>
          <input
            style={{ flex: 1, padding: 8 }}
            value={input}
            placeholder="Type a message…"
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") sendChat();
            }}
          />
          <button style={{ padding: "8px 12px" }} onClick={sendChat}>
            Send
          </button>
        </div>

        <h2 style={{ marginTop: 16 }}>A2UI actions (debug)</h2>
        <pre style={{ border: "1px solid #eee", padding: 12, overflowX: "auto" }}>
          {JSON.stringify(actions, null, 2)}
        </pre>
      </div>
    </main>
  );
}
