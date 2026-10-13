"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { createSupabaseBrowserClient } from "@/lib/supabase/client";

export default function LogoutButton({ variant = "normal" }: { variant?: "normal" | "compact" }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);

  async function logout() {
    setBusy(true);
    const { error } = await createSupabaseBrowserClient().auth.signOut();
    if (!error) {
      router.replace("/login");
      router.refresh();
    } else {
      setBusy(false);
    }
  }

  if (variant === "compact") {
    return (
      <button
        type="button"
        onClick={logout}
        disabled={busy}
        title="Keluar dari akun petugas"
        aria-label="Keluar dari akun"
        className="inline-flex min-h-11 min-w-11 items-center justify-center rounded-lg border border-[#DDE4E1] bg-white px-2.5 py-1.5 text-xs font-semibold text-[#66736F] shadow-xs hover:border-rose-300 hover:bg-rose-50 hover:text-rose-700 transition-colors disabled:opacity-50"
      >
        <svg className="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
        </svg>
        <span className="sr-only sm:not-sr-only sm:ml-1.5">{busy ? "…" : "Keluar"}</span>
      </button>
    );
  }

  return (
    <button
      type="button"
      onClick={logout}
      disabled={busy}
      className="inline-flex min-h-10 items-center justify-center gap-1.5 rounded-lg border border-[#DDE4E1] bg-white px-3 py-1.5 text-xs font-semibold text-[#172321] shadow-xs hover:border-rose-300 hover:bg-rose-50 hover:text-rose-700 transition-colors disabled:opacity-50"
    >
      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
      </svg>
      <span>{busy ? "Memproses…" : "Keluar"}</span>
    </button>
  );
}
