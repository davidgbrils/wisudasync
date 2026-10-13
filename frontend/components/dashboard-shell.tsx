"use client";

import { useState, useEffect, type ReactNode } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import SidebarNav from "@/components/sidebar-nav";
import LogoutButton from "@/components/logout-button";

export default function DashboardShell({ children }: { children: ReactNode }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const pathname = usePathname();

  // Otomatis tutup drawer mobile saat rute berubah
  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  // Handle keyboard ESC untuk menutup drawer mobile
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") {
        setMobileOpen(false);
      }
    }
    if (mobileOpen) {
      window.addEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "";
    };
  }, [mobileOpen]);

  // Judul halaman dinamis untuk breadcrumb topbar
  const getPageTitle = (path: string) => {
    if (path.startsWith("/dashboard")) return "Ringkasan Data Master";
    if (path.startsWith("/sinkronisasi/")) return "Detail Hasil Sinkronisasi";
    if (path.startsWith("/sinkronisasi")) return "Validasi & Unggah Wisuda";
    if (path.startsWith("/riwayat")) return "Riwayat Sinkronisasi";
    if (path.startsWith("/sitasi")) return "Master Data SITASI";
    if (path.startsWith("/certiport")) return "Master Data Certiport";
    return "Ruang Kerja Petugas";
  };

  return (
    <div className="min-h-screen bg-[#F5F7F6] text-[#172321]">
      <a
        href="#main-content"
        className="sr-only z-50 rounded-lg bg-white p-3 font-semibold text-[#0F766E] shadow-lg ring-2 ring-[#0F766E] focus:not-sr-only focus:fixed focus:left-4 focus:top-4"
      >
        Lewati ke Konten Utama
      </a>

      {/* ============================================================ */}
      {/* 1. SIDEBAR DESKTOP (Layar Besar >= lg)                      */}
      {/* ============================================================ */}
      <aside
        className="fixed inset-y-0 left-0 z-30 hidden w-64 flex-col border-r border-[#DDE4E1] bg-white lg:flex xl:w-72"
        aria-label="Navigasi Utama Petugas"
      >
        {/* Brand Header */}
        <div className="flex h-16 shrink-0 items-center justify-between border-b border-[#DDE4E1] px-5 xl:px-6">
          <Link href="/dashboard" className="flex items-center gap-2.5 group">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/brand/logo-full.png"
              alt="ITCC Wisuda Sync"
              width={120}
              height={36}
              className="h-8 w-auto object-contain transition-transform group-hover:scale-102"
            />
          </Link>
          <span className="rounded-full border border-teal-200 bg-[#ECFAF8] px-2 py-0.5 text-[10px] font-semibold text-[#0F766E]">
            v1.0
          </span>
        </div>

        {/* Navigation Links */}
        <div className="flex-1 overflow-y-auto px-3.5 py-4 xl:px-4">
          <p className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-wider text-[#66736F]">
            Menu Operasional
          </p>
          <SidebarNav orientation="vertical" />

          <div className="mt-6 rounded-xl border border-[#DDE4E1] bg-[#F5F7F6]/80 p-3.5 text-xs">
            <p className="font-semibold text-[#172321]">Akses Petugas ITCC</p>
            <p className="mt-1 text-[11px] leading-relaxed text-[#66736F]">
              Pencocokan data wisuda dengan snapshot batch master SITASI & Certiport aktif.
            </p>
          </div>
        </div>

        {/* Footer Sidebar (Profil & Logout) */}
        <div className="shrink-0 border-t border-[#DDE4E1] bg-[#F5F7F6]/40 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#ECFAF8] font-bold text-[#0F766E] border border-teal-200 text-xs shadow-xs">
                IT
              </div>
              <div className="min-w-0">
                <p className="truncate text-xs font-semibold text-[#172321]">Petugas ITCC</p>
                <p className="truncate text-[10px] text-[#66736F]">Staff Verifikator</p>
              </div>
            </div>
            <LogoutButton variant="compact" />
          </div>
        </div>
      </aside>

      {/* ============================================================ */}
      {/* 2. MOBILE TOPBAR & DRAWER (Layar Ponsel / Tablet < lg)        */}
      {/* ============================================================ */}
      <header className="fixed inset-x-0 top-0 z-20 flex h-16 items-center justify-between border-b border-[#DDE4E1] bg-white px-4 shadow-xs lg:hidden">
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setMobileOpen(true)}
            aria-label="Buka navigasi menu"
            aria-expanded={mobileOpen}
            className="flex h-11 w-11 items-center justify-center rounded-lg border border-[#DDE4E1] text-[#172321] hover:bg-[#F5F7F6] focus:outline-none focus:ring-2 focus:ring-[#0F766E]"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <Link href="/dashboard" className="flex items-center">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/brand/logo-full.png"
              alt="ITCC Wisuda Sync"
              width={110}
              height={32}
              className="h-7 w-auto object-contain"
            />
          </Link>
        </div>

        <div className="flex items-center gap-2">
          <LogoutButton variant="compact" />
        </div>
      </header>

      {/* Backdrop Mobile Drawer */}
      {mobileOpen && (
        <div
          role="presentation"
          onClick={() => setMobileOpen(false)}
          className="fixed inset-0 z-40 bg-slate-900/60 backdrop-blur-xs transition-opacity lg:hidden"
        />
      )}

      {/* Panel Slide-over Mobile Drawer */}
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Menu Navigasi Mobile"
        className={`fixed inset-y-0 left-0 z-50 flex w-72 max-w-[85vw] flex-col border-r border-[#DDE4E1] bg-white shadow-2xl transition-transform duration-300 ease-in-out lg:hidden ${
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex h-16 shrink-0 items-center justify-between border-b border-[#DDE4E1] px-4">
          <Link href="/dashboard" className="flex items-center" onClick={() => setMobileOpen(false)}>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/brand/logo-full.png"
              alt="ITCC Wisuda Sync"
              width={110}
              height={32}
              className="h-7 w-auto object-contain"
            />
          </Link>
          <button
            type="button"
            onClick={() => setMobileOpen(false)}
            aria-label="Tutup menu navigasi"
            className="flex h-10 w-10 items-center justify-center rounded-lg text-[#66736F] hover:bg-[#F5F7F6] hover:text-[#172321]"
          >
            ✕
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-3.5 py-4">
          <p className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-wider text-[#66736F]">
            Navigasi Halaman
          </p>
          <SidebarNav orientation="vertical" onNavigate={() => setMobileOpen(false)} />
        </div>

        <div className="shrink-0 border-t border-[#DDE4E1] bg-[#F5F7F6]/60 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-[#172321]">Petugas ITCC</p>
              <p className="text-[10px] text-[#66736F]">Staff Verifikator</p>
            </div>
            <LogoutButton variant="compact" />
          </div>
        </div>
      </div>

      {/* ============================================================ */}
      {/* 3. DESKTOP TOP HEADER (Breadcrumbs & Sistem Info)             */}
      {/* ============================================================ */}
      <div className="flex min-h-screen flex-col lg:pl-64 xl:pl-72">
        <header className="sticky top-0 z-20 hidden h-16 shrink-0 items-center justify-between border-b border-[#DDE4E1] bg-white/95 px-6 backdrop-blur-xs lg:flex xl:px-8">
          <div className="flex items-center gap-2 text-xs text-[#66736F]">
            <span className="font-semibold text-[#0F766E]">Portal ITCC</span>
            <span>/</span>
            <span className="font-medium text-[#172321]">{getPageTitle(pathname)}</span>
          </div>

          <div className="flex items-center gap-4">
            <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-800">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-600 animate-pulse" />
              Sistem Operasional
            </span>
            <div className="h-4 w-px bg-[#DDE4E1]" />
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-[#172321]">Ruang Kerja Petugas</span>
            </div>
          </div>
        </header>

        {/* ============================================================ */}
        {/* 4. MAIN CONTENT CONTAINER (FLUID & RESPONSIF)                 */}
        {/* ============================================================ */}
        <main
          id="main-content"
          className="flex-1 w-full max-w-7xl mx-auto px-4 py-6 sm:px-6 sm:py-8 lg:px-8 lg:py-10 pt-20 lg:pt-8"
        >
          {children}
        </main>
      </div>
    </div>
  );
}
