"use client";

import { useState } from "react";
import Link from "next/link";
import { signIn } from "next-auth/react";

function apiBaseUrlPublic(): string {
  return (process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000").replace(/\/$/, "");
}

export function RegisterClient() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  return (
    <div className="flex flex-col gap-3">
      <div>
        <h1 className="text-2xl font-semibold text-zinc-100">Create account</h1>
        <p className="pt-1 text-sm text-zinc-300">Use email/password, or Google.</p>
      </div>

      <button
        className="rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-2 text-sm text-zinc-200 hover:bg-zinc-900"
        onClick={() => signIn("google", { callbackUrl: "/coach" })}
      >
        Continue with Google
      </button>

      <div className="rounded-2xl border border-zinc-900 bg-zinc-950 p-4">
        <div className="flex flex-col gap-2">
          <div className="text-xs text-zinc-400">Or create with email/password</div>

          <input
            className="w-full rounded-xl border border-zinc-800 bg-black px-3 py-2 text-sm text-zinc-100"
            placeholder="Name (optional)"
            value={name}
            onChange={(e) => setName(e.target.value)}
            autoComplete="name"
          />
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
            autoComplete="new-password"
          />
          <input
            className="w-full rounded-xl border border-zinc-800 bg-black px-3 py-2 text-sm text-zinc-100"
            placeholder="Confirm password"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            autoComplete="new-password"
          />

          {error ? <div className="text-xs text-red-400">{error}</div> : null}

          <button
            className="rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-2 text-sm text-zinc-200 hover:bg-zinc-900 disabled:opacity-60"
            disabled={busy}
            onClick={async () => {
              setError(null);

              const trimmedEmail = email.trim().toLowerCase();
              if (!trimmedEmail) return setError("Email is required");
              if (!password) return setError("Password is required");
              if (password !== confirmPassword) return setError("Passwords do not match");

              setBusy(true);
              try {
                const resp = await fetch(`${apiBaseUrlPublic()}/auth/register`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({
                    email: trimmedEmail,
                    password,
                    name: name.trim() ? name.trim() : undefined,
                  }),
                });

                if (!resp.ok) {
                  const body = (await resp.json().catch(() => null)) as unknown;
                  const detail =
                    body && typeof body === "object" && "detail" in body
                      ? String((body as { detail?: unknown }).detail)
                      : null;
                  setError(detail || "Unable to register");
                  return;
                }

                const res = await signIn("credentials", {
                  redirect: false,
                  email: trimmedEmail,
                  password,
                });

                if (res?.error) {
                  setError("Account created, but sign-in failed");
                  return;
                }

                window.location.href = "/coach";
              } finally {
                setBusy(false);
              }
            }}
          >
            {busy ? "Creating…" : "Create account"}
          </button>

          <div className="pt-1 text-xs text-zinc-400">
            Already have an account?{" "}
            <Link className="text-zinc-200 hover:underline" href="/">
              Sign in
            </Link>
          </div>
        </div>
      </div>

      <p className="pt-2 text-xs text-zinc-500">
        Passwords are stored using PBKDF2.
      </p>
    </div>
  );
}
