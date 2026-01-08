import { Dumbbell } from "lucide-react";

type ChatHeaderProps = {
  wsState: string;
  sessionId: string;
};

export function ChatHeader({ wsState, sessionId }: ChatHeaderProps) {
  return (
    <header className="flex items-center justify-between border-b border-zinc-900 px-5 py-4">
      <div className="flex items-center gap-3">
        <div className="rounded-xl bg-red-600 p-2">
          <Dumbbell className="h-4 w-4 text-white" />
        </div>
        <div>
          <div className="text-sm font-black uppercase tracking-tight text-white">
            Iron Coach
          </div>
          <div className="text-xs text-zinc-500">
            WS: {wsState}
            {sessionId ? ` • ${sessionId}` : ""}
          </div>
        </div>
      </div>
      <div
        className={`h-2 w-2 rounded-full ${
          wsState === "connected"
            ? "bg-emerald-500"
            : wsState === "error"
              ? "bg-red-500"
              : "bg-zinc-700"
        }`}
        aria-label={`WebSocket state: ${wsState}`}
        title={`WebSocket state: ${wsState}`}
      />
    </header>
  );
}
