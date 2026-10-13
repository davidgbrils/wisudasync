"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import {
  getJson,
  getSyncSessions,
  type ActiveBatch,
  type BatchResponse,
  type SyncSession,
} from "@/lib/api";

type Summary = {
  sitasi: ActiveBatch | null;
  certiport: ActiveBatch | null;
};

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString("id-ID", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

function sessionStatusBadge(status: string) {
  switch (status) {
    case "COMPLETED":
      return (
        <span className="inline-flex items-center gap-1 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-0.5 text-[11px] font-semibold text-emerald-800">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-600" />
          Selesai
        </span>
      );
    case "PROCESSING":
      return (
        <span className="inline-flex items-center gap-1 rounded-full border border-sky-200 bg-sky-50 px-2.5 py-0.5 text-[11px] font-semibold text-sky-800">
          <span className="h-1.5 w-1.5 rounded-full bg-sky-600 animate-pulse" />
          Memproses
        </span>
      );
    case "FAILED":
      return (
        <span className="inline-flex items-center gap-1 rounded-full border border-rose-200 bg-rose-50 px-2.5 py-0.5 text-[11px] font-semibold text-rose-800">
          <span className="h-1.5 w-1.5 rounded-full bg-rose-600" />
          Gagal
        </span>
      );
    default:
      return (
        <span className="inline-flex items-center gap-1 rounded-full border border-slate-200 bg-slate-100 px-2.5 py-0.5 text-[11px] font-semibold text-slate-700">
          {status}
        </span>
      );
  }
}

export default function DashboardPage() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [recentSessions, setRecentSessions] = useState<SyncSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [retry, setRetry] = useState(0);

  useEffect(() => {
    let current = true;
    setLoading(true);
    setError("");

    Promise.all([
      getJson<BatchResponse>("/sitasi/batch"),
      getJson<BatchResponse>("/certiport/batch"),
      getSyncSessions(1, 5).catch(() => ({ data: { items: [], total: 0 } })),
    ])
      .then(([sitasi, certiport, sessionsRes]) => {
        if (current) {
          setSummary({ sitasi: sitasi.data, certiport: certiport.data });
          setRecentSessions(sessionsRes.data?.items ?? []);
        }
      })
      .catch((reason: unknown) => {
        if (current) {
          setError(
            reason instanceof Error
              ? reason.message
              : "Data ringkasan belum dapat dimuat dari server."
          );
        }
      })
      .finally(() => {
        if (current) setLoading(false);
      });

    return () => {
      current = false;
    };
  }, [retry]);

  return (
    <div className="space-y-6 sm:space-y-8">
      {/* 1. Header Operasional & Tombol Aksi Cepat */}
      <div className="flex flex-col justify-between gap-4 border-b border-[#DDE4E1] pb-6 sm:flex-row sm:items-center">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-teal-200 bg-[#ECFAF8] px-3 py-0.5 text-xs font-semibold text-[#0F766E]">
            <span className="h-1.5 w-1.5 rounded-full bg-[#0F766E]" />
            Ruang Kerja Staf ITCC
          </div>
          <h1 className="mt-2 text-2xl font-bold tracking-tight text-[#172321] sm:text-3xl">
            Ringkasan Operasional
          </h1>
          <p className="mt-1 text-xs text-[#66736F] sm:text-sm">
            Verifikasi kelulusan sertifikasi Microsoft (MOS dan MCF) calon wisudawan berdasarkan arsip data SITASI dan Certiport.
          </p>
        </div>
        <div className="flex shrink-0 items-center gap-3">
          <Link
            href="/sinkronisasi"
            className="inline-flex min-h-11 items-center justify-center rounded-xl bg-[#0F766E] px-5 py-2.5 text-xs font-semibold text-white shadow-xs transition-colors hover:bg-[#0F4B46] focus-visible:outline focus-visible:outline-2 focus-visible:outline-teal-700 sm:text-sm"
          >
            + Validasi Berkas Wisuda
          </Link>
        </div>
      </div>

      {/* 2. Alur 4 Langkah Kerja Operasional */}
      <div className="rounded-2xl border border-[#DDE4E1] bg-white p-5 sm:p-6 shadow-xs">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-[#66736F]">
          Alur Kerja Sinkronisasi
        </h2>
        <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-xl border border-teal-100 bg-[#ECFAF8] p-3.5">
            <div className="flex items-center justify-between text-xs font-bold text-[#0F766E]">
              <span>Tahap 1</span>
              <span>Primer</span>
            </div>
            <p className="mt-1.5 text-xs font-semibold text-[#172321]">Master SITASI</p>
            <p className="mt-0.5 text-[11px] text-[#66736F]">
              Pencocokan Exact NIM calon wisudawan dan batas nilai ujian min. 700.
            </p>
          </div>

          <div className="rounded-xl border border-sky-100 bg-sky-50/60 p-3.5">
            <div className="flex items-center justify-between text-xs font-bold text-sky-800">
              <span>Tahap 2</span>
              <span>Sekunder</span>
            </div>
            <p className="mt-1.5 text-xs font-semibold text-[#172321]">Master Certiport</p>
            <p className="mt-0.5 text-[11px] text-[#66736F]">
              Verifikasi nama peserta, sub-program ujian, dan tanggal kelulusan.
            </p>
          </div>

          <div className="rounded-xl border border-[#DDE4E1] bg-[#F5F7F6]/60 p-3.5">
            <div className="flex items-center justify-between text-xs font-bold text-[#66736F]">
              <span>Tahap 3</span>
              <span>Unggah</span>
            </div>
            <p className="mt-1.5 text-xs font-semibold text-[#172321]">Pencocokan Wisuda</p>
            <p className="mt-0.5 text-[11px] text-[#66736F]">
              Pemeriksaan struktur kolom Excel dan penentuan status deterministik.
            </p>
          </div>

          <div className="rounded-xl border border-[#DDE4E1] bg-[#F5F7F6]/60 p-3.5">
            <div className="flex items-center justify-between text-xs font-bold text-[#66736F]">
              <span>Tahap 4</span>
              <span>Audit</span>
            </div>
            <p className="mt-1.5 text-xs font-semibold text-[#172321]">Review & Ekspor</p>
            <p className="mt-0.5 text-[11px] text-[#66736F]">
              Verifikasi manual baris ambigu (ADR-009) lalu unduh draf hasil.
            </p>
          </div>
        </div>
      </div>

      {/* 3. Status Master Data Sumber Aktif */}
      <section aria-labelledby="active-batches" className="space-y-4">
        <div className="flex flex-col justify-between gap-1 sm:flex-row sm:items-center">
          <div>
            <h2 id="active-batches" className="text-base font-bold text-[#172321] sm:text-lg">
              Status Master Data Aktif
            </h2>
            <p className="text-xs text-[#66736F] sm:text-sm">
              Batch acuan yang digunakan sistem saat proses pencocokan berjalan.
            </p>
          </div>
          {error && (
            <button
              type="button"
              onClick={() => setRetry((v) => v + 1)}
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#0F766E] hover:underline"
            >
              Muat Ulang Status
            </button>
          )}
        </div>

        {error && (
          <div className="rounded-xl border border-amber-200 bg-amber-50/70 p-4 text-xs text-amber-950 flex items-start gap-3">
            <span className="mt-0.5 inline-flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-amber-200 font-bold text-amber-800">
              !
            </span>
            <div>
              <p className="font-semibold">Informasi Batch Belum Terhubung Otomatis</p>
              <p className="mt-0.5 text-amber-900/80">
                Koneksi API atau basis data belum tersambung. Anda tetap dapat mengelola berkas melalui menu master data.
              </p>
            </div>
          </div>
        )}

        {loading ? (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:gap-6">
            <div className="rounded-2xl border border-[#DDE4E1] bg-white p-6 shadow-xs animate-pulse">
              <div className="h-4 w-24 bg-slate-200 rounded" />
              <div className="mt-3 h-8 w-32 bg-slate-200 rounded" />
              <div className="mt-2 h-4 w-40 bg-slate-100 rounded" />
            </div>
            <div className="rounded-2xl border border-[#DDE4E1] bg-white p-6 shadow-xs animate-pulse">
              <div className="h-4 w-24 bg-slate-200 rounded" />
              <div className="mt-3 h-8 w-32 bg-slate-200 rounded" />
              <div className="mt-2 h-4 w-40 bg-slate-100 rounded" />
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:gap-6">
            <BatchCard
              title="Master SITASI"
              subtitle="Pencocokan Primer berbasis Exact NIM"
              batch={summary?.sitasi ?? null}
              href="/sitasi"
            />
            <BatchCard
              title="Master Certiport"
              subtitle="Pencocokan Sekunder Nama & Sub-Program"
              batch={summary?.certiport ?? null}
              href="/certiport"
            />
          </div>
        )}
      </section>

      {/* 4. Sesi Sinkronisasi Terbaru */}
      <section aria-labelledby="recent-sessions" className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 id="recent-sessions" className="text-base font-bold text-[#172321] sm:text-lg">
              Sesi Sinkronisasi Terbaru
            </h2>
            <p className="text-xs text-[#66736F] sm:text-sm">
              Daftar proses pencocokan berkas wisuda terakhir yang tercatat di sistem.
            </p>
          </div>
          <Link
            href="/riwayat"
            className="text-xs font-semibold text-[#0F766E] hover:underline"
          >
            Lihat Semua Riwayat →
          </Link>
        </div>

        <div className="overflow-hidden rounded-2xl border border-[#DDE4E1] bg-white shadow-xs">
          {recentSessions.length === 0 ? (
            <div className="p-8 text-center">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[#F5F7F6] text-[#66736F]">
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <p className="mt-3 text-sm font-semibold text-[#172321]">
                Belum Ada Sesi Sinkronisasi
              </p>
              <p className="mt-1 text-xs text-[#66736F]">
                Mulai sesi pencocokan baru dengan mengunggah draf berkas wisuda (.xlsx).
              </p>
              <div className="mt-4">
                <Link
                  href="/sinkronisasi"
                  className="inline-flex min-h-10 items-center justify-center rounded-xl bg-[#0F766E] px-4 text-xs font-semibold text-white shadow-xs hover:bg-[#0F4B46]"
                >
                  Mulai Validasi Wisuda
                </Link>
              </div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-[#172321]">
                <thead className="border-b border-[#DDE4E1] bg-[#F5F7F6] font-mono text-[11px] uppercase tracking-wider text-[#66736F]">
                  <tr>
                    <th scope="col" className="px-4 py-3">Nama Berkas</th>
                    <th scope="col" className="px-4 py-3">Waktu Sesi</th>
                    <th scope="col" className="px-4 py-3 text-right">Mahasiswa</th>
                    <th scope="col" className="px-4 py-3 text-center">Hasil Valid</th>
                    <th scope="col" className="px-4 py-3 text-center">Perlu Review</th>
                    <th scope="col" className="px-4 py-3 text-center">Status</th>
                    <th scope="col" className="px-4 py-3 text-right">Aksi</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#DDE4E1]">
                  {recentSessions.map((s) => (
                    <tr key={s.id} className="transition-colors hover:bg-[#F5F7F6]/60">
                      <td className="px-4 py-3.5 font-medium text-[#172321]">
                        <span className="truncate block max-w-xs">{s.file_name}</span>
                      </td>
                      <td className="px-4 py-3.5 text-[#66736F]">
                        {formatDate(s.created_at)}
                      </td>
                      <td className="px-4 py-3.5 text-right font-mono font-medium tabular-nums">
                        {s.total_rows.toLocaleString("id-ID")}
                      </td>
                      <td className="px-4 py-3.5 text-center">
                        <span className="inline-flex rounded-full bg-emerald-50 px-2 py-0.5 text-[11px] font-semibold text-emerald-800 border border-emerald-200">
                          {s.total_valid}
                        </span>
                      </td>
                      <td className="px-4 py-3.5 text-center">
                        <span className="inline-flex rounded-full bg-amber-50 px-2 py-0.5 text-[11px] font-semibold text-amber-900 border border-amber-200">
                          {s.total_review}
                        </span>
                      </td>
                      <td className="px-4 py-3.5 text-center">
                        {sessionStatusBadge(s.status)}
                      </td>
                      <td className="px-4 py-3.5 text-right">
                        <Link
                          href={`/sinkronisasi/${s.session_id ?? s.id}`}
                          className="font-semibold text-[#0F766E] hover:underline"
                        >
                          Buka Detail →
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </section>

      {/* 5. Pedoman Operasional ITCC (Anti-Slop Enterprise Guidelines) */}
      <div className="rounded-2xl border border-[#DDE4E1] bg-[#F5F7F6]/60 p-5 sm:p-6 text-xs">
        <h3 className="font-bold text-[#172321]">
          Pedoman Verifikasi Petugas ITCC
        </h3>
        <ul className="mt-2 space-y-1.5 text-[#66736F] leading-relaxed">
          <li>
            1. <strong>Integritas Data:</strong> Pencocokan data wisuda ke SITASI menggunakan Exact NIM string. Variasi penulisan spasi atau tanda baca dinormalisasi secara otomatis.
          </li>
          <li>
            2. <strong>Prinsip Ketat:</strong> Baris kandidat yang ambigu atau memiliki beberapa catatan tidak pernah ditandai VALID secara otomatis, melainkan masuk antrean verifikasi petugas (ADR-009).
          </li>
          <li>
            3. <strong>Kunci Ekspor Final:</strong> Berkas ekspor akhir dengan format resmi hanya dapat diunduh setelah pemetaan kolom disetujui pimpinan ITCC (ADR-003).
          </li>
        </ul>
      </div>
    </div>
  );
}

function BatchCard({
  title,
  subtitle,
  batch,
  href,
}: {
  title: string;
  subtitle: string;
  batch: ActiveBatch | null;
  href: string;
}) {
  return (
    <article className="flex flex-col justify-between rounded-2xl border border-[#DDE4E1] bg-white p-5 sm:p-6 shadow-xs transition-all hover:border-slate-300">
      <div>
        <div className="flex items-start justify-between gap-3">
          <div>
            <span className="text-[11px] font-semibold uppercase tracking-wider text-[#66736F]">
              {title}
            </span>
            <p className="mt-1 text-xs text-[#66736F]">{subtitle}</p>
          </div>
          <span
            className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-[11px] font-semibold ${
              batch
                ? "border-emerald-200 bg-emerald-50 text-emerald-800"
                : "border-[#DDE4E1] bg-[#F5F7F6] text-[#66736F]"
            }`}
          >
            {batch ? "Batch Aktif" : "Belum Ada Batch"}
          </span>
        </div>

        <div className="mt-4 rounded-xl bg-[#F5F7F6]/60 p-4 border border-[#DDE4E1]/60">
          <p className="text-xs text-[#66736F]">Total Baris Tersimpan</p>
          <p className="mt-1 text-2xl sm:text-3xl font-bold tabular-nums text-[#172321]">
            {batch ? batch.imported_rows.toLocaleString("id-ID") : "0"}
          </p>
          <p className="mt-0.5 text-xs text-[#66736F]">
            {batch ? "Baris siap dicocokkan" : "Belum ada file workbook diimpor"}
          </p>
        </div>

        {batch && (
          <div className="mt-3 flex items-center justify-between font-mono text-[11px] text-[#66736F] truncate border-t border-[#F0F4F3] pt-2.5">
            <span>
              ID: <code className="text-[#0F766E]">{batch.id.slice(0, 12)}…</code>
            </span>
            <span>Status: {batch.status}</span>
          </div>
        )}
      </div>

      <div className="mt-5 pt-2">
        <Link
          href={href}
          className="inline-flex min-h-11 w-full items-center justify-center rounded-xl border border-[#DDE4E1] bg-white px-4 text-xs font-semibold text-[#172321] shadow-xs transition-colors hover:bg-[#F5F7F6] hover:border-slate-300 focus-visible:outline focus-visible:outline-2 focus-visible:outline-teal-700"
        >
          {batch ? "Kelola & Periksa Data Master" : "Unggah & Impor Master Baru"} →
        </Link>
      </div>
    </article>
  );
}
