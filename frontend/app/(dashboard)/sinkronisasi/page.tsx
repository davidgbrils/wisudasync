"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";

import { startSync, uploadExcel, type ActiveBatch, type WisudaValidation } from "@/lib/api";

const MAX_FILE_BYTES = 10 * 1024 * 1024;

function formatBatch(batch: ActiveBatch | null): string {
  if (!batch) return "Belum ada batch aktif";
  return `Batch ${batch.id.slice(0, 8)} · ${batch.imported_rows.toLocaleString("id-ID")} baris · ${batch.status}`;
}

export default function WisudaUploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<WisudaValidation["data"] | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [dragging, setDragging] = useState(false);
  const errorRef = useRef<HTMLParagraphElement>(null);
  const resultRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (error) errorRef.current?.focus();
  }, [error]);

  useEffect(() => {
    if (result) resultRef.current?.focus();
  }, [result]);

  function chooseFile(selected: File | undefined) {
    setResult(null);
    setError("");
    if (!selected) return;
    if (!selected.name.toLowerCase().endsWith(".xlsx")) {
      setFile(null);
      setError("Pilih file dengan format .xlsx.");
      return;
    }
    if (selected.size > MAX_FILE_BYTES) {
      setFile(null);
      setError("Ukuran file melebihi batas 10 MiB.");
      return;
    }
    setFile(selected);
  }

  async function validateFile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file || busy || syncing) return;
    setBusy(true);
    setError("");
    setResult(null);
    try {
      const response = await uploadExcel<WisudaValidation>("/sync/validate", file);
      setResult(response.data);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "File belum dapat divalidasi.");
    } finally {
      setBusy(false);
    }
  }

  async function handleSync() {
    if (!file || busy || syncing) return;
    setSyncing(true);
    setError("");
    try {
      const response = await startSync(file);
      const sessionId = response.data?.session_id || response.data?.id;
      if (sessionId) {
        router.push(`/sinkronisasi/${sessionId}`);
      }
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Proses sinkronisasi gagal dijalankan.");
      setSyncing(false);
    }
  }

  return (
    <section className="mx-auto w-full max-w-6xl space-y-6 sm:space-y-8">
      <header className="space-y-1.5">
        <div className="inline-flex items-center gap-1.5 rounded-full border border-teal-200 bg-teal-50 px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wider text-teal-800">
          Tahap 1 · Pra-Sinkronisasi
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-[#172321] sm:text-3xl lg:text-4xl">Validasi Berkas Wisuda</h1>
        <p className="max-w-3xl text-xs sm:text-sm leading-relaxed text-[#66736F]">
          Unggah salinan workbook `.xlsx` untuk memeriksa kelengkapan struktur dan data mahasiswa. Tahap validasi bersifat read-only dan tidak mengubah berkas sumber.
        </p>
      </header>

      <form onSubmit={validateFile} className="space-y-4">
        <label
          htmlFor="wisuda-file"
          onDragOver={(event) => { event.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={(event) => {
            event.preventDefault();
            setDragging(false);
            chooseFile(event.dataTransfer.files[0]);
          }}
          className={`flex min-h-56 cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-8 text-center transition-all ${
            dragging
              ? "border-[#0F766E] bg-[#ECFAF8]"
              : "border-[#DDE4E1] bg-white hover:border-[#0F766E] hover:bg-[#F5F7F6]/50 shadow-xs"
          }`}
        >
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[#ECFAF8] text-[#0F766E] shadow-xs">
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>
          <span className="mt-3 text-sm sm:text-base font-bold text-[#172321]">
            {file ? file.name : "Tarik dan letakkan berkas Excel (.xlsx) di sini"}
          </span>
          <span className="mt-1 text-xs text-[#66736F]">
            Format workbook Microsoft Excel (.xlsx), ukuran maksimal 10 MiB
          </span>
          <span className="mt-4 inline-flex items-center rounded-xl border border-[#DDE4E1] bg-white px-4 py-2 text-xs font-semibold text-[#172321] shadow-xs hover:bg-slate-50">
            {file ? "Ganti Berkas Excel" : "Pilih Berkas dari Komputer"}
          </span>
          <input
            id="wisuda-file"
            name="wisudaFile"
            type="file"
            accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            className="sr-only"
            aria-describedby="wisuda-file-help"
            onChange={(event) => chooseFile(event.currentTarget.files?.[0])}
          />
          <span id="wisuda-file-help" className="sr-only">Workbook lokal diproses untuk validasi, tidak disimpan secara permanen.</span>
        </label>

        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          <button
            type="submit"
            disabled={!file || busy || syncing}
            className="min-h-11 w-full sm:w-auto rounded-xl border border-[#DDE4E1] bg-white px-5 py-2.5 text-xs font-semibold text-[#172321] shadow-xs hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-teal-800 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-400"
          >
            {busy ? "Memvalidasi Struktur…" : "Validasi Struktur Berkas"}
          </button>
          <button
            type="button"
            onClick={handleSync}
            disabled={!file || busy || syncing}
            className="min-h-11 w-full sm:w-auto rounded-xl bg-[#0F766E] px-6 py-2.5 text-xs font-semibold text-white shadow-xs hover:bg-[#0F4B46] focus-visible:outline focus-visible:outline-2 focus-visible:outline-teal-800 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            {syncing ? "Memproses Sinkronisasi…" : "Proses Sinkronisasi Sekarang"}
          </button>
          <p className="text-xs text-[#66736F] text-center sm:text-left" aria-live="polite">
            {syncing
              ? "Sedang membandingkan data wisuda dengan batch aktif SITASI & Certiport…"
              : busy
              ? "Workbook sedang diperiksa oleh sistem."
              : file
              ? "Berkas siap divalidasi atau disinkronkan."
              : "Belum ada berkas dipilih."}
          </p>
        </div>
      </form>

      {error && (
        <div ref={errorRef} tabIndex={-1} role="alert" className="rounded-xl border border-red-200 bg-red-50 p-4 text-xs font-medium text-red-900 shadow-sm">
          {error}
        </div>
      )}

      {result && (
        <section aria-labelledby="validation-result-title" className="space-y-5 rounded-2xl border border-[#DDE4E1] bg-white p-6 shadow-sm">
          <div ref={resultRef} tabIndex={-1} className="flex flex-col gap-2 rounded-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-teal-800 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <h2 id="validation-result-title" className="text-lg font-bold text-[#172321]">Hasil Pemeriksaan Validasi</h2>
              <p className="mt-0.5 text-xs text-[#66736F]" aria-live="polite">
                {result.is_valid
                  ? (result.empty_row_count > 0 || !result.layout_matches_template ? "Validasi dasar lolos dengan catatan penting." : "Struktur workbook sesuai standar template wisuda.")
                  : "Ditemukan masalah pada struktur kolom atau data wisuda."}
              </p>
            </div>
            <span className={`w-fit rounded-full border px-3 py-1 text-xs font-semibold ${
              result.is_valid
                ? (result.empty_row_count > 0 || !result.layout_matches_template ? "border-amber-200 bg-amber-50 text-amber-900" : "border-emerald-200 bg-emerald-50 text-emerald-800")
                : "border-rose-200 bg-rose-50 text-rose-900"
            }`}>
              {result.is_valid ? (result.empty_row_count > 0 || !result.layout_matches_template ? "Lolos Dengan Catatan" : "Lolos Validasi") : "Perlu Perbaikan"}
            </span>
          </div>

          {result.is_valid && (
            <div className="flex flex-col gap-3 rounded-xl border border-teal-200 bg-[#ECFAF8] p-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-xs font-bold text-teal-950">Berkas Siap Diproses Sinkronisasi</p>
                <p className="text-xs text-teal-800">Mulai perbandingan exact NIM ke SITASI dan nama lengkap ke Certiport.</p>
              </div>
              <button
                type="button"
                onClick={handleSync}
                disabled={syncing}
                className="min-h-9 shrink-0 rounded-lg bg-[#0F766E] px-4 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-[#0F4B46] disabled:cursor-not-allowed disabled:bg-slate-300"
              >
                {syncing ? "Sedang Memproses…" : "Mulai Sinkronisasi Sekarang"}
              </button>
            </div>
          )}

          <dl className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-xl border border-[#DDE4E1] bg-[#F5F7F6] p-4">
              <dt className="text-xs text-[#66736F]">Total Mahasiswa</dt>
              <dd className="mt-1 text-2xl font-bold tabular-nums text-[#172321]">{result.student_count.toLocaleString("id-ID")}</dd>
            </div>
            <div className="rounded-xl border border-[#DDE4E1] bg-[#F5F7F6] p-4">
              <dt className="text-xs text-[#66736F]">Baris Kosong</dt>
              <dd className="mt-1 text-2xl font-bold tabular-nums text-[#172321]">{result.empty_row_count.toLocaleString("id-ID")}</dd>
            </div>
            <div className="rounded-xl border border-[#DDE4E1] bg-[#F5F7F6] p-4">
              <dt className="text-xs text-[#66736F]">Sheet & Kolom</dt>
              <dd className="mt-1 text-sm font-semibold text-[#172321]">{result.sheet_name} · {result.columns.length} kolom</dd>
            </div>
          </dl>

          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-[#66736F]">Batch Master Aktif Saat Pemeriksaan</h3>
            <dl className="mt-2 grid gap-3 sm:grid-cols-2">
              <div className="rounded-xl border border-[#DDE4E1] bg-white p-3.5 shadow-sm">
                <dt className="text-[11px] font-semibold uppercase tracking-wide text-teal-800">Master SITASI</dt>
                <dd className="mt-1 font-mono text-xs text-[#172321]">{formatBatch(result.active_masters.sitasi)}</dd>
              </div>
              <div className="rounded-xl border border-[#DDE4E1] bg-white p-3.5 shadow-sm">
                <dt className="text-[11px] font-semibold uppercase tracking-wide text-teal-800">Master Certiport</dt>
                <dd className="mt-1 font-mono text-xs text-[#172321]">{formatBatch(result.active_masters.certiport)}</dd>
              </div>
            </dl>
          </div>

          {!result.layout_matches_template && (
            <p className="rounded-lg border border-amber-200 bg-amber-50 p-3.5 text-xs text-amber-950">
              Susunan kolom berbeda dari template baku. Berkas tetap dibaca apa adanya; pastikan kolom identitas mahasiswa sesuai sebelum melanjutkan.
            </p>
          )}

          {result.missing_columns.length > 0 && (
            <p className="rounded-lg border border-red-200 bg-red-50 p-3.5 text-xs text-red-900">
              Kolom wajib belum ditemukan: {result.missing_columns.join(", ")}.
            </p>
          )}

          {result.empty_row_count > 0 && (
            <div className="rounded-lg border border-amber-200 bg-amber-50 p-3.5 text-xs text-amber-950">
              <p>{result.empty_row_count.toLocaleString("id-ID")} baris kosong terdeteksi: {result.empty_rows.join(", ") || "baris lainnya"}{result.empty_rows_truncated ? ", dan seterusnya" : ""}.</p>
            </div>
          )}

          {result.issues.length > 0 && (
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-wider text-[#66736F]">Daftar Temuan Masalah</h3>
              <ul className="mt-2 divide-y divide-[#DDE4E1] rounded-xl border border-[#DDE4E1] bg-white">
                {result.issues.map((issue, index) => (
                  <li key={`${issue.code}-${issue.source_row}-${index}`} className="flex flex-col gap-1 px-4 py-3 text-xs sm:flex-row sm:gap-4">
                    <span className="shrink-0 font-medium text-[#172321]">{issue.source_row ? `Baris ${issue.source_row} · ${issue.field}` : issue.field}</span>
                    <span className="text-[#66736F]">{issue.message}</span>
                  </li>
                ))}
              </ul>
              {result.issues_truncated && <p className="mt-2 text-xs text-[#66736F]">Daftar masalah dibatasi. Perbaiki temuan di atas lalu lakukan validasi ulang.</p>}
            </div>
          )}

          <div className="border-t border-[#DDE4E1] pt-4">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-[#66736F]">Daftar Kolom Terbaca (Urutan Asli)</h3>
            <p className="mt-1.5 break-words font-mono text-xs leading-relaxed text-[#172321]">{result.columns.join(" · ")}</p>
            <p className="mt-2 text-[11px] text-[#66736F]">Prinsip non-destructive: validasi dan sinkronisasi tidak menimpa data asli tanpa persetujuan mapping final.</p>
          </div>
        </section>
      )}
    </section>
  );
}
