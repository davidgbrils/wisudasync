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
          <div className="inline-flex items-center gap-1.5 rounded-full border border-teal-200 bg-teal-50 px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wider text-teal-800">
            Data Master Sumber
          </div>
          <h1 className="mt-2 text-2xl font-bold tracking-tight text-[#172321] sm:text-3xl">{title}</h1>
          <p className="mt-1 text-sm text-[#66736F]">
            {isSitasi
              ? "Master data SITASI terikat pada NIM mahasiswa sebagai kunci pencocokan primer."
              : "Master data Certiport tidak memiliki NIM; pencocokan menggunakan nama lengkap dan sub-program."}
          </p>
        </div>
        <span className="rounded-full border border-[#DDE4E1] bg-white px-3 py-1 font-mono text-xs font-medium tabular-nums text-[#172321] shadow-sm">
          {loading ? "Memuat…" : `${total.toLocaleString("id-ID")} baris data`}
        </span>
      </div>

      {!isSitasi && (
        <div className="flex items-start gap-3 rounded-lg border border-sky-200 bg-sky-50/70 p-4 text-xs text-sky-900">
          <span className="mt-0.5 inline-flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-sky-200 font-bold text-sky-800">i</span>
          <p className="leading-relaxed">
            <strong className="font-semibold text-sky-950">Aturan Pencocokan Certiport:</strong> Sumber data ini tidak memuat NIM mahasiswa. Sistem menggunakan normalisasi nama lengkap, program, dan hasil kelulusan. Apabila ditemukan nama ganda atau ambigu, sistem akan menandainya sebagai <span className="font-semibold">PERLU VERIFIKASI</span> untuk ditinjau oleh petugas.
          </p>
        </div>
      )}

      <section className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        <form onSubmit={handleUpload} className="rounded-2xl border border-[#DDE4E1] bg-white p-5 sm:p-6 shadow-xs lg:col-span-7">
          <h2 className="text-base font-bold text-[#172321]">Perbarui Data Master</h2>
          <p className="mt-1 text-xs text-[#66736F]">Unggah file workbook `.xlsx` untuk memperbarui batch aktif. Batas file 10 MiB.</p>
          <div className="mt-4 flex flex-wrap items-center gap-3">
            <label htmlFor={`${type}-file`} className="inline-flex min-h-11 cursor-pointer items-center rounded-xl border border-[#DDE4E1] bg-white px-4 text-xs font-semibold text-[#172321] shadow-xs hover:bg-[#F5F7F6] focus-within:ring-2 focus-within:ring-teal-700">
              Pilih File Excel (.xlsx)
              <input ref={fileInputRef} id={`${type}-file`} name="file" type="file" accept=".xlsx" className="sr-only" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
            </label>
            <span className="text-xs text-[#66736F] max-w-xs truncate" aria-live="polite">{file ? file.name : "Belum ada file dipilih"}</span>
            <button type="submit" disabled={!file || uploading} className="min-h-11 rounded-xl bg-[#0F766E] px-5 text-xs font-semibold text-white shadow-xs hover:bg-[#0F4B46] focus-visible:outline focus-visible:outline-2 focus-visible:outline-teal-700 disabled:cursor-not-allowed disabled:opacity-40">
              {uploading ? "Mengimpor Data…" : "Impor Batch Baru"}
            </button>
          </div>
          <p className="mt-3 text-[11px] text-[#66736F]">Proses impor bersifat atomik: jika validasi gagal, batch aktif sebelumnya tetap dipertahankan.</p>
          {uploading && <p className="mt-3 text-xs font-medium text-[#0F766E]" role="status">Sedang membaca dan memvalidasi struktur sheet…</p>}
          {notice && <p className="mt-3 rounded-xl border border-teal-200 bg-teal-50 px-3.5 py-2.5 text-xs font-medium text-teal-900" role="status" aria-live="polite">{notice}</p>}
        </form>

        <section className="rounded-2xl border border-[#DDE4E1] bg-white p-5 sm:p-6 shadow-xs lg:col-span-5" aria-labelledby="batch-heading">
          <div className="flex items-center justify-between gap-3">
            <h2 id="batch-heading" className="text-base font-bold text-[#172321]">Status Batch Aktif</h2>
            {batch && <span className="inline-flex items-center rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-0.5 text-[11px] font-semibold text-emerald-800">● Aktif</span>}
          </div>
          {loading ? (
            <p className="mt-4 text-xs text-[#66736F]">Memeriksa status batch aktif…</p>
          ) : batch ? (
            <dl className="mt-3.5 grid grid-cols-2 gap-3 text-xs">
              <div className="rounded-xl bg-[#F5F7F6] p-3 border border-[#DDE4E1]/50">
                <dt className="text-[11px] text-[#66736F]">Total Baris</dt>
                <dd className="mt-0.5 text-lg font-bold tabular-nums text-[#172321]">{batch.imported_rows.toLocaleString("id-ID")}</dd>
              </div>
              <div className="rounded-xl bg-[#F5F7F6] p-3 border border-[#DDE4E1]/50">
                <dt className="text-[11px] text-[#66736F]">Status Batch</dt>
                <dd className="mt-0.5 font-bold text-emerald-800">Selesai</dd>
              </div>
              <div className="col-span-2 rounded-xl bg-[#F5F7F6] p-3 border border-[#DDE4E1]/50">
                <dt className="text-[11px] text-[#66736F]">Waktu Impor</dt>
                <dd className="mt-0.5 font-medium text-[#172321]">{batchUpdatedAt ?? "Waktu tidak tersedia"}</dd>
              </div>
              <div className="col-span-2 rounded-xl bg-[#F5F7F6] p-3 border border-[#DDE4E1]/50">
                <dt className="text-[11px] text-[#66736F]">ID Referensi Batch</dt>
                <dd className="mt-0.5 font-mono text-[11px] text-[#0F766E] truncate">{batch.id}</dd>
              </div>
            </dl>
          ) : (
            <p className="mt-4 text-xs text-[#66736F]">Belum ada batch master aktif. Silakan impor file untuk memulai pencocokan.</p>
          )}
        </section>
      </section>

      <form onSubmit={applyFilters} className="grid gap-3.5 rounded-2xl border border-[#DDE4E1] bg-white p-5 sm:p-6 shadow-xs sm:grid-cols-2 lg:grid-cols-4">
        <div className="sm:col-span-2 lg:col-span-4">
          <h2 className="text-base font-bold text-[#172321]">Pencarian & Filter Data</h2>
          <p className="mt-0.5 text-xs text-[#66736F]">Penyaringan data diproses secara real-time di server pada batch aktif.</p>
        </div>
        {isSitasi ? (
          <>
            <FilterInput id="filter-nim" label="NIM Mahasiswa" value={draftFilters.nim} onChange={(value) => updateFilter("nim", value)} placeholder="Contoh: 210101..." />
            <FilterInput id="filter-sitasi-name" label="Nama Mahasiswa" value={draftFilters.nama} onChange={(value) => updateFilter("nama", value)} placeholder="Nama lengkap..." />
            <FilterInput id="filter-sertifikasi" label="Sertifikasi" value={draftFilters.sertifikasi} onChange={(value) => updateFilter("sertifikasi", value)} placeholder="MOS / MCF..." />
            <FilterInput id="filter-sitasi-status" label="Status Kelulusan" value={draftFilters.status} onChange={(value) => updateFilter("status", value)} placeholder="Lulus / Tidak Lulus..." />
          </>
        ) : (
          <>
            <FilterInput id="filter-certiport-name" label="Nama Kandidat" value={draftFilters.nama} onChange={(value) => updateFilter("nama", value)} placeholder="Nama kandidat..." />
            <FilterInput id="filter-program" label="Program Ujian" value={draftFilters.program} onChange={(value) => updateFilter("program", value)} placeholder="Microsoft Office Specialist..." />
            <FilterInput id="filter-result" label="Hasil Ujian" value={draftFilters.result} onChange={(value) => updateFilter("result", value)} placeholder="Pass / Fail..." />
          </>
        )}
        <div className="flex items-end gap-2.5 sm:col-span-2 lg:col-span-4 pt-1">
          <button type="submit" className="min-h-11 rounded-xl bg-[#0F766E] px-5 text-xs font-semibold text-white shadow-xs hover:bg-[#0F4B46] focus-visible:outline focus-visible:outline-2 focus-visible:outline-teal-700">
            Terapkan Filter
          </button>
          <button type="button" onClick={clearFilters} className="min-h-11 rounded-xl border border-[#DDE4E1] bg-white px-4 text-xs font-semibold text-[#172321] hover:bg-[#F5F7F6] focus-visible:outline focus-visible:outline-2 focus-visible:outline-teal-700">
            Reset
          </button>
        </div>
      </form>

      <section className="overflow-hidden rounded-2xl border border-[#DDE4E1] bg-white shadow-xs" aria-label={`Tabel ${title}`}>
        <div className="flex items-center justify-between border-b border-[#DDE4E1] bg-[#F5F7F6]/50 px-4 py-2.5 text-xs text-[#66736F] sm:hidden">
          <span>Geser tabel ke samping untuk melihat kolom →</span>
        </div>
        {loadError ? (
          <div className="p-8 text-center" role="alert">
            <p className="font-semibold text-[#172321]">Data belum dapat dimuat</p>
            <p className="mt-1 text-xs text-rose-700">{loadError}</p>
            <button type="button" onClick={() => setRefreshKey((value) => value + 1)} className="mt-4 min-h-10 rounded-xl border border-[#DDE4E1] px-4 text-xs font-semibold text-[#172321] hover:bg-slate-50">
              Coba lagi
            </button>
          </div>
        ) : loading ? (
          <div className="p-10 text-center text-xs text-[#66736F]" role="status">Memuat baris data master…</div>
        ) : items.length === 0 ? (
          <div className="p-10 text-center">
            <p className="font-semibold text-[#172321]">{batch ? "Tidak ada baris yang cocok" : "Data belum tersedia"}</p>
            <p className="mt-1 text-xs text-[#66736F]">{batch ? "Ubah kata kunci pencarian atau reset filter." : "Belum ada batch master aktif untuk sumber ini."}</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-xs">
              <caption className="sr-only">Data {title} dari batch aktif</caption>
              <thead className="border-b border-[#DDE4E1] bg-[#F5F7F6] font-mono text-[11px] uppercase tracking-wider text-[#66736F]">
                <tr>
                  {columns.map(([key, label]) => (
                    <th key={key} scope="col" className="whitespace-nowrap px-4 py-3 font-semibold">
                      {label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-[#DDE4E1]">
                {items.map((item, rowIndex) => (
                  <tr key={String(item.id ?? rowIndex)} className="hover:bg-[#F5F7F6]/60 transition-colors">
                    {columns.map(([key]) => {
                      const val = String(item[key] ?? "—");
                      const isNim = key === "nim";
                      const isStatus = key === "status" || key === "result";
                      const isPassed = /lulus|pass/i.test(val);
                      const isFailed = /tidak lulus|fail/i.test(val);

                      return (
                        <td key={key} className={`max-w-64 whitespace-nowrap px-4 py-3 text-[#172321] ${isNim ? "font-mono font-medium text-[#0F766E]" : ""}`}>
                          {isStatus && val !== "—" ? (
                            <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-semibold ${
                              isPassed
                                ? "border-emerald-200 bg-emerald-50 text-emerald-800"
                                : isFailed
                                ? "border-rose-200 bg-rose-50 text-rose-800"
                                : "border-[#DDE4E1] bg-slate-100 text-slate-700"
                            }`}>
                              {val}
                            </span>
                          ) : (
                            val
                          )}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {!loadError && !loading && (
          <div className="flex flex-wrap items-center justify-between gap-3 border-t border-[#DDE4E1] bg-[#F5F7F6]/40 px-4 py-3">
            <p className="text-xs text-[#66736F]">
              Halaman <span className="font-semibold text-[#172321] tabular-nums">{page}</span> dari <span className="font-semibold text-[#172321] tabular-nums">{pageCount}</span>
            </p>
            <div className="flex gap-2">
              <button type="button" onClick={() => setPage((value) => Math.max(1, value - 1))} disabled={page <= 1} className="min-h-8 rounded-lg border border-[#DDE4E1] bg-white px-3 text-xs font-medium text-[#172321] shadow-sm hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40">
                Sebelumnya
              </button>
              <button type="button" onClick={() => setPage((value) => Math.min(pageCount, value + 1))} disabled={page >= pageCount} className="min-h-8 rounded-lg border border-[#DDE4E1] bg-white px-3 text-xs font-medium text-[#172321] shadow-sm hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40">
                Berikutnya
              </button>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}

function FilterInput({ id, label, value, onChange, placeholder }: { id: string; label: string; value: string; onChange: (value: string) => void; placeholder?: string }) {
  return (
    <div className="min-w-0">
      <label htmlFor={id} className="mb-1 block text-xs font-medium text-[#172321]">
        {label}
      </label>
      <input
        id={id}
        name={id}
        type="search"
        autoComplete="off"
        placeholder={placeholder}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="min-h-9 w-full rounded-lg border border-[#DDE4E1] bg-white px-3 text-xs text-[#172321] placeholder:text-[#66736F]/60 focus:border-[#0F766E] focus:outline-none focus:ring-1 focus:ring-[#0F766E]"
      />
    </div>
  );
}
