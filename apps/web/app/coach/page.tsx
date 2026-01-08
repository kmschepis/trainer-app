import { redirect } from "next/navigation";
import { getServerSession } from "next-auth/next";

import { authOptions } from "../auth";
import { CoachClient } from "./CoachClient";

export default async function CoachPage() {
  const session = await getServerSession(authOptions);
  if (!session) redirect("/");

  return <CoachClient />;
}
