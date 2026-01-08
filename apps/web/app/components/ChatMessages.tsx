import { Loader2 } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkBreaks from "remark-breaks";
import remarkGfm from "remark-gfm";

import type { ReactNode } from "react";

import type { ChatMessage } from "../types";

type ChatMessagesProps = {
  messages: ChatMessage[];
  isSending: boolean;
  substatus?: string;
  scrollRef: React.RefObject<HTMLDivElement>;
};

function MarkdownBubble({ text }: { text: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm, remarkBreaks]}
      components={{
        p: ({ children }: { children?: ReactNode }) => (
          <p className="whitespace-pre-wrap last:mb-0">{children}</p>
        ),
        a: ({ href, children }: { href?: string; children?: ReactNode }) => (
          <a
            href={href}
            className="text-red-400 underline hover:text-red-300"
            target="_blank"
            rel="noreferrer"
          >
            {children}
          </a>
        ),
        ul: ({ children }: { children?: ReactNode }) => (
          <ul className="ml-5 list-disc space-y-1">{children}</ul>
        ),
        ol: ({ children }: { children?: ReactNode }) => (
          <ol className="ml-5 list-decimal space-y-1">{children}</ol>
        ),
        li: ({ children }: { children?: ReactNode }) => <li>{children}</li>,
        pre: ({ children }: { children?: ReactNode }) => (
          <pre className="overflow-x-auto rounded-xl border border-zinc-800 bg-zinc-950 p-3">{children}</pre>
        ),
        code: ({
          inline,
          children,
        }: {
          inline?: boolean;
          children?: ReactNode;
        }) => {
          if (inline) {
            return (
              <code className="rounded bg-zinc-950 px-1 py-0.5 font-mono text-[0.85em]">
                {children}
              </code>
            );
          }
          return <code className="font-mono text-[0.85em]">{children}</code>;
        },
        blockquote: ({ children }: { children?: ReactNode }) => (
          <blockquote className="border-l-2 border-zinc-700 pl-3 text-zinc-200">
            {children}
          </blockquote>
        ),
      }}
    >
      {text}
    </ReactMarkdown>
  );
}

export function ChatMessages({ messages, isSending, substatus, scrollRef }: ChatMessagesProps) {
  return (
    <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto p-5">
      {messages.map((m: ChatMessage, idx: number) => (
        <div
          key={idx}
          className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
        >
          <div
            className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
              m.role === "user"
                ? "bg-red-600 text-white"
                : "border border-zinc-800 bg-zinc-900 text-zinc-100"
            }`}
          >
            <MarkdownBubble text={m.text} />
          </div>
        </div>
      ))}

      {isSending ? (
        <div className="space-y-1 text-xs font-semibold tracking-wide text-red-500">
          <div className="flex items-center gap-2">
            <Loader2 className="h-4 w-4 animate-spin" />
            Coach is thinking…
          </div>
          {substatus ? <div className="pl-6 text-[11px] font-medium text-zinc-400">{substatus}</div> : null}
        </div>
      ) : null}
    </div>
  );
}
