"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { getJson, uploadExcel, type ActiveBatch, type BatchResponse, type MasterListResponse, type MasterRow } from "@/lib/api";

type MasterType = "sitasi" | "certiport";

type Props = {
  type: MasterType;
  title: string;
};

type Filters = { nim: string; nama: string; sertifikasi: string; status: string; program: string; result: string };

const EMPTY_FILTERS: Filters = { nim: "", nama: "", sertifikasi: "", status: "", program: "", result: "" };

export default function MasterDataPage({ type, title }: Props) {
  const [items, setItems] = useState<MasterRow[]>([]);
  const [total, setTotal] = useState(0);
  const [batch, setBatch] = useState<ActiveBatch | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [loadError, setLoadError] = useState("");
  const [notice, setNotice] = useState("");
  const [draftFilters, setDraftFilters] = useState<Filters>(EMPTY_FILTERS);
  const [filters, setFilters] = useState<Filters>(EMPTY_FILTERS);
  const [page, setPage] = useState(1);
  const [refreshKey, setRefreshKey] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const pageSize = 25;

  const isSitasi = type === "sitasi";
  const columns = isSitasi
    ? [["nim", "NIM"], ["nama", "Nama"], ["program_studi", "Program Studi"], ["sertifikasi", "Sertifikasi"], ["sub_program", "Sub Program"], ["nilai", "Nilai"], ["status", "Status"]]
    : [["full_name", "Nama"], ["program_name", "Program"], ["certification_name", "Sertifikasi"], ["score", "Nilai"], ["result", "Hasil"]];

  useEffect(() => {
    let current = true;
    setLoading(true);
    setLoadError("");
    setItems([]);
    setTotal(0);
    setBatch(null);
    const query = new URLSearchParams({ page: String(page), limit: String(pageSize) });
    if (isSitasi) {
      if (filters.nim.trim()) query.set("nim", filters.nim.trim());
      if (filters.nama.trim()) query.set("nama", filters.nama.trim());
      if (filters.sertifikasi.trim()) query.set("sertifikasi", filters.sertifikasi.trim());
      if (filters.status.trim()) query.set("status", filters.status.trim());
    } else {
      if (filters.nama.trim()) query.set("nama", filters.nama.trim());
      if (filters.program.trim()) query.set("program", filters.program.trim());
      if (filters.result.trim()) query.set("result", filters.result.trim());
    }

    Promise.all([
      getJson<MasterListResponse>(`/${type}?${query.toString()}`),
      getJson<BatchResponse>(`/${type}/batch`),
    ])
      .then(([listResponse, batchResponse]) => {
        if (!current) return;
        setItems(listResponse.data.items);
        setTotal(listResponse.data.total);
        setBatch(batchResponse.data);
      })
      .catch((error: unknown) => {
        if (current) setLoadError(error instanceof Error ? error.message : "Data belum dapat dimuat. Coba lagi.");
      })
      .finally(() => {
        if (current) setLoading(false);
      });

    return () => { current = false; };
  }, [filters, isSitasi, page, refreshKey, type]);

  function updateFilter(name: keyof Filters, value: string) {
    setDraftFilters((current) => ({ ...current, [name]: value }));
  }

  function applyFilters(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPage(1);
    setFilters({ ...draftFilters });
    setNotice("");
  }

  function clearFilters() {
    setDraftFilters(EMPTY_FILTERS);
    setFilters(EMPTY_FILTERS);
    setPage(1);
    setNotice("");
  }

  async function handleUpload(event: FormEvent) {
    event.preventDefault();
    if (!file) return;

    setUploading(true);
    setNotice("");
    try {
      const response = await uploadExcel<{ data?: { imported_rows?: number } }>(`/${type}/import`, file);
      const importedRows = Number(response.data?.imported_rows ?? 0);
      setNotice(`Import selesai. ${importedRows.toLocaleString("id-ID")} baris tersimpan dan batch baru aktif.`);
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
      setPage(1);
      setRefreshKey((value) => value + 1);
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Import gagal diproses. Coba lagi.");
    } finally {
      setUploading(false);
    }
  }

  const pageCount = Math.max(1, Math.ceil(total / pageSize));
  const batchUpdatedAt = batch?.completed_at
    ? new Intl.DateTimeFormat("id-ID", { dateStyle: "medium", timeStyle: "short" }).format(new Date(batch.completed_at))
    : null;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-teal-700">Data master</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-slate-900">{title}</h1>
          <p className="mt-1 text-sm text-slate-600">Cari, periksa, atau perbarui batch sumber {isSitasi ? "SITASI" : "Certiport"}.</p>
        </div>
        <span className="rounded-full bg-slate-200 px-3 py-1 text-sm tabular-nums text-slate-700">{loading ? "Memuat…" : `${total.toLocaleString("id-ID")} hasil`}</span>
      </div>

      <section className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(18rem,0.8fr)]">
        <form onSubmit={handleUpload} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="font-semibold text-slate-900">Perbarui data sumber</h2>
          <p className="mt-1 text-sm text-slate-600">Pilih workbook `.xlsx` sesuai template. Batas unggah 10 MiB.</p>
          <div className="mt-4 flex flex-wrap items-center gap-3">
            <label htmlFor={`${type}-file`} className="inline-flex min-h-11 cursor-pointer items-center rounded-md border border-slate-300 px-4 text-sm font-medium text-slate-800 hover:bg-slate-50 focus-within:ring-2 focus-within:ring-teal-700 focus-within:ring-offset-2">
              Pilih file Excel
              <input ref={fileInputRef} id={`${type}-file`} name="file" type="file" accept=".xlsx" className="sr-only" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
            </label>
            <span className="text-sm text-slate-600" aria-live="polite">{file ? "1 file dipilih" : "Belum ada file"}</span>
            <button type="submit" disabled={!file || uploading} className="min-h-11 rounded-md bg-slate-900 px-4 text-sm font-semibold text-white hover:bg-slate-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700 disabled:cursor-not-allowed disabled:opacity-50">
              {uploading ? "Mengunggah…" : "Import batch"}
            </button>
          </div>
          <p className="mt-3 text-xs text-slate-500">Batch aktif lama tetap digunakan jika import gagal.</p>
          {uploading && <p className="mt-3 text-sm text-teal-800" role="status">Mengunggah dan memvalidasi workbook…</p>}
          {notice && <p className="mt-3 rounded-md bg-teal-50 px-3 py-2 text-sm text-teal-900" role="status" aria-live="polite">{notice}</p>}
        </form>

        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm" aria-labelledby="batch-heading">
          <div className="flex items-center justify-between gap-3">
            <h2 id="batch-heading" className="font-semibold text-slate-900">Batch aktif</h2>
            {batch && <span className="rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-medium text-emerald-800">Aktif</span>}
          </div>
          {loading ? <p className="mt-4 text-sm text-slate-500">Memeriksa batch…</p> : batch ? (
            <dl className="mt-4 grid grid-cols-2 gap-4 text-sm">
              <div><dt className="text-slate-500">Baris sumber</dt><dd className="mt-1 font-semibold tabular-nums text-slate-900">{batch.imported_rows.toLocaleString("id-ID")}</dd></div>
              <div><dt className="text-slate-500">Status</dt><dd className="mt-1 font-semibold text-slate-900">Selesai</dd></div>
              <div className="col-span-2"><dt className="text-slate-500">Diperbarui</dt><dd className="mt-1 text-slate-800">{batchUpdatedAt ?? "Waktu tidak tersedia"}</dd></div>
              <div className="col-span-2"><dt className="text-slate-500">ID batch</dt><dd className="mt-1 font-mono text-xs text-slate-700">{batch.id}</dd></div>
            </dl>
          ) : <p className="mt-4 text-sm text-slate-600">Belum ada batch aktif. Import workbook untuk memulai.</p>}
        </section>
      </section>

      <form onSubmit={applyFilters} className="grid gap-3 rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:grid-cols-2 xl:grid-cols-4">
        <div className="sm:col-span-2 xl:col-span-4">
          <h2 className="font-semibold text-slate-900">Cari dan filter data</h2>
          <p className="mt-1 text-sm text-slate-600">Pencarian diterapkan di server pada batch aktif.</p>
        </div>
        {isSitasi ? <>
          <FilterInput id="filter-nim" label="NIM" value={draftFilters.nim} onChange={(value) => updateFilter("nim", value)} />
          <FilterInput id="filter-sitasi-name" label="Nama" value={draftFilters.nama} onChange={(value) => updateFilter("nama", value)} />
          <FilterInput id="filter-sertifikasi" label="Sertifikasi" value={draftFilters.sertifikasi} onChange={(value) => updateFilter("sertifikasi", value)} />
          <FilterInput id="filter-sitasi-status" label="Status sumber" value={draftFilters.status} onChange={(value) => updateFilter("status", value)} />
        </> : <>
          <FilterInput id="filter-certiport-name" label="Nama" value={draftFilters.nama} onChange={(value) => updateFilter("nama", value)} />
          <FilterInput id="filter-program" label="Program" value={draftFilters.program} onChange={(value) => updateFilter("program", value)} />
          <FilterInput id="filter-result" label="Hasil" value={draftFilters.result} onChange={(value) => updateFilter("result", value)} />
        </>}
        <div className="flex items-end gap-2 sm:col-span-2 xl:col-span-4">
          <button type="submit" className="min-h-10 rounded-md bg-teal-800 px-4 text-sm font-semibold text-white hover:bg-teal-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700">Terapkan filter</button>
          <button type="button" onClick={clearFilters} className="min-h-10 rounded-md border border-slate-300 px-4 text-sm font-medium text-slate-700 hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700">Reset</button>
        </div>
      </form>

      <section className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm" aria-label={`Tabel ${title}`}>
        {loadError ? (
          <div className="p-8 text-center" role="alert">
            <p className="font-medium text-slate-900">Data belum dapat dimuat</p>
            <p className="mt-1 text-sm text-slate-600">{loadError}</p>
            <button type="button" onClick={() => setRefreshKey((value) => value + 1)} className="mt-4 min-h-10 rounded-md border border-slate-300 px-4 text-sm font-medium hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700">Coba lagi</button>
          </div>
        ) : loading ? (
          <div className="p-10 text-center text-sm text-slate-600" role="status">Memuat data…</div>
        ) : items.length === 0 ? (
          <div className="p-10 text-center">
            <p className="font-medium text-slate-900">{batch ? "Tidak ada data yang cocok" : "Data belum tersedia"}</p>
            <p className="mt-1 text-sm text-slate-600">{batch ? "Ubah kata kunci atau reset filter." : "Belum ada batch aktif untuk sumber ini."}</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <caption className="sr-only">Data {title} dari batch aktif</caption>
              <thead className="bg-slate-100 text-xs uppercase tracking-wide text-slate-600">
                <tr>{columns.map(([key, label]) => <th key={key} scope="col" className="whitespace-nowrap px-4 py-3 font-semibold">{label}</th>)}</tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {items.map((item, rowIndex) => <tr key={String(item.id ?? rowIndex)} className="hover:bg-slate-50">
                  {columns.map(([key]) => <td key={key} className="max-w-64 whitespace-nowrap px-4 py-3 text-slate-800">{String(item[key] ?? "—")}</td>)}
                </tr>)}
              </tbody>
            </table>
          </div>
        )}
        {!loadError && !loading && <div className="flex flex-wrap items-center justify-between gap-3 border-t border-slate-200 px-4 py-3">
          <p className="text-sm text-slate-600">Halaman <span className="tabular-nums">{page}</span> dari <span className="tabular-nums">{pageCount}</span></p>
          <div className="flex gap-2">
            <button type="button" onClick={() => setPage((value) => Math.max(1, value - 1))} disabled={page <= 1} className="min-h-10 rounded-md border border-slate-300 px-3 text-sm hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700 disabled:cursor-not-allowed disabled:opacity-45">Sebelumnya</button>
            <button type="button" onClick={() => setPage((value) => Math.min(pageCount, value + 1))} disabled={page >= pageCount} className="min-h-10 rounded-md border border-slate-300 px-3 text-sm hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700 disabled:cursor-not-allowed disabled:opacity-45">Berikutnya</button>
          </div>
        </div>}
      </section>
    </div>
  );
}

function FilterInput({ id, label, value, onChange }: { id: string; label: string; value: string; onChange: (value: string) => void }) {
  return <div className="min-w-0">
    <label htmlFor={id} className="mb-1.5 block text-sm font-medium text-slate-700">{label}</label>
    <input id={id} name={id} type="search" autoComplete="off" value={value} onChange={(event) => onChange(event.target.value)} className="min-h-10 w-full rounded-md border border-slate-300 px-3 text-sm text-slate-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700" />
  </div>;
}
