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

function newId(): string {
  return newRequestId();
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
  const [threadId, setThreadId] = useState<string>("");
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
    };

    ws.onmessage = (event) => {
      const raw = String(event.data);
      try {
        const payload = JSON.parse(raw) as { type?: string; [k: string]: unknown };
        const type = payload.type;
        if (type === "RUN_STARTED") {
          setIsSending(true);
          return;
        }

        if (type === "RUN_FINISHED") {
          setIsSending(false);
          return;
        }

        if (type === "RUN_ERROR") {
          setIsSending(false);
          const msg = typeof payload.message === "string" ? payload.message : "Run failed";
          setToast(msg);
          return;
        }

        if (type === "TEXT_MESSAGE_CHUNK" && typeof payload.delta === "string") {
          setIsSending(false);
          setMessages((prev: ChatMessage[]) => [...prev, { role: "assistant", text: payload.delta }]);
          return;
        }

        if (type === "CUSTOM" && payload.name === "ui.action" && payload.value && typeof payload.value === "object") {
          const action = payload.value as A2UIAction;
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
            // Server-driven close implies the profile was accepted/saved.
            setHasProfile(true);
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

    const nextThreadId = threadId || newId();
    if (!threadId) setThreadId(nextThreadId);

    const uiContext = {
      hasProfile,
      onboarding: {
        open: isOnboardingOpen,
        draft: onboardingDraft,
      },
    };

    ws.send(
      JSON.stringify({
        threadId: nextThreadId,
        runId: newId(),
        state: {},
        messages: [{ id: newId(), role: "user", content: text }],
        tools: [],
        context: [{ description: "uiContext", value: JSON.stringify(uiContext) }],
        forwardedProps: { uiContext },
      })
    );
  }

  async function submitOnboarding() {
    // UI-triggered submit. We tell the coach (agent) and include the form draft as context.
    // The backend will persist `ProfileSaved` (canonical) via tool execution.
    if (wsState !== "connected") return;
    const ws = wsRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    setMessages((prev: ChatMessage[]) => [
      ...prev,
      { role: "user", text: "Submitted onboarding form for review." },
    ]);
    setIsSending(true);

    const nextThreadId = threadId || newId();
    if (!threadId) setThreadId(nextThreadId);

    const uiContext = {
      hasProfile,
      onboarding: {
        open: true,
        draft: onboardingDraft,
        submit: true,
      },
    };

    ws.send(
      JSON.stringify({
        threadId: nextThreadId,
        runId: newId(),
        state: {},
        messages: [{ id: newId(), role: "user", content: "ONBOARDING_SUBMIT" }],
        tools: [],
        context: [{ description: "uiContext", value: JSON.stringify(uiContext) }],
        forwardedProps: { uiContext },
      })
    );
  }

  return (
    <main className="relative flex min-h-screen w-full items-center justify-center bg-black p-4">
      <Toast message={toast} />

      <section className="relative flex h-[92vh] w-full max-w-3xl flex-col overflow-hidden rounded-3xl border border-zinc-900 bg-zinc-950">
        <ChatHeader wsState={wsState} sessionId={threadId} hasProfile={hasProfile} />
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
