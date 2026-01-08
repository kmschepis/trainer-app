import { redirect } from "next/navigation";
import { getServerSession } from "next-auth/next";

import { authOptions } from "../auth";
import { CoachAuditClient } from "./CoachAuditClient";

export default async function CoachAuditPage() {
  const session = await getServerSession(authOptions);
  if (!session) redirect("/");

  return <CoachAuditClient />;
}
