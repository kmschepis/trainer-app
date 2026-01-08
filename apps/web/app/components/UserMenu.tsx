"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { signOut, useSession } from "next-auth/react";

function UserIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="h-5 w-5"
      aria-hidden="true"
    >
      <path
        d="M12 12a4.25 4.25 0 1 0 0-8.5A4.25 4.25 0 0 0 12 12Z"
        stroke="currentColor"
        strokeWidth="1.5"
      />
      <path
        d="M4.5 20.5c1.6-4 5-6 7.5-6s5.9 2 7.5 6"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
    </svg>
  );
}

export function UserMenu() {
  const { data: session, status } = useSession();
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement | null>(null);

  const email = session?.user?.email ?? "";
  const name = session?.user?.name ?? "";
  const label = name || email || "Signed in";

  useEffect(() => {
    function onPointerDown(e: MouseEvent) {
      const el = rootRef.current;
      if (!el) return;
      if (el.contains(e.target as Node)) return;
      setOpen(false);
    }

    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }

    document.addEventListener("mousedown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("mousedown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, []);

  if (status === "loading") {
    return (
      <button
        className="inline-flex items-center justify-center rounded-full border border-zinc-800 bg-zinc-950 p-2 text-zinc-200"
        disabled
        aria-label="User menu"
      >
        <UserIcon />
      </button>
    );
  }

  if (!session) return null;

  return (
    <div className="relative" ref={rootRef}>
      <button
        className="inline-flex items-center justify-center rounded-full border border-zinc-800 bg-zinc-950 p-2 text-zinc-200 hover:bg-zinc-900"
        onClick={() => setOpen((v: boolean) => !v)}
        aria-label="User menu"
        aria-haspopup="menu"
        aria-expanded={open}
      >
        <UserIcon />
      </button>

      {open ? (
        <div
          className="absolute right-0 mt-2 w-64 overflow-hidden rounded-2xl border border-zinc-900 bg-zinc-950"
          role="menu"
        >
          <div className="px-4 py-3">
            <div className="text-xs text-zinc-500">Signed in as</div>
            <div className="pt-1 text-sm text-zinc-100">{label}</div>
            {name && email ? <div className="pt-0.5 text-xs text-zinc-400">{email}</div> : null}
          </div>

          <div className="h-px bg-zinc-900" />

          <Link
            className="block w-full px-4 py-2 text-left text-sm text-zinc-200 hover:bg-zinc-900"
            role="menuitem"
            href="/coach_audit"
            onClick={() => setOpen(false)}
          >
            Coach audit console
          </Link>

          <button
            className="w-full px-4 py-2 text-left text-sm text-zinc-200 hover:bg-zinc-900"
            role="menuitem"
            onClick={() => signOut({ callbackUrl: "/" })}
          >
            Sign out
          </button>
        </div>
      ) : null}
    </div>
  );
}
