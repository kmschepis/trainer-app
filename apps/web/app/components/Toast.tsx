type ToastProps = {
  message: string;
};

export function Toast({ message }: ToastProps) {
  if (!message) return null;

  return (
    <div className="pointer-events-none absolute top-4 z-50 rounded-full border border-zinc-800 bg-zinc-950 px-4 py-2 text-xs font-semibold text-zinc-200">
      {message}
    </div>
  );
}
