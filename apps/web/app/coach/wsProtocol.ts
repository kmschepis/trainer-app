export type WsState = "disconnected" | "connecting" | "connected" | "closed" | "error";

export type ClientRunMessage = {
  id: string;
  role: "user";
  content: string;
};

export type ClientRunEnvelope = {
  threadId: string;
  runId: string;
  messages: ClientRunMessage[];
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
      type: "TOOL_CALL_STARTED";
      toolName?: string;
      label?: string;
    }
  | {
      type: "TOOL_CALL_RESULT";
      toolName?: string;
      label?: string;
    }
  | {
      type: "TEXT_MESSAGE_CHUNK";
      delta: string;
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
      type === "RUN_FINISHED" ||
      type === "RUN_ERROR" ||
      type === "TOOL_CALL_STARTED" ||
      type === "TOOL_CALL_RESULT" ||
      type === "CUSTOM"
    ) {
      return record as unknown as ServerEvent;
    }

    return null;
  } catch {
    return null;
  }
}
