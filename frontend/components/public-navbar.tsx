"use client";

import Link from "next/link";
import { useState } from "react";

const navLinks = [
  { href: "#fitur", label: "Fitur" },
  { href: "#cara-kerja", label: "Cara Kerja" },
  { href: "#status", label: "Status Data" },
];

export default function PublicNavbar() {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/90 backdrop-blur">
      <div className="mx-auto flex min-h-16 max-w-6xl items-center justify-between gap-4 px-4 sm:px-6">
        <Link
          href="/"
          className="flex min-w-0 items-center gap-3 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-teal-700"
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/brand/logo-full.png"
            alt="ITCC Wisuda Sync - Pusat Data Sertifikasi"
            width={128}
            height={40}
            className="h-10 w-auto"
          />
        </Link>

        <nav aria-label="Navigasi halaman" className="hidden items-center gap-1 md:flex">
          {navLinks.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="inline-flex min-h-11 items-center rounded-md px-3 text-sm font-medium text-slate-600 transition hover:bg-slate-100 hover:text-slate-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700"
            >
              {link.label}
            </a>
          ))}
        </nav>

        <div className="hidden items-center gap-2 md:flex">
          <Link
            href="/login"
            className="inline-flex min-h-11 items-center rounded-md px-4 text-sm font-medium text-slate-700 transition hover:bg-slate-100 hover:text-slate-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700"
          >
            Masuk
          </Link>
          <Link
            href="/login?mode=register"
            className="inline-flex min-h-11 items-center rounded-md bg-teal-800 px-4 text-sm font-medium text-white transition hover:bg-teal-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700"
          >
            Daftar
          </Link>
        </div>

        <button
          type="button"
          onClick={() => setOpen((value) => !value)}
          aria-expanded={open}
          aria-controls="navbar-mobile"
          aria-label={open ? "Tutup menu navigasi" : "Buka menu navigasi"}
          className="inline-flex min-h-11 min-w-11 items-center justify-center rounded-md border border-slate-300 p-2 text-slate-700 transition hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700 md:hidden"
        >
          <span aria-hidden="true" className="space-y-1">
            <span className="block h-0.5 w-5 bg-current" />
            <span className="block h-0.5 w-5 bg-current" />
            <span className="block h-0.5 w-5 bg-current" />
          </span>
        </button>
      </div>

      {open && (
        <div id="navbar-mobile" className="border-t border-slate-200 bg-white px-4 py-4 md:hidden">
          <nav aria-label="Navigasi halaman" className="space-y-1">
            {navLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                onClick={() => setOpen(false)}
                className="flex min-h-11 items-center rounded-md px-3 text-sm font-medium text-slate-700 transition hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700"
              >
                {link.label}
              </a>
            ))}
          </nav>
          <div className="mt-3 grid gap-2 border-t border-slate-200 pt-3">
            <Link
              href="/login"
              onClick={() => setOpen(false)}
              className="inline-flex min-h-11 items-center justify-center rounded-md border border-slate-300 px-4 text-sm font-medium text-slate-700 transition hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700"
            >
              Masuk
            </Link>
            <Link
              href="/login?mode=register"
              onClick={() => setOpen(false)}
              className="inline-flex min-h-11 items-center justify-center rounded-md bg-teal-800 px-4 text-sm font-medium text-white transition hover:bg-teal-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700"
            >
              Daftar
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
