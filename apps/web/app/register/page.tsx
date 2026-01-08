import { redirect } from "next/navigation";
import { getServerSession } from "next-auth/next";

import { authOptions } from "../auth";
import { RegisterClient } from "./RegisterClient";

export default async function RegisterPage() {
  const session = await getServerSession(authOptions);
  if (session) redirect("/coach");

  return (
    <main className="relative flex min-h-screen w-full items-center justify-center bg-black p-4">
      <section className="w-full max-w-xl rounded-3xl border border-zinc-900 bg-zinc-950 p-8">
        <RegisterClient />
      </section>
    </main>
  );
}
