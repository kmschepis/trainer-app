import type { ChangeEvent, FormEvent, KeyboardEvent } from "react";
import { Send } from "lucide-react";

type ChatComposerProps = {
  wsState: string;
  input: string;
  setInput: (next: string) => void;
  onSend: () => void;
};

export function ChatComposer({ wsState, input, setInput, onSend }: ChatComposerProps) {
  return (
    <form
      className="border-t border-zinc-900 bg-zinc-950 p-4"
      onSubmit={(e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        onSend();
      }}
    >
      <div className="relative">
        <input
          className="w-full rounded-2xl border border-zinc-800 bg-zinc-900 py-3 pl-4 pr-11 text-sm text-zinc-100 placeholder:text-zinc-500 focus:border-red-500 focus:outline-none"
          value={input}
          placeholder={wsState === "connected" ? "Talk to coach…" : "Connecting…"}
          disabled={wsState !== "connected"}
          onChange={(e: ChangeEvent<HTMLInputElement>) => setInput(e.target.value)}
          onKeyDown={(e: KeyboardEvent<HTMLInputElement>) => {
            if (e.key === "Enter") onSend();
          }}
        />
        <button
          type="submit"
          className="absolute right-3 top-1/2 -translate-y-1/2 rounded-lg p-1 text-red-500 hover:text-red-400 disabled:opacity-50"
          disabled={wsState !== "connected"}
          aria-label="Send"
          title="Send"
        >
          <Send className="h-5 w-5" />
        </button>
      </div>
    </form>
  );
}
