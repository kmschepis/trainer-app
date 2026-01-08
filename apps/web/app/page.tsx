import { redirect } from "next/navigation";
import { getServerSession } from "next-auth/next";

import { authOptions } from "./auth";
import { AuthButtons } from "./components/AuthButtons";

export default async function LandingPage() {
  const session = await getServerSession(authOptions);
  if (session) redirect("/coach");

  return (
    <main className="relative flex min-h-screen w-full items-center justify-center bg-black p-4">
      <section className="w-full max-w-xl rounded-3xl border border-zinc-900 bg-zinc-950 p-8">
        <div className="flex flex-col gap-3">
          <h1 className="text-2xl font-semibold text-zinc-100">Trainer2</h1>
          <p className="text-sm text-zinc-300">Log workouts, chat with your coach, and keep your state private.</p>
          <ul className="list-disc space-y-1 pl-5 text-sm text-zinc-400">
            <li>Private profile + session state</li>
            <li>Realtime coach chat</li>
            <li>Simple, fast UI</li>
          </ul>
          <div className="pt-2">
            <AuthButtons />
          </div>
          <p className="pt-4 text-xs text-zinc-500">
            By continuing you agree to keep credentials secure.
          </p>
        </div>
      </section>
    </main>
  );
}
