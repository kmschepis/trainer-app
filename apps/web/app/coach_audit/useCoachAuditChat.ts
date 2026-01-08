"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import type { ChatMessage } from "../types";
import type { ClientRunEnvelope, ServerEvent, WsState } from "../coach/wsProtocol";
import { parseServerEvent } from "../coach/wsProtocol";

function newRequestId(): string {
  if (typeof globalThis.crypto?.randomUUID === "function") return globalThis.crypto.randomUUID();
  return String(Date.now());
}

function withQueryParam(url: string, key: string, value: string): string {
  const hasQuery = url.includes("?");
  const sep = hasQuery ? "&" : "?";
  return `${url}${sep}${encodeURIComponent(key)}=${encodeURIComponent(value)}`;
}

function safeJsonStringify(value: unknown): string {
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return "";
  }
}

function tryParseJsonObject(text: string): Record<string, unknown> | null {
  try {
    const parsed: unknown = JSON.parse(text);
    if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) return parsed as Record<string, unknown>;
    return null;
  } catch {
    return null;
  }
}

type TimelineItem = {
  id: string;
  ts: string;
  type: string;
  summary?: string;
};

type StagedState = {
  threadId: string;
  runId: string;
  payload: unknown;
};

type DraftState = {
  threadId: string;
  runId: string;
  draftText: string;
};

type PolicyState = {
  autoApproveStage: boolean;
  autoApproveToolCalls: boolean;
  autoApproveAssistant: boolean;
};

type PendingToolCall = {
  toolCallId: string;
  toolName: string;
  label: string;
  argsText: string;
  setArgsText: (next: string) => void;
};

type UseCoachAuditChatArgs = {
  idToken: string | undefined;
  wsUrl: string;
};

const POLICY_KEY = "trainer2.auditPolicy.v2";

