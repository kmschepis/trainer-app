"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import { ChatComposer } from "./components/ChatComposer";
import { ChatHeader } from "./components/ChatHeader";
import { ChatMessages } from "./components/ChatMessages";
import { OnboardingDrawer } from "./components/OnboardingDrawer";
import { Toast } from "./components/Toast";
import { defaultOnboardingDraft, mergeOnboardingDraft } from "./lib/onboarding";
import type { A2UIAction, ChatMessage, OnboardingDraft } from "./types";

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

  const [wsState, setWsState] = useState<string>("disconnected");
  const [sessionId, setSessionId] = useState<string>("");
  const [input, setInput] = useState<string>("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      text: "Coach here. Tell me what you want to train today.",
    },
  ]);
  const [isSending, setIsSending] = useState<boolean>(false);

  const [hasProfile, setHasProfile] = useState<boolean>(false);
  const [toast, setToast] = useState<string>("");

  const [isOnboardingOpen, setIsOnboardingOpen] = useState<boolean>(false);
  const [onboardingDraft, setOnboardingDraft] = useState<OnboardingDraft>(
    defaultOnboardingDraft()
  );

  const wsRef = useRef<WebSocket | null>(null);
  const scrollRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    let cancelled = false;

    fetch(`${apiBaseUrl}/state`)
      .then((r) => r.json())
      .then((data: unknown) => {
        if (cancelled) return;
        const snapshot = (data as { snapshot?: { profile?: unknown } })?.snapshot;
        setHasProfile(Boolean(snapshot?.profile));
      })
      .catch(() => {
        if (cancelled) return;
        setHasProfile(false);
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
          setIsSending(false);
          setMessages((prev: ChatMessage[]) => [
            ...prev,
            { role: "assistant", text: payload.message },
          ]);
          return;
        }

        if (type === "a2ui.action" && payload.action && typeof payload.action === "object") {
          const action = payload.action as A2UIAction;
          if (action.type === "ui.onboarding.open") {
            setIsOnboardingOpen(true);
            if (action.draft) {
              setOnboardingDraft((prev: OnboardingDraft) =>
                mergeOnboardingDraft(prev, action.draft ?? {})
              );
            }
            return;
          }
          if (action.type === "ui.onboarding.patch") {
            setOnboardingDraft((prev: OnboardingDraft) =>
              mergeOnboardingDraft(prev, action.patch ?? {})
            );
            return;
          }
          if (action.type === "ui.onboarding.close") {
            setIsOnboardingOpen(false);
            return;
          }
          if (action.type === "ui.toast") {
            setToast(String(action.message ?? ""));
            return;
          }
          return;
        }
      } catch {
        // ignore non-JSON
      }
    };

    ws.onerror = () => {
      setIsSending(false);
      setWsState("error");
    };
    ws.onclose = () => {
      setIsSending(false);
      setWsState("closed");
    };

    return () => {
      cancelled = true;
      ws.close();
      wsRef.current = null;
    };
  }, [apiBaseUrl, wsUrl]);

  useEffect(() => {
    if (!toast) return;
    const t = window.setTimeout(() => setToast(""), 2500);
    return () => window.clearTimeout(t);
  }, [toast]);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }, [messages, isSending]);

  function sendChat() {
    const ws = wsRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    const text = input.trim();
    if (!text) return;

    setMessages((prev: ChatMessage[]) => [...prev, { role: "user", text }]);
    setInput("");
    setIsSending(true);

    ws.send(
      JSON.stringify({
        type: "chat.send",
        sessionId: sessionId || undefined,
        message: text,
        context: {
          hasProfile,
          onboarding: {
            open: isOnboardingOpen,
            draft: onboardingDraft,
          },
        },
        requestId: newRequestId(),
      })
    );
  }

  async function submitOnboarding() {
    // UI-triggered submit. We tell the coach (agent) and include the form draft as context.
    // The backend will persist `UserOnboarded` via an agent-driven action.
    if (wsState !== "connected") return;
    const ws = wsRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    setMessages((prev: ChatMessage[]) => [
      ...prev,
      { role: "user", text: "Submitted onboarding form for review." },
    ]);
    setIsSending(true);

    ws.send(
      JSON.stringify({
        type: "chat.send",
        sessionId: sessionId || undefined,
        message: "ONBOARDING_SUBMIT",
        context: {
          hasProfile,
          onboarding: {
            open: true,
            draft: onboardingDraft,
            submit: true,
          },
        },
        requestId: newRequestId(),
      })
    );
  }

  return (
    <main className="relative flex min-h-screen w-full items-center justify-center bg-black p-4">
      <Toast message={toast} />

      <section className="relative flex h-[92vh] w-full max-w-3xl flex-col overflow-hidden rounded-3xl border border-zinc-900 bg-zinc-950">
        <ChatHeader wsState={wsState} sessionId={sessionId} hasProfile={hasProfile} />
        <ChatMessages messages={messages} isSending={isSending} scrollRef={scrollRef} />
        <ChatComposer wsState={wsState} input={input} setInput={setInput} onSend={sendChat} />
      </section>
      <OnboardingDrawer
        open={isOnboardingOpen}
        draft={onboardingDraft}
        setDraft={setOnboardingDraft}
        onClose={() => setIsOnboardingOpen(false)}
        onSubmit={submitOnboarding}
        submitDisabled={wsState !== "connected"}
      />
    </main>
  );
}
