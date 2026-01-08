"use client";

import { useMemo, useState } from "react";
import { useSession } from "next-auth/react";

import { ChatComposer } from "../components/ChatComposer";
import { ChatHeader } from "../components/ChatHeader";
import { ChatMessages } from "../components/ChatMessages";
import { UserMenu } from "../components/UserMenu";

import { useCoachAuditChat } from "./useCoachAuditChat";
import { JsonExplorer } from "./JsonExplorer";

function CollapsibleSection({
  title,
  open,
  onToggle,
  children,
}: {
  title: string;
  open: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-2xl border border-zinc-900 bg-zinc-950">
      <button
        type="button"
        className="flex w-full items-center justify-between px-4 py-3 text-left"
        onClick={onToggle}
        aria-expanded={open}
      >
        <div className="text-xs font-semibold text-zinc-200">{title}</div>
        <div className="text-xs text-zinc-500">{open ? "Hide" : "Show"}</div>
      </button>
      {open ? <div className="px-4 pb-4">{children}</div> : null}
    </section>
  );
}

export function CoachAuditClient() {
  const { data: session } = useSession();
  const idToken = (session as unknown as { idToken?: string } | null)?.idToken;

  const wsUrl = useMemo(
    () => process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/realtime",
    []
  );

  const [input, setInput] = useState<string>("");

  const [openStage, setOpenStage] = useState(true);
  const [openTimeline, setOpenTimeline] = useState(true);
  const [openPolicy, setOpenPolicy] = useState(true);
  const [openTool, setOpenTool] = useState(true);
  const [openAssistant, setOpenAssistant] = useState(true);

  const {
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
  } = useCoachAuditChat({ idToken, wsUrl });

  function sendChat() {
    const normalized = input.replace(/\r\n/g, "\n").trimEnd();
    if (!normalized.trim()) return;
    setInput("");
    sendUserMessage(normalized);
  }

  const latestTool = pendingToolCalls.length ? pendingToolCalls[pendingToolCalls.length - 1] : null;

  return (
    <main className="relative flex min-h-screen w-full bg-black p-4">
      <div className="absolute right-6 top-6">
        <UserMenu />
      </div>

      <div className="mx-auto flex h-[92vh] w-full max-w-6xl gap-4">
        <section className="flex w-1/2 flex-col overflow-hidden rounded-3xl border border-zinc-900 bg-zinc-950">
          <ChatHeader wsState={wsState} sessionId={threadId} />
          <ChatMessages
            messages={messages}
            isSending={isSending}
            substatus={substatus}
            scrollRef={scrollRef}
          />
          <ChatComposer wsState={wsState} input={input} setInput={setInput} onSend={sendChat} />
        </section>

        <aside className="flex w-1/2 flex-col gap-3 overflow-hidden rounded-3xl border border-zinc-900 bg-zinc-950 p-5">
          <div>
            <div className="text-sm font-black uppercase tracking-tight text-white">Audit console</div>
            <div className="mt-1 text-xs text-zinc-500">Approve context, tools, and output.</div>
          </div>

          <CollapsibleSection title="Run staging" open={openStage} onToggle={() => setOpenStage((v) => !v)}>
            {staged ? (
              <div className="space-y-3">
                <label className="flex cursor-pointer items-center gap-2 text-xs text-zinc-300">
                  <input
                    type="checkbox"
                    className="h-4 w-4 accent-red-500"
                    checked={policy.autoApproveStage}
                    onChange={(e) => setPolicy({ ...policy, autoApproveStage: e.target.checked })}
                  />
                  <span>Auto-approve staged run</span>
                </label>
                <JsonExplorer
                  title="Staged payload"
                  text={stagedEditText}
                  onTextChange={setStagedEditText}
                  heightClassName="h-44"
                />
                <div className="flex gap-2">
                  <button
                    className="rounded-xl bg-emerald-600 px-3 py-2 text-xs font-semibold text-white hover:bg-emerald-500"
                    onClick={() => approveStage()}
                  >
                    Approve + Send
                  </button>
                  <button
                    className="rounded-xl border border-zinc-800 bg-zinc-900 px-3 py-2 text-xs font-semibold text-zinc-100 hover:bg-zinc-800"
                    onClick={() => approveStage({ useEdits: true })}
                  >
                    Edit payload + Send
                  </button>
                  <button
                    className="rounded-xl border border-red-800 bg-zinc-950 px-3 py-2 text-xs font-semibold text-red-400 hover:bg-zinc-900"
                    onClick={() => denyStage()}
                  >
                    Deny
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-xs text-zinc-500">No staged run.</div>
            )}
          </CollapsibleSection>

          <CollapsibleSection title="Event timeline" open={openTimeline} onToggle={() => setOpenTimeline((v) => !v)}>
            <div className="max-h-40 space-y-1 overflow-y-auto pr-1 text-[11px] text-zinc-400">
              {timeline.map((t) => (
                <div key={t.id} className="flex gap-2">
                  <span className="text-zinc-600">{t.ts}</span>
                  <span className="text-zinc-200">{t.type}</span>
                  {t.summary ? <span className="text-zinc-500">{t.summary}</span> : null}
                </div>
              ))}
              {!timeline.length ? <div className="text-zinc-500">No events yet.</div> : null}
            </div>
          </CollapsibleSection>

          <CollapsibleSection title="Policies (auto-approve)" open={openPolicy} onToggle={() => setOpenPolicy((v) => !v)}>
            <div className="space-y-2 text-xs text-zinc-300">
              <label className="flex cursor-pointer items-center gap-2">
                <input
                  type="checkbox"
                  className="h-4 w-4 accent-red-500"
                  checked={policy.autoApproveStage}
                  onChange={(e) => setPolicy({ ...policy, autoApproveStage: e.target.checked })}
                />
                <span>Auto-approve staged run</span>
              </label>

              <label className="flex cursor-pointer items-center gap-2">
                <input
                  type="checkbox"
                  className="h-4 w-4 accent-red-500"
                  checked={policy.autoApproveToolCalls}
                  onChange={(e) => setPolicy({ ...policy, autoApproveToolCalls: e.target.checked })}
                />
                <span>Auto-approve tool calls</span>
              </label>

              <label className="flex cursor-pointer items-center gap-2">
                <input
                  type="checkbox"
                  className="h-4 w-4 accent-red-500"
                  checked={policy.autoApproveAssistant}
                  onChange={(e) => setPolicy({ ...policy, autoApproveAssistant: e.target.checked })}
                />
                <span>Auto-approve assistant response</span>
              </label>
            </div>
          </CollapsibleSection>

          <div className="min-h-0 flex-1">
          <CollapsibleSection title="Tool call (args)" open={openTool} onToggle={() => setOpenTool((v) => !v)}>
            {latestTool ? (
              <div className="space-y-3">
                <label className="flex cursor-pointer items-center gap-2 text-xs text-zinc-300">
                  <input
                    type="checkbox"
                    className="h-4 w-4 accent-red-500"
                    checked={policy.autoApproveToolCalls}
                    onChange={(e) => setPolicy({ ...policy, autoApproveToolCalls: e.target.checked })}
                  />
                  <span>Auto-approve tool calls</span>
                </label>
                <div className="text-[11px] text-zinc-400">
                  <span className="text-zinc-200">{latestTool.toolName}</span>
                  {latestTool.label ? <span className="text-zinc-500"> — {latestTool.label}</span> : null}
                </div>
                <JsonExplorer
                  title="Tool args"
                  text={latestTool.argsText}
                  onTextChange={latestTool.setArgsText}
                  heightClassName={openStage || openTimeline || openPolicy || openAssistant ? "h-40" : "h-[22rem]"}
                />
                <div className="flex gap-2">
                  <button
                    className="rounded-xl bg-emerald-600 px-3 py-2 text-xs font-semibold text-white hover:bg-emerald-500"
                    onClick={() => approveTool(latestTool.toolCallId, latestTool.argsText)}
                  >
                    Approve
                  </button>
                  <button
                    className="rounded-xl border border-red-800 bg-zinc-950 px-3 py-2 text-xs font-semibold text-red-400 hover:bg-zinc-900"
                    onClick={() => denyTool(latestTool.toolCallId)}
                  >
                    Deny
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-xs text-zinc-500">No tool awaiting approval.</div>
            )}
          </CollapsibleSection>
          </div>

          <CollapsibleSection title="Assistant response" open={openAssistant} onToggle={() => setOpenAssistant((v) => !v)}>
            {draft ? (
              <div className="space-y-3">
                <label className="flex cursor-pointer items-center gap-2 text-xs text-zinc-300">
                  <input
                    type="checkbox"
                    className="h-4 w-4 accent-red-500"
                    checked={policy.autoApproveAssistant}
                    onChange={(e) => setPolicy({ ...policy, autoApproveAssistant: e.target.checked })}
                  />
                  <span>Auto-approve assistant response</span>
                </label>
                <textarea
                  className="h-40 w-full resize-none rounded-xl border border-zinc-800 bg-zinc-900 p-3 text-[12px] text-zinc-100 focus:border-red-500 focus:outline-none"
                  value={draftEditText}
                  onChange={(e) => setDraftEditText(e.target.value)}
                />
                <div className="flex gap-2">
                  <button
                    className="rounded-xl bg-emerald-600 px-3 py-2 text-xs font-semibold text-white hover:bg-emerald-500"
                    onClick={() => approveDraft()}
                  >
                    Approve
                  </button>
                  <button
                    className="rounded-xl border border-zinc-800 bg-zinc-900 px-3 py-2 text-xs font-semibold text-zinc-100 hover:bg-zinc-800"
                    onClick={() => approveDraft({ useEdits: true })}
                  >
                    Approve (edited)
                  </button>
                  <button
                    className="rounded-xl border border-red-800 bg-zinc-950 px-3 py-2 text-xs font-semibold text-red-400 hover:bg-zinc-900"
                    onClick={() => denyDraft()}
                  >
                    Deny
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-xs text-zinc-500">No draft awaiting approval.</div>
            )}
          </CollapsibleSection>
        </aside>
      </div>
    </main>
  );
}
