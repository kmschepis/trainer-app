"use client";

import { useEffect, useMemo, useState } from "react";

type Health = { status: string };

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
  const [lastMessage, setLastMessage] = useState<string>("");

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
    ws.onopen = () => {
      setWsState("connected");
      ws.send("hello");
    };
    ws.onmessage = (event) => setLastMessage(String(event.data));
    ws.onerror = () => setWsState("error");
    ws.onclose = () => setWsState("closed");

    return () => {
      cancelled = true;
      ws.close();
    };
  }, [apiBaseUrl, wsUrl]);

  return (
    <main>
      <h1>trainer2 — Phase 0</h1>
      <p>
        API health: <strong>{apiHealth?.status ?? "loading"}</strong>
      </p>
      <p>
        WS state: <strong>{wsState}</strong>
      </p>
      <p>
        WS last message: <strong>{lastMessage || "(none)"}</strong>
      </p>
    </main>
  );
}