export function useCoachAuditChat({ idToken, wsUrl }: UseCoachAuditChatArgs) {
  const [wsState, setWsState] = useState<WsState>("disconnected");
  const [threadId, setThreadId] = useState<string>("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState<boolean>(false);
  const [substatus, setSubstatus] = useState<string>("");

  const wsRef = useRef<WebSocket | null>(null);
  const threadIdRef = useRef<string>("");
  const scrollRef = useRef<HTMLDivElement>(null!);

  const [timeline, setTimeline] = useState<TimelineItem[]>([]);
  const [staged, setStaged] = useState<StagedState | null>(null);
  const [stagedEditText, setStagedEditText] = useState<string>("");

  const activeRunRef = useRef<{ threadId: string; runId: string }>({ threadId: "", runId: "" });

  const [draft, setDraft] = useState<DraftState | null>(null);
  const [draftEditText, setDraftEditText] = useState<string>("");

  const [policy, setPolicyState] = useState<PolicyState>({
    autoApproveStage: true,
    autoApproveToolCalls: true,
    autoApproveAssistant: true,
  });
  const policyRef = useRef<PolicyState>({
    autoApproveStage: true,
    autoApproveToolCalls: true,
    autoApproveAssistant: true,
  });

  const [pendingToolCalls, setPendingToolCalls] = useState<PendingToolCall[]>([]);
  const toolArgsByIdRef = useRef<Map<string, string>>(new Map());

  const authedWsUrl = useMemo(() => {
    const withMode = withQueryParam(wsUrl, "mode", "audit");
    return idToken ? withQueryParam(withMode, "token", idToken) : "";
  }, [idToken, wsUrl]);

  useEffect(() => {
    policyRef.current = policy;
  }, [policy]);

  function addTimeline(type: string, summary?: string) {
    const now = new Date();
    const ts = now.toLocaleTimeString();
    setTimeline((prev) => [...prev, { id: newRequestId(), ts, type, summary }]);
  }

  function wsSend(obj: unknown) {
    const ws = wsRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    ws.send(JSON.stringify(obj));
  }

  useEffect(() => {
    if (!idToken) return;

    // Always start a new conversation/thread on login.
    const initialThreadId = newRequestId();
    threadIdRef.current = initialThreadId;
    setThreadId(initialThreadId);
    setMessages([]);

    const storedPolicy = window.localStorage.getItem(POLICY_KEY);
    if (storedPolicy) {
      try {
        const parsed: unknown = JSON.parse(storedPolicy);
        if (parsed && typeof parsed === "object") {
          const obj = parsed as Record<string, unknown>;
          const next: PolicyState = {
            autoApproveStage: obj.autoApproveStage !== false,
            autoApproveToolCalls: obj.autoApproveToolCalls !== false,
            autoApproveAssistant: obj.autoApproveAssistant !== false,
          };
          setPolicyState(next);
          policyRef.current = next;
        }
      } catch {
        // ignore
      }
    }
  }, [idToken]);

  useEffect(() => {
    if (!idToken) return;
    if (!authedWsUrl) return;

    setWsState("connecting");
    const ws = new WebSocket(authedWsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setWsState("connected");
      setIsSending(false);
      setSubstatus("");
      setMessages([]);
      setTimeline([]);
      setStaged(null);
      setDraft(null);
      setPendingToolCalls([]);
      toolArgsByIdRef.current = new Map();
    };

    ws.onmessage = (event) => {
      const raw = String(event.data);
      const evt = parseServerEvent(raw);
      if (!evt) return;

      addTimeline(evt.type, summarize(evt));

      if (evt.type === "RUN_STARTED") {
        setIsSending(true);
        setSubstatus("");
        if (typeof evt.threadId === "string" && typeof evt.runId === "string") {
          activeRunRef.current = { threadId: evt.threadId, runId: evt.runId };
        }
        return;
      }

      if (evt.type === "RUN_FINISHED") {
        setIsSending(false);
        setSubstatus("");
        setPendingToolCalls([]);
        toolArgsByIdRef.current = new Map();
        activeRunRef.current = { threadId: "", runId: "" };
        return;
      }

      if (evt.type === "RUN_ERROR") {
        setIsSending(false);
        setSubstatus("");
        const msg = typeof evt.message === "string" ? evt.message : "Run failed";
        setMessages((prev) => [...prev, { role: "assistant", text: `Error: ${msg}` }]);
        return;
      }

      if (evt.type === "RUN_STAGED") {
        const t = typeof evt.threadId === "string" ? evt.threadId : threadIdRef.current;
        const r = typeof evt.runId === "string" ? evt.runId : "";
        setStaged({ threadId: t, runId: r, payload: evt.payload });
        setStagedEditText(safeJsonStringify(evt.payload));
        setIsSending(true);
        activeRunRef.current = { threadId: t, runId: r };

        if (policyRef.current.autoApproveStage) {
          wsSend({ type: "RUN_STAGE_APPROVED", threadId: t, runId: r });
        }
        return;
      }

      if (evt.type === "RUN_STAGE_APPROVED" || evt.type === "RUN_STAGE_DENIED") {
        setStaged(null);
        return;
      }

      if (evt.type === "TOOL_CALL_STARTED") {
        const toolName = typeof evt.toolName === "string" ? evt.toolName : "";
        const label = typeof evt.label === "string" ? evt.label : "";
        if (toolName) setSubstatus(label.trim() ? label.trim() : `Running ${toolName}…`);
        return;
      }

      if (evt.type === "TOOL_CALL_RESULT") {
        const toolName = typeof evt.toolName === "string" ? evt.toolName : "";
        const label = typeof evt.label === "string" ? evt.label : "";
        if (toolName) {
          const base = label.trim() ? label.trim().replace(/[.…]+$/, "") : `Running ${toolName}…`.replace(/…$/, "");
          setSubstatus(`${base} done.`);
        }
        return;
      }

      if (evt.type === "TOOL_CALL_PROPOSED") {
        const toolName = typeof evt.toolName === "string" ? evt.toolName : "";
        const label = typeof evt.label === "string" ? evt.label : "";
        const toolCallId = typeof evt.toolCallId === "string" ? evt.toolCallId : "";
        const args = evt.args;

        if (!toolCallId || !toolName) return;

        if (policyRef.current.autoApproveToolCalls) {
          wsSend({ type: "TOOL_CALL_APPROVED", threadId: evt.threadId, runId: evt.runId, toolCallId });
          return;
        }

        const initialArgsText = safeJsonStringify(args ?? {});
        toolArgsByIdRef.current.set(toolCallId, initialArgsText);

        setPendingToolCalls((prev) => {
          const existing = prev.find((p) => p.toolCallId === toolCallId);
          if (existing) return prev;
          return [
            ...prev,
            {
              toolCallId,
              toolName,
              label,
              argsText: initialArgsText,
              setArgsText: (next: string) => {
                toolArgsByIdRef.current.set(toolCallId, next);
                setPendingToolCalls((cur) =>
                  cur.map((c) => (c.toolCallId === toolCallId ? { ...c, argsText: next } : c))
                );
              },
            },
          ];
        });

        return;
      }

      if (evt.type === "TOOL_CALL_APPROVED" || evt.type === "TOOL_CALL_DENIED") {
        const toolCallId = typeof evt.toolCallId === "string" ? evt.toolCallId : "";
        if (!toolCallId) return;
        setPendingToolCalls((prev) => prev.filter((p) => p.toolCallId !== toolCallId));
        toolArgsByIdRef.current.delete(toolCallId);
        return;
      }

      if (evt.type === "ASSISTANT_DRAFT_PROPOSED") {
        const t = typeof evt.threadId === "string" ? evt.threadId : threadIdRef.current;
        const r = typeof evt.runId === "string" ? evt.runId : "";
        const text = typeof evt.draftText === "string" ? evt.draftText : "";

        if (policyRef.current.autoApproveAssistant) {
          wsSend({ type: "ASSISTANT_FINAL_APPROVED", threadId: t, runId: r });
          return;
        }

        setDraft({ threadId: t, runId: r, draftText: text });
        setDraftEditText(text);
        return;
      }

      if (evt.type === "ASSISTANT_FINAL_APPROVED" || evt.type === "ASSISTANT_FINAL_DENIED") {
        setDraft(null);
        return;
      }

      if (evt.type === "TEXT_MESSAGE_CHUNK") {
        setIsSending(false);
        setMessages((prev) => [...prev, { role: "assistant", text: evt.delta }]);
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
  }, [authedWsUrl, idToken]);

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

    setMessages((prev) => [...prev, { role: "user", text: normalized }]);
    setIsSending(true);

    const nextThreadId = threadIdRef.current || threadId || newRequestId();
    threadIdRef.current = nextThreadId;
    if (!threadId) setThreadId(nextThreadId);

    const payload: ClientRunEnvelope = {
      threadId: nextThreadId,
      runId: newRequestId(),
      message: normalized,
      forwardedProps: {
        auditPolicy: policyRef.current,
      },
    };

    ws.send(JSON.stringify(payload));
  }

  function approveStage(opts?: { useEdits?: boolean }) {
    if (!staged) return;

    if (opts?.useEdits) {
      const parsed = tryParseJsonObject(stagedEditText);
      const payload = parsed ?? {};

      const message = typeof (payload as any).message === "string" ? String((payload as any).message) : undefined;
      const context = typeof (payload as any).context === "object" && (payload as any).context ? (payload as any).context : undefined;

      wsSend({ type: "RUN_STAGE_APPROVED", threadId: staged.threadId, runId: staged.runId, payloadEdits: { message, context } });
      return;
    }

    wsSend({ type: "RUN_STAGE_APPROVED", threadId: staged.threadId, runId: staged.runId });
  }

  function denyStage() {
    if (!staged) return;
    wsSend({ type: "RUN_STAGE_DENIED", threadId: staged.threadId, runId: staged.runId });
  }

  function approveTool(toolCallId: string, argsText: string) {
    if (!toolCallId) return;
    const parsed = tryParseJsonObject(argsText);
    const active = activeRunRef.current;
    wsSend({ type: "TOOL_CALL_APPROVED", threadId: active.threadId || threadIdRef.current, runId: active.runId || "", toolCallId, argsOverride: parsed ?? undefined });
  }

  function denyTool(toolCallId: string) {
    const active = activeRunRef.current;
    wsSend({ type: "TOOL_CALL_DENIED", threadId: active.threadId || threadIdRef.current, runId: active.runId || "", toolCallId });
  }

  function approveDraft(opts?: { useEdits?: boolean }) {
    if (!draft) return;
    if (opts?.useEdits) {
      wsSend({ type: "ASSISTANT_FINAL_APPROVED", threadId: draft.threadId, runId: draft.runId, finalText: draftEditText });
      return;
    }
    wsSend({ type: "ASSISTANT_FINAL_APPROVED", threadId: draft.threadId, runId: draft.runId });
  }

  function denyDraft() {
    if (!draft) return;
    wsSend({ type: "ASSISTANT_FINAL_DENIED", threadId: draft.threadId, runId: draft.runId });
  }

  function setPolicy(next: PolicyState) {
    setPolicyState(next);
    window.localStorage.setItem(POLICY_KEY, JSON.stringify(next));
  }

  return {
    wsState,
    threadId,
    messages,
    isSending,
    substatus,
    scrollRef,
    sendUserMessage,
    timeline,
    staged,
    stagedEditText,
    setStagedEditText,
    approveStage,
    denyStage,
    draft,
    draftEditText,
    setDraftEditText,
    approveDraft,
    denyDraft,
    policy,
    setPolicy,
    pendingToolCalls,
    approveTool,
    denyTool,
  };
}

function summarize(evt: ServerEvent): string {
  if (evt.type === "RUN_ERROR") return typeof evt.message === "string" ? evt.message : "";
  if (evt.type === "TOOL_CALL_PROPOSED") {
    const name = typeof evt.toolName === "string" ? evt.toolName : "";
    return name ? `(${name})` : "";
  }
  if (evt.type === "TOOL_CALL_STARTED" || evt.type === "TOOL_CALL_RESULT") {
    const name = typeof evt.toolName === "string" ? evt.toolName : "";
    return name ? `(${name})` : "";
  }
  if (evt.type === "ASSISTANT_DRAFT_PROPOSED") return "draft ready";
  return "";
}
