"use client";

import { useState } from "react";
import Link from "next/link";
import { signIn, signOut, useSession } from "next-auth/react";

export function AuthButtons() {
  const { data: session, status } = useSession();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  if (status === "loading") {
    return (
      <button
        className="rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-2 text-sm text-zinc-200"
        disabled
      >
        Loading…
      </button>
    );
  }

  if (session) {
    return (
      <button
        className="rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-2 text-sm text-zinc-200 hover:bg-zinc-900"
        onClick={() => signOut({ callbackUrl: "/" })}
      >
        Sign out
      </button>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      <button
        className="rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-2 text-sm text-zinc-200 hover:bg-zinc-900"
        onClick={() => signIn("google", { callbackUrl: "/coach" })}
      >
        Sign in with Google
      </button>

      <div className="rounded-2xl border border-zinc-900 bg-zinc-950 p-4">
        <div className="flex flex-col gap-2">
          <div className="text-xs text-zinc-400">Or sign in with email/password</div>
          <input
            className="w-full rounded-xl border border-zinc-800 bg-black px-3 py-2 text-sm text-zinc-100"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
          />
          <input
            className="w-full rounded-xl border border-zinc-800 bg-black px-3 py-2 text-sm text-zinc-100"
            placeholder="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
          />
          {error ? <div className="text-xs text-red-400">{error}</div> : null}
          <button
            className="rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-2 text-sm text-zinc-200 hover:bg-zinc-900"
            onClick={async () => {
              setError(null);
              const res = await signIn("credentials", {
                redirect: false,
                email,
                password,
              });
              if (res?.error) setError("Invalid credentials");
              if (res?.ok) window.location.href = "/coach";
            }}
          >
            Sign in
          </button>

          <div className="pt-1 text-xs text-zinc-400">
            New here?{" "}
            <Link className="text-zinc-200 hover:underline" href="/register">
              Create an account
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
