"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { createSupabaseBrowserClient } from "@/lib/supabase/client";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const { error: signInError } = await createSupabaseBrowserClient().auth.signInWithPassword({
        email: email.trim(),
        password,
      });
      if (signInError) {
        setError("Email atau kata sandi salah, atau akun belum diaktifkan.");
        return;
      }
      router.replace("/sitasi");
      router.refresh();
    } catch {
      setError("Login belum dapat diproses. Periksa konfigurasi atau koneksi.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-md items-center px-6">
      <section className="w-full rounded-xl border border-gray-200 bg-white p-8 shadow-sm">
        <p className="text-sm font-medium text-gray-500">ITCC · ITPLN</p>
        <h1 className="mt-2 text-2xl font-semibold">Masuk Wisuda Sync</h1>
        <p className="mt-2 text-sm text-gray-600">Akses hanya untuk petugas ITCC yang terdaftar.</p>
        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div>
            <label htmlFor="email" className="mb-1 block text-sm font-medium">Email</label>
            <input id="email" type="email" autoComplete="username" required value={email} onChange={(event) => setEmail(event.target.value)} className="w-full rounded-md border px-3 py-2" />
          </div>
          <div>
            <label htmlFor="password" className="mb-1 block text-sm font-medium">Kata sandi</label>
            <input id="password" type="password" autoComplete="current-password" required value={password} onChange={(event) => setPassword(event.target.value)} className="w-full rounded-md border px-3 py-2" />
          </div>
          {error && <p role="alert" className="text-sm text-red-700">{error}</p>}
          <button type="submit" disabled={loading} className="w-full rounded-md bg-gray-900 px-4 py-2 font-medium text-white disabled:opacity-60">
            {loading ? "Memeriksa…" : "Masuk"}
          </button>
        </form>
      </section>
    </main>
  );
}
