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
    <section className="mx-auto max-w-5xl space-y-6">
      <header className="space-y-2">
        <p className="text-sm font-semibold uppercase tracking-[0.14em] text-teal-800">Tahap sinkronisasi</p>
        <h1 className="text-2xl font-semibold text-slate-950 sm:text-3xl">Validasi file wisuda</h1>
        <p className="max-w-3xl text-sm leading-6 text-slate-600">
          Unggah salinan `.xlsx` untuk memeriksa struktur dan data dasar. Validasi tidak menyimpan atau mengubah workbook.
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
          className={`flex min-h-48 cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-5 py-8 text-center transition-colors focus-within:ring-2 focus-within:ring-teal-700 focus-within:ring-offset-2 ${dragging ? "border-teal-800 bg-teal-50" : "border-slate-300 bg-white hover:border-teal-700"}`}
        >
          <span className="text-base font-semibold text-slate-900">Tarik file Wisuda ke sini</span>
          <span className="mt-2 text-sm text-slate-600">atau pilih file `.xlsx`, maksimal 10 MiB</span>
          <span className="mt-3 text-sm font-medium text-teal-800">{file ? "1 file dipilih" : "Pilih file"}</span>
          <input
            id="wisuda-file"
            name="wisudaFile"
            type="file"
            accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            className="sr-only"
            aria-describedby="wisuda-file-help"
            onChange={(event) => chooseFile(event.currentTarget.files?.[0])}
          />
          <span id="wisuda-file-help" className="sr-only">Workbook lokal diproses untuk validasi, tidak disimpan.</span>
        </label>

        <div className="flex flex-wrap items-center gap-3">
          <button
            type="submit"
            disabled={!file || busy || syncing}
            className="min-h-11 rounded-lg border border-slate-300 bg-white px-5 py-2.5 text-sm font-semibold text-slate-800 transition-colors hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-800 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-400"
          >
            {busy ? "Memvalidasi…" : "Validasi file"}
          </button>
          <button
            type="button"
            onClick={handleSync}
            disabled={!file || busy || syncing}
            className="min-h-11 rounded-lg bg-teal-800 px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-teal-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-800 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            {syncing ? "Memproses sinkronisasi…" : "Proses Sinkronisasi"}
          </button>
          <p className="text-sm text-slate-600" aria-live="polite">
            {syncing
              ? "Sedang mencocokkan data wisuda dengan SITASI dan Certiport…"
              : busy
              ? "Workbook sedang diperiksa oleh backend."
              : file
              ? "Workbook siap diproses."
              : "Belum ada file dipilih."}
          </p>
        </div>
      </form>

      {error && <p ref={errorRef} tabIndex={-1} role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-900">{error}</p>}

      {result && (
        <section aria-labelledby="validation-result-title" className="space-y-5 rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
          <div ref={resultRef} tabIndex={-1} className="flex flex-col gap-2 rounded-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-teal-800 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <h2 id="validation-result-title" className="text-lg font-semibold text-slate-950">Hasil pemeriksaan</h2>
              <p className="mt-1 text-sm text-slate-600" aria-live="polite">
                {result.is_valid ? (result.empty_row_count > 0 || !result.layout_matches_template ? "Validasi dasar lolos dengan catatan." : "Validasi dasar lolos.") : "Perbaiki masalah berikut sebelum lanjut."}
              </p>
            </div>
            <span className={`w-fit rounded-full px-3 py-1 text-sm font-semibold ${result.is_valid ? "bg-emerald-50 text-emerald-800" : "bg-amber-50 text-amber-900"}`}>
              {result.is_valid ? (result.empty_row_count > 0 || !result.layout_matches_template ? "Lolos dengan catatan" : "Lolos") : "Perlu diperbaiki"}
            </span>
          </div>

          {result.is_valid && (
            <div className="flex flex-col gap-3 rounded-lg border border-teal-200 bg-teal-50 p-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm font-semibold text-teal-950">File siap disinkronkan</p>
                <p className="text-xs text-teal-800">Cocokkan data wisuda dengan batch aktif SITASI dan Certiport sekarang.</p>
              </div>
              <button
                type="button"
                onClick={handleSync}
                disabled={syncing}
                className="min-h-10 shrink-0 rounded-lg bg-teal-800 px-5 py-2 text-sm font-semibold text-white transition-colors hover:bg-teal-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-teal-800 disabled:cursor-not-allowed disabled:bg-slate-300"
              >
                {syncing ? "Sedang Memproses…" : "Mulai Sinkronisasi Sekarang"}
              </button>
            </div>
          )}

          <dl className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-lg bg-slate-50 p-4"><dt className="text-sm text-slate-600">Baris mahasiswa</dt><dd className="mt-1 text-2xl font-semibold tabular-nums text-slate-950">{result.student_count.toLocaleString("id-ID")}</dd></div>
            <div className="rounded-lg bg-slate-50 p-4"><dt className="text-sm text-slate-600">Baris kosong</dt><dd className="mt-1 text-2xl font-semibold tabular-nums text-slate-950">{result.empty_row_count.toLocaleString("id-ID")}</dd></div>
            <div className="rounded-lg bg-slate-50 p-4"><dt className="text-sm text-slate-600">Sheet dan kolom</dt><dd className="mt-1 text-base font-semibold text-slate-950">{result.sheet_name} · {result.columns.length} kolom</dd></div>
          </dl>

          <div>
            <h3 className="text-sm font-semibold text-slate-900">Batch master aktif saat diperiksa</h3>
            <dl className="mt-2 grid gap-3 sm:grid-cols-2">
              <div className="rounded-lg border border-slate-200 p-4"><dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">SITASI</dt><dd className="mt-1 text-sm text-slate-800">{formatBatch(result.active_masters.sitasi)}</dd></div>
              <div className="rounded-lg border border-slate-200 p-4"><dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">Certiport</dt><dd className="mt-1 text-sm text-slate-800">{formatBatch(result.active_masters.certiport)}</dd></div>
            </dl>
          </div>

          {!result.layout_matches_template && (
            <p className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-950">
              Susunan kolom berbeda dari template. File tetap tidak diubah; periksa kolom sebelum tahap berikutnya.
            </p>
          )}

          {result.missing_columns.length > 0 && (
            <p className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-900">
              Kolom wajib belum ditemukan: {result.missing_columns.join(", ")}.
            </p>
          )}

          {result.empty_row_count > 0 && (
            <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-950">
              <p>{result.empty_row_count.toLocaleString("id-ID")} baris kosong ditemukan: {result.empty_rows.join(", ") || "baris lainnya"}{result.empty_rows_truncated ? ", dan seterusnya" : ""}.</p>
            </div>
          )}

          {result.issues.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-slate-900">Masalah validasi</h3>
              <ul className="mt-2 divide-y divide-slate-200 rounded-lg border border-slate-200">
                {result.issues.map((issue, index) => (
                  <li key={`${issue.code}-${issue.source_row}-${index}`} className="flex flex-col gap-1 px-4 py-3 text-sm sm:flex-row sm:gap-4">
                    <span className="shrink-0 font-medium text-slate-700">{issue.source_row ? `Baris ${issue.source_row} · ${issue.field}` : issue.field}</span>
                    <span className="text-slate-600">{issue.message}</span>
                  </li>
                ))}
              </ul>
              {result.issues_truncated && <p className="mt-2 text-sm text-slate-600">Daftar masalah dibatasi. Perbaiki yang tampil, lalu validasi kembali.</p>}
            </div>
          )}

          <div className="border-t border-slate-200 pt-4">
            <h3 className="text-sm font-semibold text-slate-900">Kolom workbook (urutan asli)</h3>
            <p className="mt-1 break-words text-sm leading-6 text-slate-600">{result.columns.join(" · ")}</p>
            <p className="mt-2 text-xs text-slate-500">Validasi hanya membaca workbook. Kolom Sertifikasi MOS, Sertifikasi MCF, dan Title Microsoft tidak ditulis ulang.</p>
          </div>
        </section>
      )}
    </section>
  );
}
