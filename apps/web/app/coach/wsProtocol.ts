export type WsState = "disconnected" | "connecting" | "connected" | "closed" | "error";

export type ClientRunEnvelope = {
  threadId: string;
  runId: string;
  message: string;
  forwardedProps?: Record<string, unknown>;
};

export type ServerEvent =
  | {
      type: "RUN_STARTED";
      threadId?: string;
      runId?: string;
      parentRunId?: string;
    }
  | {
      type: "RUN_STAGED";
      threadId?: string;
      runId?: string;
      payload?: unknown;
    }
  | {
      type: "RUN_STAGE_APPROVED";
      threadId?: string;
      runId?: string;
      payloadEdits?: unknown;
    }
  | {
      type: "RUN_STAGE_DENIED";
      threadId?: string;
      runId?: string;
      reason?: string;
    }
  | {
      type: "RUN_FINISHED";
      threadId?: string;
      runId?: string;
    }
  | {
      type: "RUN_ERROR";
      message?: string;
      threadId?: string;
      runId?: string;
    }
  | {
      type: "TOOL_CALL_PROPOSED";
      threadId?: string;
      runId?: string;
      toolCallId?: string;
      toolName?: string;
      args?: unknown;
      label?: string;
    }
  | {
      type: "TOOL_CALL_APPROVED";
      threadId?: string;
      runId?: string;
      toolCallId?: string;
      argsOverride?: unknown;
    }
  | {
      type: "TOOL_CALL_DENIED";
      threadId?: string;
      runId?: string;
      toolCallId?: string;
      reason?: string;
    }
  | {
      type: "TOOL_CALL_STARTED";
      toolName?: string;
      label?: string;
      toolCallId?: string;
      args?: unknown;
    }
  | {
      type: "TOOL_CALL_RESULT";
      toolName?: string;
      label?: string;
      toolCallId?: string;
      result?: unknown;
    }
  | {
      type: "TEXT_MESSAGE_CHUNK";
      delta: string;
    }
  | {
      type: "ASSISTANT_DRAFT_PROPOSED";
      threadId?: string;
      runId?: string;
      draftText?: string;
      draftA2ui?: unknown;
    }
  | {
      type: "ASSISTANT_FINAL_APPROVED";
      threadId?: string;
      runId?: string;
      finalText?: string;
      finalA2ui?: unknown;
    }
  | {
      type: "ASSISTANT_FINAL_DENIED";
      threadId?: string;
      runId?: string;
      reason?: string;
    }
  | {
      type: "CUSTOM";
      name?: string;
      value?: unknown;
    };

export function parseServerEvent(raw: string): ServerEvent | null {
  try {
    const parsed: unknown = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object") return null;

    const record = parsed as Record<string, unknown>;
    const type = record.type;
    if (typeof type !== "string") return null;

    if (type === "TEXT_MESSAGE_CHUNK") {
      const delta = record.delta;
      if (typeof delta !== "string") return null;
      return { type, delta };
    }

    if (
      type === "RUN_STARTED" ||
      type === "RUN_STAGED" ||
      type === "RUN_STAGE_APPROVED" ||
      type === "RUN_STAGE_DENIED" ||
      type === "RUN_FINISHED" ||
      type === "RUN_ERROR" ||
      type === "TOOL_CALL_PROPOSED" ||
      type === "TOOL_CALL_APPROVED" ||
      type === "TOOL_CALL_DENIED" ||
      type === "TOOL_CALL_STARTED" ||
      type === "TOOL_CALL_RESULT" ||
      type === "ASSISTANT_DRAFT_PROPOSED" ||
      type === "ASSISTANT_FINAL_APPROVED" ||
      type === "ASSISTANT_FINAL_DENIED" ||
      type === "CUSTOM"
    ) {
      return record as unknown as ServerEvent;
    }

    return null;
  } catch {
    return null;
  }
}
