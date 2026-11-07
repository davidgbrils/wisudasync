"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { createSupabaseBrowserClient } from "@/lib/supabase/client";
import { getJson } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  async function signIn(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    let supabase: ReturnType<typeof createSupabaseBrowserClient> | null = null;
    try {
      supabase = createSupabaseBrowserClient();
      const { error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) throw new Error("Email atau kata sandi tidak cocok.");
      await getJson("/auth/me");
      router.replace("/sinkronisasi");
      router.refresh();
    } catch (error) {
      if (supabase) await supabase.auth.signOut();
      setMessage(error instanceof Error ? error.message : "Login belum berhasil.");
      setBusy(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#F5F7F6] px-4 text-[#172321]">
      <div className="w-full max-w-sm rounded-2xl border border-[#DDE4E1] bg-white p-8 shadow-sm">
        <h1 className="text-2xl font-bold">Masuk ke Wisuda Sync</h1>
        <p className="mt-2 text-sm text-[#66736F]">Gunakan akun petugas ITCC yang sudah terdaftar.</p>
        <form onSubmit={signIn} className="mt-7 space-y-4">
          <label className="block text-sm font-medium" htmlFor="email">Email</label>
          <input id="email" type="email" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)} className="w-full rounded-lg border border-[#BFCBC6] px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-[#0F766E]" />
          <label className="block text-sm font-medium" htmlFor="password">Kata sandi</label>
          <input id="password" type="password" autoComplete="current-password" required value={password} onChange={(e) => setPassword(e.target.value)} className="w-full rounded-lg border border-[#BFCBC6] px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-[#0F766E]" />
          {message && <p role="alert" className="text-sm text-red-700">{message}</p>}
          <button type="submit" disabled={busy} className="w-full rounded-lg bg-[#0F766E] px-4 py-2.5 font-semibold text-white hover:bg-[#0B5E58] focus:outline-none focus:ring-2 focus:ring-[#0F766E] focus:ring-offset-2 disabled:opacity-60">
            {busy ? "Memeriksa akun…" : "Masuk"}
          </button>
        </form>
      </div>
    </main>
  );
}
