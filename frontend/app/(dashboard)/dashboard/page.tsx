"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { getJson, type ActiveBatch, type BatchResponse } from "@/lib/api";

type Summary = { sitasi: ActiveBatch | null; certiport: ActiveBatch | null };

export default function DashboardPage() {
  const [summary, setSummary] = useState<Summary | null>(null);
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
    ])
      .then(([sitasi, certiport]) => {
        if (current) setSummary({ sitasi: sitasi.data, certiport: certiport.data });
      })
      .catch((reason: unknown) => {
        if (current) setError(reason instanceof Error ? reason.message : "Ringkasan belum dapat dimuat.");
      })
      .finally(() => { if (current) setLoading(false); });
    return () => { current = false; };
  }, [retry]);

  return (
    <div className="space-y-8">
      <div className="rounded-2xl bg-slate-900 px-6 py-7 text-white sm:px-8 sm:py-9">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-teal-300">Ruang kerja petugas</p>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight sm:text-3xl">Ringkasan data master</h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-300">Periksa batch aktif dan buka data SITASI atau Certiport yang perlu dikelola.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <Link href="/sinkronisasi" className="flex items-center justify-between rounded-xl border border-teal-200 bg-teal-50/60 p-4 shadow-sm transition-colors hover:bg-teal-50">
          <div>
            <p className="font-semibold text-teal-950">Validasi & Sinkronisasi Wisuda</p>
            <p className="mt-0.5 text-xs text-teal-800">Unggah workbook wisuda dan jalankan pencocokan dengan data master.</p>
          </div>
          <span className="text-sm font-semibold text-teal-800">Buka →</span>
        </Link>
        <Link href="/riwayat" className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition-colors hover:bg-slate-50">
          <div>
            <p className="font-semibold text-slate-900">Riwayat Sinkronisasi</p>
            <p className="mt-0.5 text-xs text-slate-600">Periksa hasil pencocokan dan detail bukti sesi sebelumnya.</p>
          </div>
          <span className="text-sm font-semibold text-slate-700">Lihat →</span>
        </Link>
      </div>

      <section aria-labelledby="active-batches" className="space-y-4">
        <div>
          <h2 id="active-batches" className="text-lg font-semibold text-slate-900">Status batch aktif</h2>
          <p className="mt-1 text-sm text-slate-600">Informasi dimuat dari FastAPI. Tidak ada data contoh.</p>
        </div>
        {error ? <div className="rounded-xl border border-rose-200 bg-rose-50 p-5" role="alert">
          <p className="font-medium text-rose-900">Ringkasan gagal dimuat</p>
          <p className="mt-1 text-sm text-rose-800">{error}</p>
          <button type="button" onClick={() => setRetry((value) => value + 1)} className="mt-3 min-h-10 rounded-md border border-rose-300 px-3 text-sm font-medium text-rose-900 hover:bg-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-rose-700">Coba lagi</button>
        </div> : loading ? <div className="rounded-xl border border-slate-200 bg-white p-6 text-sm text-slate-600" role="status">Memeriksa batch…</div> : (
          <div className="grid gap-4 lg:grid-cols-2">
            <BatchCard title="SITASI" batch={summary?.sitasi ?? null} href="/sitasi" />
            <BatchCard title="Certiport" batch={summary?.certiport ?? null} href="/certiport" />
          </div>
        )}
      </section>
    </div>
  );
}

function BatchCard({ title, batch, href }: { title: string; batch: ActiveBatch | null; href: string }) {
  return <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
    <div className="flex items-start justify-between gap-3">
      <div>
        <p className="text-sm font-medium text-slate-500">{title}</p>
        <p className="mt-2 text-2xl font-semibold tabular-nums text-slate-900">{batch ? batch.imported_rows.toLocaleString("id-ID") : "—"}</p>
        <p className="mt-1 text-sm text-slate-600">{batch ? "baris pada batch aktif" : "belum ada batch aktif"}</p>
      </div>
      <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${batch ? "bg-emerald-100 text-emerald-800" : "bg-slate-100 text-slate-700"}`}>{batch ? "Aktif" : "Belum tersedia"}</span>
    </div>
    {batch && <p className="mt-4 truncate border-t border-slate-100 pt-3 font-mono text-xs text-slate-500">Batch {batch.id}</p>}
    <Link href={href} className="mt-4 inline-flex min-h-10 items-center rounded-md bg-slate-100 px-3 text-sm font-semibold text-slate-800 hover:bg-slate-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700">Buka data</Link>
  </article>;
}
