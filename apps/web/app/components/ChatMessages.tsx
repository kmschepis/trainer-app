import { Loader2 } from "lucide-react";

import type { ChatMessage } from "../types";

type ChatMessagesProps = {
  messages: ChatMessage[];
  isSending: boolean;
  scrollRef: React.RefObject<HTMLDivElement | null>;
};

export function ChatMessages({ messages, isSending, scrollRef }: ChatMessagesProps) {
  return (
    <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto p-5">
      {messages.map((m: ChatMessage, idx: number) => (
        <div
          key={idx}
          className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
        >
          <div
            className={`max-w-[85%] whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm leading-relaxed ${
              m.role === "user"
                ? "bg-red-600 text-white"
                : "border border-zinc-800 bg-zinc-900 text-zinc-100"
            }`}
          >
            {m.text}
          </div>
        </div>
      ))}

      {isSending ? (
        <div className="flex items-center gap-2 text-xs font-semibold tracking-wide text-red-500">
          <Loader2 className="h-4 w-4 animate-spin" />
          Coach is thinking…
        </div>
      ) : null}
    </div>
  );
}
