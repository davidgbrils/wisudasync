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
    <section className="mx-auto max-w-6xl space-y-6">
      <header className="space-y-2">
        <p className="text-sm font-semibold uppercase tracking-[0.14em] text-teal-800">Riwayat Sesi</p>
        <h1 className="text-2xl font-semibold text-slate-950 sm:text-3xl">Riwayat Sinkronisasi</h1>
        <p className="max-w-3xl text-sm leading-6 text-slate-600">
          Daftar seluruh proses pencocokan data wisuda yang pernah dijalankan beserta versi snapshot batch masternya.
        </p>
      </header>

      {error && (
        <p role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-900">
          {error}
        </p>
      )}

      <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
        <table className="w-full text-left text-sm text-slate-800">
          <thead className="border-b border-slate-200 bg-slate-50 text-xs font-semibold uppercase text-slate-600">
            <tr>
              <th scope="col" className="px-4 py-3">Waktu</th>
              <th scope="col" className="px-4 py-3">Nama File</th>
              <th scope="col" className="px-4 py-3">Status</th>
              <th scope="col" className="px-4 py-3">Batch Master</th>
              <th scope="col" className="px-4 py-3">Total Baris</th>
              <th scope="col" className="px-4 py-3">Ringkasan Hasil</th>
              <th scope="col" className="px-4 py-3 text-right">Aksi</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading ? (
              <tr>
                <td colSpan={7} className="p-8 text-center text-slate-500">
                  Memuat riwayat sinkronisasi...
                </td>
              </tr>
            ) : sessions.length === 0 ? (
              <tr>
                <td colSpan={7} className="p-8 text-center text-slate-500">
                  Belum ada sesi sinkronisasi yang dijalankan.{" "}
                  <Link href="/sinkronisasi" className="font-semibold text-teal-800 hover:underline">
                    Mulai sinkronisasi pertama
                  </Link>
                </td>
              </tr>
            ) : (
              sessions.map((sess) => (
                <tr key={sess.id} className="hover:bg-slate-50/80">
                  <td className="px-4 py-3 text-xs text-slate-600">
                    {new Date(sess.created_at).toLocaleString("id-ID")}
                  </td>
                  <td className="px-4 py-3 font-medium text-slate-900">
                    {sess.file_name}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-block rounded-full border px-2.5 py-0.5 text-xs font-semibold ${
                        sess.status === "COMPLETED"
                          ? "border-emerald-200 bg-emerald-50 text-emerald-800"
                          : sess.status === "FAILED"
                          ? "border-rose-200 bg-rose-50 text-rose-800"
                          : "border-sky-200 bg-sky-50 text-sky-800"
                      }`}
                    >
                      {sess.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-500">
                    <div>SITASI: <code className="font-mono text-slate-700">{sess.sitasi_import_id.slice(0, 8)}</code></div>
                    <div>Certiport: <code className="font-mono text-slate-700">{sess.certiport_import_id.slice(0, 8)}</code></div>
                  </td>
                  <td className="px-4 py-3 font-semibold text-slate-900">
                    {sess.total_rows.toLocaleString("id-ID")}
                  </td>
                  <td className="px-4 py-3 text-xs">
                    {sess.status === "COMPLETED" ? (
                      <div className="flex flex-wrap gap-2">
                        <span className="rounded bg-emerald-50 px-1.5 py-0.5 font-medium text-emerald-800">
                          {sess.total_valid} Valid
                        </span>
                        <span className="rounded bg-amber-50 px-1.5 py-0.5 font-medium text-amber-900">
                          {sess.total_review} Review
                        </span>
                        <span className="rounded bg-slate-100 px-1.5 py-0.5 font-medium text-slate-700">
                          {sess.total_not_found} Tidak Ada
                        </span>
                      </div>
                    ) : (
                      <span className="text-slate-400">—</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Link
                      href={`/sinkronisasi/${sess.id}`}
                      className="rounded bg-teal-50 px-3 py-1 text-xs font-semibold text-teal-800 hover:bg-teal-100"
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

      {/* Pagination */}
      {total > 0 && (
        <div className="flex flex-col items-center justify-between gap-3 text-sm text-slate-600 sm:flex-row">
          <p>
            Menampilkan sesi {(page - 1) * limit + 1}–{Math.min(page * limit, total)} dari {total}
          </p>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1 || loading}
              className="rounded border border-slate-300 px-3 py-1.5 text-xs font-medium hover:bg-slate-50 disabled:opacity-50"
            >
              ← Sebelumnya
            </button>
            <span className="text-xs">
              Halaman {page} dari {totalPages}
            </span>
            <button
              type="button"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages || loading}
              className="rounded border border-slate-300 px-3 py-1.5 text-xs font-medium hover:bg-slate-50 disabled:opacity-50"
            >
              Berikutnya →
            </button>
          </div>
        </div>
      )}
    </section>
  );
}
