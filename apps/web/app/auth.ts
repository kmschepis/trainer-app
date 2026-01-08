import type { NextAuthOptions } from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import CredentialsProvider from "next-auth/providers/credentials";

type LoginResponse = {
  userId: string;
  email?: string | null;
  name?: string | null;
  accessToken: string;
};

function apiBaseUrlInternal(): string {
  return (
    process.env.API_BASE_URL_INTERNAL ??
    process.env.NEXT_PUBLIC_API_BASE_URL ??
    "http://api:8000"
  ).replace(/\/$/, "");
}

export const authOptions: NextAuthOptions = {
  session: { strategy: "jwt" },
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID ?? "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET ?? "",
    }),

    CredentialsProvider({
      name: "Email & Password",
      credentials: {
        email: { label: "Email", type: "text" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        const email = credentials?.email?.toString().trim() ?? "";
        const password = credentials?.password?.toString() ?? "";
        if (!email || !password) return null;

        const resp = await fetch(`${apiBaseUrlInternal()}/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });

        if (!resp.ok) return null;
        const data = (await resp.json()) as unknown;
        if (!data || typeof data !== "object") return null;
        const d = data as LoginResponse;
        if (typeof d.userId !== "string" || typeof d.accessToken !== "string") return null;

        return {
          id: d.userId,
          email: d.email ?? email,
          name: d.name ?? null,
          accessToken: d.accessToken,
        } as unknown as { id: string; email?: string | null; name?: string | null; accessToken: string };
      },
    }),
  ],
  callbacks: {
    async jwt({ token, account, user }) {
      if (account?.provider === "google") {
        // Google ID token used to authenticate API/WS.
        const idToken = (account as unknown as { id_token?: unknown } | null)?.id_token;
        if (typeof idToken === "string" && idToken.trim()) {
          (token as unknown as { idToken?: string }).idToken = idToken;
        }
      }

      const accessToken = (user as unknown as { accessToken?: unknown } | null)?.accessToken;
      if (typeof accessToken === "string" && accessToken.trim()) {
        (token as unknown as { idToken?: string }).idToken = accessToken;
      }

      return token;
    },
    async session({ session, token }) {
      const idToken = (token as unknown as { idToken?: unknown } | null)?.idToken;
      if (typeof idToken === "string") {
        (session as unknown as { idToken?: string }).idToken = idToken;
      }
      return session;
    },
  },
};
