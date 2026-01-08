"use client";

import { useMemo, useState } from "react";
import { useSession } from "next-auth/react";

import { ChatComposer } from "../components/ChatComposer";
import { ChatHeader } from "../components/ChatHeader";
import { ChatMessages } from "../components/ChatMessages";
import { UserMenu } from "../components/UserMenu";
import { useCoachChat } from "./useCoachChat";

import type { ChatMessage } from "../types";

export function CoachClient() {
  const { data: session } = useSession();
  const idToken = (session as unknown as { idToken?: string } | null)?.idToken;
  const sessionEmail = session?.user?.email ?? "";

  const wsUrl = useMemo(
    () => process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/realtime",
    []
  );
  const [input, setInput] = useState<string>("");

  const threadStorageKey = useMemo(() => {
    const keyPart = sessionEmail || "default";
    return `trainer2.threadId.${keyPart}`;
  }, [sessionEmail]);

  const { wsState, threadId, messages, isSending, substatus, scrollRef, sendUserMessage } =
    useCoachChat({ idToken, wsUrl, threadStorageKey });

  function sendChat() {
    const normalized = input.replace(/\r\n/g, "\n").trimEnd();
    if (!normalized.trim()) return;
    setInput("");
    sendUserMessage(normalized);
  }

  return (
    <main className="relative flex min-h-screen w-full items-center justify-center bg-black p-4">
      <div className="absolute right-6 top-6">
        <UserMenu />
      </div>

      <section className="relative flex h-[92vh] w-full max-w-3xl flex-col overflow-hidden rounded-3xl border border-zinc-900 bg-zinc-950">
        <ChatHeader wsState={wsState} sessionId={threadId} />
        <ChatMessages messages={messages} isSending={isSending} substatus={substatus} scrollRef={scrollRef} />
        <ChatComposer wsState={wsState} input={input} setInput={setInput} onSend={sendChat} />
      </section>
    </main>
  );
}
