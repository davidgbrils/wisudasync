"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { registerStaff } from "@/lib/api";
import { createSupabaseBrowserClient } from "@/lib/supabase/client";

export default function LoginForm({ initialMode = "login" }: { initialMode?: "login" | "register" }) {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">(initialMode);

  // Form states
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  // Feedback states
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  function switchMode(newMode: "login" | "register") {
    setMode(newMode);
    setError("");
    setSuccess("");
  }

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const { error: signInError } = await createSupabaseBrowserClient().auth.signInWithPassword({
        email: email.trim(),
        password,
      });

      if (signInError) {
        setError("Email atau kata sandi salah, atau akun belum terdaftar.");
        return;
      }

      router.replace("/dashboard");
      router.refresh();
    } catch {
      setError("Login belum dapat diproses. Periksa konfigurasi atau koneksi.");
    } finally {
      setLoading(false);
    }
  }

  async function handleRegister(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSuccess("");

    if (password.length < 6) {
      setError("Kata sandi minimal 6 karakter.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Konfirmasi kata sandi tidak cocok.");
      return;
    }

    if (displayName.trim().length < 2) {
      setError("Nama lengkap minimal 2 karakter.");
      return;
    }

    setLoading(true);

    try {
      // 1. Daftarkan akun ke backend (membuat auth.users & mencatat di public.profiles)
      await registerStaff({
        email: email.trim(),
        password,
        display_name: displayName.trim(),
      });

      setSuccess("Akun petugas berhasil dibuat dan tercatat di database! Mengalihkan...");

      // 2. Otomatis login ke sesi browser Supabase
      const { error: signInError } = await createSupabaseBrowserClient().auth.signInWithPassword({
        email: email.trim(),
        password,
      });

      if (signInError) {
        setSuccess("Akun berhasil terdaftar di database! Silakan masuk dengan email dan kata sandi Anda.");
        setMode("login");
        return;
      }

      router.replace("/dashboard");
      router.refresh();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Pendaftaran gagal. Periksa koneksi.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-md flex-col items-center justify-center px-6 py-12">
      <div className="mb-4 w-full">
        <Link
          href="/"
          className="inline-flex items-center gap-1.5 text-sm font-medium text-[#66736F] transition hover:text-[#0F4B46] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0F766E]"
        >
          <span aria-hidden="true">←</span> Kembali ke beranda
        </Link>
      </div>
      <section className="w-full rounded-xl border border-[#DDE4E1] bg-white p-8 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/brand/app-icon.png" alt="" width={28} height={28} className="h-7 w-7 rounded" />
            <p className="text-xs font-semibold uppercase tracking-wider text-[#66736F]">ITCC · ITPLN</p>
          </div>
          <span className="rounded-full border border-[#A7F3D0] bg-[#ECFAF8] px-2.5 py-0.5 text-xs font-semibold text-[#0F4B46]">
            Wisuda Sync
          </span>
        </div>

        <h1 className="mt-4 text-2xl font-semibold tracking-tight text-[#172321]">
          {mode === "login" ? "Masuk ke Sistem" : "Pendaftaran Petugas"}
        </h1>
        <p className="mt-1 text-sm text-[#66736F]">
          {mode === "login"
            ? "Masukkan akun petugas ITCC Anda untuk mengakses sistem."
            : "Buat akun petugas baru untuk dicatat di database."}
        </p>

        {/* Tab switch */}
        <div className="mt-5 flex rounded-lg border border-[#DDE4E1] bg-[#F5F7F6] p-1 text-sm font-medium text-[#66736F]">
          <button
            type="button"
            onClick={() => switchMode("login")}
            className={`flex-1 rounded-md py-1.5 transition ${
              mode === "login"
                ? "bg-white font-semibold text-[#172321] shadow-sm"
                : "hover:text-[#172321]"
            }`}
          >
            Masuk
          </button>
          <button
            type="button"
            onClick={() => switchMode("register")}
            className={`flex-1 rounded-md py-1.5 transition ${
              mode === "register"
                ? "bg-white font-semibold text-[#172321] shadow-sm"
                : "hover:text-[#172321]"
            }`}
          >
            Daftar Akun
          </button>
        </div>

        {error && (
          <div role="alert" className="mt-4 rounded-lg border border-[#FECDD3] bg-[#FFF1F2] p-3 text-sm text-[#9F1239]">
            {error}
          </div>
        )}

        {success && (
          <div role="status" className="mt-4 rounded-lg border border-[#A7F3D0] bg-[#ECFDF5] p-3 text-sm text-[#065F46]">
            {success}
          </div>
        )}

        {mode === "login" ? (
          <form onSubmit={handleLogin} className="mt-5 space-y-4">
            <div>
              <label htmlFor="login-email" className="mb-1 block text-sm font-medium text-[#172321]">
                Email Petugas
              </label>
              <input
                id="login-email"
                type="email"
                autoComplete="username"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="petugas@itpln.ac.id"
                className="w-full rounded-lg border border-[#DDE4E1] bg-white px-3.5 py-2.5 text-sm text-[#172321] placeholder:text-[#66736F] focus:border-[#0F766E] focus:outline-none focus:ring-1 focus:ring-[#0F766E]"
              />
            </div>
            <div>
              <label htmlFor="login-password" className="mb-1 block text-sm font-medium text-[#172321]">
                Kata Sandi
              </label>
              <input
                id="login-password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full rounded-lg border border-[#DDE4E1] bg-white px-3.5 py-2.5 text-sm text-[#172321] placeholder:text-[#66736F] focus:border-[#0F766E] focus:outline-none focus:ring-1 focus:ring-[#0F766E]"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-[#0F766E] px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-[#0C5F58] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0F766E] disabled:opacity-60"
            >
              {loading ? "Memeriksa…" : "Masuk"}
            </button>
            <p className="pt-2 text-center text-xs text-[#66736F]">
              Belum terdaftar?{" "}
              <button
                type="button"
                onClick={() => switchMode("register")}
                className="font-semibold text-[#0F766E] hover:underline"
              >
                Daftar akun petugas di sini
              </button>
            </p>
          </form>
        ) : (
          <form onSubmit={handleRegister} className="mt-5 space-y-4">
            <div>
              <label htmlFor="reg-name" className="mb-1 block text-sm font-medium text-[#172321]">
                Nama Lengkap Petugas
              </label>
              <input
                id="reg-name"
                type="text"
                autoComplete="name"
                required
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                placeholder="Nama Anda"
                className="w-full rounded-lg border border-[#DDE4E1] bg-white px-3.5 py-2.5 text-sm text-[#172321] placeholder:text-[#66736F] focus:border-[#0F766E] focus:outline-none focus:ring-1 focus:ring-[#0F766E]"
              />
            </div>
            <div>
              <label htmlFor="reg-email" className="mb-1 block text-sm font-medium text-[#172321]">
                Email Petugas
              </label>
              <input
                id="reg-email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="petugas@itpln.ac.id"
                className="w-full rounded-lg border border-[#DDE4E1] bg-white px-3.5 py-2.5 text-sm text-[#172321] placeholder:text-[#66736F] focus:border-[#0F766E] focus:outline-none focus:ring-1 focus:ring-[#0F766E]"
              />
            </div>
            <div>
              <label htmlFor="reg-password" className="mb-1 block text-sm font-medium text-[#172321]">
                Kata Sandi (min. 6 karakter)
              </label>
              <input
                id="reg-password"
                type="password"
                autoComplete="new-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full rounded-lg border border-[#DDE4E1] bg-white px-3.5 py-2.5 text-sm text-[#172321] placeholder:text-[#66736F] focus:border-[#0F766E] focus:outline-none focus:ring-1 focus:ring-[#0F766E]"
              />
            </div>
            <div>
              <label htmlFor="reg-confirm" className="mb-1 block text-sm font-medium text-[#172321]">
                Konfirmasi Kata Sandi
              </label>
              <input
                id="reg-confirm"
                type="password"
                autoComplete="new-password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full rounded-lg border border-[#DDE4E1] bg-white px-3.5 py-2.5 text-sm text-[#172321] placeholder:text-[#66736F] focus:border-[#0F766E] focus:outline-none focus:ring-1 focus:ring-[#0F766E]"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-[#0F766E] px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-[#0C5F58] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#0F766E] disabled:opacity-60"
            >
              {loading ? "Mendaftarkan…" : "Daftar & Catat di Database"}
            </button>
            <p className="pt-2 text-center text-xs text-[#66736F]">
              Sudah punya akun?{" "}
              <button
                type="button"
                onClick={() => switchMode("login")}
                className="font-semibold text-[#0F766E] hover:underline"
              >
                Masuk di sini
              </button>
            </p>
          </form>
        )}
      </section>
    </main>
  );
}
