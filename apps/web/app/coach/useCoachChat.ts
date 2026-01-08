"use client";

import { useEffect, useRef, useState } from "react";

import type { ChatMessage } from "../types";
import type { ClientRunEnvelope, WsState } from "./wsProtocol";
import { parseServerEvent } from "./wsProtocol";

function newRequestId(): string {
  if (typeof globalThis.crypto?.randomUUID === "function") return globalThis.crypto.randomUUID();
  return String(Date.now());
}

function withQueryParam(url: string, key: string, value: string): string {
  const hasQuery = url.includes("?");
  const sep = hasQuery ? "&" : "?";
  return `${url}${sep}${encodeURIComponent(key)}=${encodeURIComponent(value)}`;
}

type UseCoachChatArgs = {
  idToken: string | undefined;
  wsUrl: string;
};

export function useCoachChat({ idToken, wsUrl }: UseCoachChatArgs) {
  const [wsState, setWsState] = useState<WsState>("disconnected");
  const [threadId, setThreadId] = useState<string>("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState<boolean>(false);
  const [substatus, setSubstatus] = useState<string>("");

  const wsRef = useRef<WebSocket | null>(null);
  const threadIdRef = useRef<string>("");
  const scrollRef = useRef<HTMLDivElement>(null!);

  const runHasToolCallsRef = useRef<boolean>(false);
  const runHasAssistantTextRef = useRef<boolean>(false);

  useEffect(() => {
    if (!idToken) return;

    // Always start a new conversation/thread on login.
    const initialThreadId = newRequestId();
    threadIdRef.current = initialThreadId;
    setThreadId(initialThreadId);

    setMessages([]);

    setWsState("connecting");
    const authedWsUrl = withQueryParam(wsUrl, "token", idToken);
    const ws = new WebSocket(authedWsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setWsState("connected");
      setSubstatus("");
      setIsSending(false);
      setMessages([]);
      runHasToolCallsRef.current = false;
      runHasAssistantTextRef.current = false;
    };

    ws.onmessage = (event) => {
      const raw = String(event.data);
      const evt = parseServerEvent(raw);
      if (!evt) return;

      if (evt.type === "RUN_STARTED") {
          setIsSending(true);
          runHasToolCallsRef.current = false;
          runHasAssistantTextRef.current = false;
          setSubstatus("");
          return;
      }

      if (evt.type === "RUN_FINISHED") {
          setIsSending(false);
          runHasToolCallsRef.current = false;
          runHasAssistantTextRef.current = false;
          setSubstatus("");
          return;
      }

      if (evt.type === "RUN_ERROR") {
          setIsSending(false);
          setSubstatus("");
          const msg = typeof evt.message === "string" ? evt.message : "Run failed";
          setMessages((prev: ChatMessage[]) => [...prev, { role: "assistant", text: `Error: ${msg}` }]);
          return;
      }

      if (evt.type === "TOOL_CALL_STARTED") {
          const toolName = typeof evt.toolName === "string" ? evt.toolName : "";
          const label = typeof evt.label === "string" ? evt.label : "";
          if (toolName) {
            runHasToolCallsRef.current = true;
            setSubstatus(label.trim() ? label.trim() : `Running ${toolName}…`);
          }
          return;
      }

      if (evt.type === "TOOL_CALL_RESULT") {
          const toolName = typeof evt.toolName === "string" ? evt.toolName : "";
          const label = typeof evt.label === "string" ? evt.label : "";
          if (toolName) {
            runHasToolCallsRef.current = true;
            const base = label.trim()
              ? label.trim().replace(/[.…]+$/, "")
              : `Running ${toolName}…`.replace(/…$/, "");
            setSubstatus(`${base} done.`);
          }
          return;
      }

      if (evt.type === "TEXT_MESSAGE_CHUNK") {
          setIsSending(false);
          const delta = evt.delta;

          if (delta.trim() === "OK." && runHasToolCallsRef.current && !runHasAssistantTextRef.current) {
            return;
          }

          runHasAssistantTextRef.current = true;
          setMessages((prev: ChatMessage[]) => [...prev, { role: "assistant", text: delta }]);
          return;
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
      ws.close();
      wsRef.current = null;
    };
  }, [idToken, wsUrl]);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }, [messages, isSending]);

  function sendUserMessage(text: string) {
    const ws = wsRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    const normalized = text.replace(/\r\n/g, "\n").trimEnd();
    if (!normalized.trim()) return;

    setMessages((prev: ChatMessage[]) => [...prev, { role: "user", text: normalized }]);
    setIsSending(true);

    const nextThreadId = threadIdRef.current || threadId || newRequestId();
    threadIdRef.current = nextThreadId;
    if (!threadId) setThreadId(nextThreadId);

    const payload: ClientRunEnvelope = {
      threadId: nextThreadId,
      runId: newRequestId(),
      message: normalized,
      forwardedProps: {},
    };

    ws.send(JSON.stringify(payload));
  }

  return {
    wsState,
    threadId,
    messages,
    isSending,
    substatus,
    scrollRef,
    sendUserMessage,
  };
}
