import type { ReactNode } from "react";
import { redirect } from "next/navigation";

import LogoutButton from "@/components/logout-button";
import SidebarNav from "@/components/sidebar-nav";
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
  return (
    <div className="min-h-screen bg-slate-50">
      <a href="#main-content" className="sr-only z-50 rounded bg-white p-3 text-slate-900 focus:not-sr-only focus:fixed focus:left-4 focus:top-4">Lewati navigasi</a>
      <header className="sticky top-0 z-20 flex min-h-16 items-center justify-between border-b border-slate-200 bg-white px-4 sm:px-6">
        <div className="flex min-w-0 items-center gap-3">
          <span aria-hidden="true" className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-teal-800 text-sm font-bold text-white">W</span>
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-slate-900">ITCC Wisuda Sync</p>
            <p className="hidden text-xs text-slate-500 sm:block">Pusat data sertifikasi</p>
          </div>
        </div>
        <LogoutButton />
      </header>
      <div className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-[1600px]">
        <aside className="hidden w-60 shrink-0 border-r border-slate-200 bg-white p-4 md:block" aria-label="Sidebar">
          <SidebarNav orientation="vertical" />
          <p className="mt-8 border-t border-slate-200 pt-4 text-xs leading-5 text-slate-500">Akses internal petugas ITCC. Data ditampilkan dari batch aktif.</p>
        </aside>
        <div className="min-w-0 flex-1">
          <div className="border-b border-slate-200 bg-white px-3 py-2 md:hidden">
            <SidebarNav orientation="horizontal" />
          </div>
          <main id="main-content" className="mx-auto w-full max-w-[1400px] p-4 sm:p-6 lg:p-8">{children}</main>
        </div>
      </div>
    </div>
  );
}
