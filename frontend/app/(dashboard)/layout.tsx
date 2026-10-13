import type { ReactNode } from "react";
import { redirect } from "next/navigation";

import DashboardShell from "@/components/dashboard-shell";
import { createSupabaseServerClient } from "@/lib/supabase/server";

export const dynamic = "force-dynamic";

async function verifyStaffRoute() {
  const supabase = await createSupabaseServerClient();
  const { data: { session } } = await supabase.auth.getSession();
  if (!session?.access_token) redirect("/login");

  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";
  let response: Response;
  try {
    response = await fetch(`${apiUrl}/auth/me`, {
      headers: { Authorization: `Bearer ${session.access_token}` },
      cache: "no-store",
    });
  } catch {
    throw new Error("Layanan API belum dapat dijangkau.");
  }
  if (response.status === 401) redirect("/login");
  if (response.status === 403) redirect("/unauthorized");
  if (!response.ok) throw new Error("Pemeriksaan akses belum dapat dilakukan.");
}

export default async function DashboardLayout({ children }: Readonly<{ children: ReactNode }>) {
  await verifyStaffRoute();
  return <DashboardShell>{children}</DashboardShell>;
}
