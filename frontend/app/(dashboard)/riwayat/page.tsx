"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { getSyncSessions, type SyncSession } from "@/lib/api";

export default function SyncHistoryPage() {
  const [sessions, setSessions] = useState<SyncSession[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(20);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadHistory() {
      setLoading(true);
      setError("");
      try {
        const res = await getSyncSessions(page, limit);
        setSessions(res.data.items);
        setTotal(res.data.total);
      } catch (cause) {
        setError(cause instanceof Error ? cause.message : "Gagal memuat riwayat sinkronisasi.");
      } finally {
        setLoading(false);
      }
    }
    loadHistory();
  }, [page, limit]);

  const totalPages = Math.ceil(total / limit) || 1;

  return (
    <section className="mx-auto w-full max-w-7xl space-y-6 sm:space-y-8">
      <header className="space-y-1.5">
        <div className="inline-flex items-center gap-1.5 rounded-full border border-teal-200 bg-teal-50 px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wider text-teal-800">
          Jejak Audit & Riwayat
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-[#172321] sm:text-3xl lg:text-4xl">Riwayat Sinkronisasi</h1>
        <p className="max-w-3xl text-xs sm:text-sm leading-relaxed text-[#66736F]">
          Log historis proses pencocokan data wisuda yang pernah dijalankan beserta versi snapshot batch master SITASI dan Certiport.
        </p>
      </header>

      {error && (
        <div role="alert" className="rounded-2xl border border-red-200 bg-red-50 p-4 text-xs font-medium text-red-900 shadow-xs">
          {error}
        </div>
      )}

      <div className="overflow-hidden rounded-2xl border border-[#DDE4E1] bg-white shadow-xs">
        <div className="flex items-center justify-between border-b border-[#DDE4E1] bg-[#F5F7F6]/50 px-4 py-2.5 text-xs text-[#66736F] sm:hidden">
          <span>Geser tabel ke samping untuk melihat detail sesi →</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-[#172321]">
            <thead className="border-b border-[#DDE4E1] bg-[#F5F7F6] font-mono text-[11px] uppercase tracking-wider text-[#66736F]">
              <tr>
                <th scope="col" className="px-4 py-3">Waktu Sesi</th>
                <th scope="col" className="px-4 py-3">Berkas Wisuda</th>
                <th scope="col" className="px-4 py-3">Status</th>
                <th scope="col" className="px-4 py-3">Snapshot Batch Master</th>
                <th scope="col" className="px-4 py-3">Total Baris</th>
                <th scope="col" className="px-4 py-3">Ringkasan Hasil</th>
                <th scope="col" className="px-4 py-3 text-right">Aksi</th>
              </tr>
            </thead>
          <tbody className="divide-y divide-[#DDE4E1]">
            {loading ? (
              <tr>
                <td colSpan={7} className="p-8 text-center text-xs text-[#66736F]">
                  Memuat riwayat sinkronisasi...
                </td>
              </tr>
            ) : sessions.length === 0 ? (
              <tr>
                <td colSpan={7} className="p-8 text-center text-xs text-[#66736F]">
                  Belum ada sesi sinkronisasi yang dijalankan.{" "}
                  <Link href="/sinkronisasi" className="font-semibold text-[#0F766E] hover:underline">
                    Mulai sinkronisasi pertama
                  </Link>
                </td>
              </tr>
            ) : (
              sessions.map((sess) => (
                <tr key={sess.id} className="hover:bg-[#F5F7F6]/60 transition-colors">
                  <td className="px-4 py-3 font-mono text-[11px] text-[#66736F]">
                    {new Date(sess.created_at).toLocaleString("id-ID")}
                  </td>
                  <td className="px-4 py-3 font-semibold text-[#172321]">
                    {sess.file_name}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-block rounded-full border px-2.5 py-0.5 text-[10px] font-semibold ${
                        sess.status === "COMPLETED"
                          ? "border-emerald-200 bg-emerald-50 text-emerald-800"
                          : sess.status === "FAILED"
                          ? "border-rose-200 bg-rose-50 text-rose-800"
                          : "border-sky-200 bg-sky-50 text-sky-800"
                      }`}
                    >
                      ● {sess.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-[11px] text-[#66736F]">
                    <div className="flex items-center gap-1">
                      <span>SITASI:</span>
                      <code className="rounded bg-white border border-[#DDE4E1] px-1 font-mono text-[10px] text-[#0F766E]">{sess.sitasi_import_id.slice(0, 8)}</code>
                    </div>
                    <div className="mt-0.5 flex items-center gap-1">
                      <span>Certiport:</span>
                      <code className="rounded bg-white border border-[#DDE4E1] px-1 font-mono text-[10px] text-[#0F766E]">{sess.certiport_import_id.slice(0, 8)}</code>
                    </div>
                  </td>
                  <td className="px-4 py-3 font-bold tabular-nums text-[#172321]">
                    {sess.total_rows.toLocaleString("id-ID")}
                  </td>
                  <td className="px-4 py-3 text-xs">
                    {sess.status === "COMPLETED" ? (
                      <div className="flex flex-wrap gap-1.5">
                        <span className="rounded-full border border-emerald-200 bg-emerald-50 px-2 py-0.5 text-[10px] font-semibold text-emerald-800">
                          {sess.total_valid} Valid
                        </span>
                        <span className="rounded-full border border-amber-200 bg-amber-50 px-2 py-0.5 text-[10px] font-semibold text-amber-900">
                          {sess.total_review} Review
                        </span>
                        <span className="rounded-full border border-[#DDE4E1] bg-slate-100 px-2 py-0.5 text-[10px] font-semibold text-slate-700">
                          {sess.total_not_found} Tidak Ada
                        </span>
                      </div>
                    ) : (
                      <span className="text-[#66736F]">—</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Link
                      href={`/sinkronisasi/${sess.id}`}
                      className="inline-block rounded-lg border border-teal-200 bg-[#ECFAF8] px-3 py-1 text-xs font-semibold text-[#0F766E] shadow-xs hover:bg-teal-100"
                    >
                      Lihat Hasil
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
        </div>
      </div>

      {/* Pagination */}
      {total > 0 && (
        <div className="flex flex-col items-center justify-between gap-3 text-xs text-[#66736F] sm:flex-row">
          <p>
            Menampilkan sesi <span className="font-semibold text-[#172321] tabular-nums">{(page - 1) * limit + 1}</span>–<span className="font-semibold text-[#172321] tabular-nums">{Math.min(page * limit, total)}</span> dari <span className="font-semibold text-[#172321] tabular-nums">{total}</span>
          </p>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1 || loading}
              className="min-h-11 rounded-xl border border-[#DDE4E1] bg-white px-4 text-xs font-semibold text-[#172321] hover:bg-slate-50 disabled:opacity-40"
            >
              ← Sebelumnya
            </button>
            <span className="text-xs">
              Halaman <span className="font-semibold text-[#172321]">{page}</span> dari <span className="font-semibold text-[#172321]">{totalPages}</span>
            </span>
            <button
              type="button"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages || loading}
              className="min-h-11 rounded-xl border border-[#DDE4E1] bg-white px-4 text-xs font-semibold text-[#172321] hover:bg-slate-50 disabled:opacity-40"
            >
              Berikutnya →
            </button>
          </div>
        </div>
      )}
    </section>
  );
}
