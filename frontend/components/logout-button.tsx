"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { createSupabaseBrowserClient } from "@/lib/supabase/client";

export default function LogoutButton() {
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

  return <button type="button" onClick={logout} disabled={busy} className="text-sm underline disabled:opacity-60">{busy ? "Keluar…" : "Keluar"}</button>;
}
