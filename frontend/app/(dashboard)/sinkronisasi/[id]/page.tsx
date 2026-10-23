"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";

import {
  downloadSyncExport,
  getSyncResultDetail,
  getSyncResults,
  getSyncSession,
  submitReviewResult,
  type ReviewAuditItem,
  type SyncEvidenceItem,
  type SyncResultDetail,
  type SyncResultItem,
  type SyncSession,
} from "@/lib/api";
import { isMcfRelevant, getProgramStudiName, resolveKodeProdiFromNim } from "@/lib/prodi";

function statusBadgeClass(status: string | null | undefined): string {
  switch (status?.toUpperCase()) {
    case "VALID":
      return "bg-emerald-50 text-emerald-800 border-emerald-200";
    case "PERLU_VERIFIKASI":
      return "bg-amber-50 text-amber-900 border-amber-200";
    case "TIDAK_LULUS":
      return "bg-rose-50 text-rose-800 border-rose-200";
    case "PENDING":
      return "bg-sky-50 text-sky-800 border-sky-200";
    case "DATA_TIDAK_DITEMUKAN":
    default:
      return "bg-slate-100 text-slate-700 border-slate-200";
  }
}

function formatStatusLabel(status: string | null | undefined): string {
  if (!status) return "—";
  return status.replace(/_/g, " ");
}

function formatScoreBadges(programData: unknown) {
  if (!programData || typeof programData !== "object") return null;
  const data = programData as {
    score?: number | null;
    scores?: Record<string, number | null>;
    exam_details?: Array<{ sub_program?: string; score?: number | null }>;
  };

  if (Array.isArray(data.exam_details) && data.exam_details.length > 0) {
    const validScores = data.exam_details.filter(
      (d) => d.score !== null && d.score !== undefined
    );
    if (validScores.length > 0) {
      return (
        <div className="mt-1 flex flex-wrap gap-1">
          {validScores.map((ed, idx) => (
            <span
              key={idx}
              className="inline-flex items-center rounded border border-[#DDE4E1] bg-[#F5F7F6] px-1.5 py-0.5 font-mono text-[10px] text-[#2C3E3B]"
              title={`Skor ${ed.sub_program || "Ujian"}: ${ed.score}`}
            >
              {ed.sub_program ? `${ed.sub_program}: ` : "Skor: "}
              <span className="ml-0.5 font-semibold text-[#0F766E]">{ed.score}</span>
            </span>
          ))}
        </div>
      );
    }
  }

  if (data.scores && Object.keys(data.scores).length > 0) {
    const entries = Object.entries(data.scores).filter(
      ([, val]) => val !== null && val !== undefined
    );
    if (entries.length > 0) {
      return (
        <div className="mt-1 flex flex-wrap gap-1">
          {entries.map(([sub, score]) => (
            <span
              key={sub}
              className="inline-flex items-center rounded border border-[#DDE4E1] bg-[#F5F7F6] px-1.5 py-0.5 font-mono text-[10px] text-[#2C3E3B]"
            >
              {sub}: <span className="ml-0.5 font-semibold text-[#0F766E]">{score}</span>
            </span>
          ))}
        </div>
      );
    }
  }

  if (data.score !== null && data.score !== undefined) {
    return (
      <div className="mt-1">
        <span className="inline-flex items-center rounded border border-[#DDE4E1] bg-[#F5F7F6] px-1.5 py-0.5 font-mono text-[10px] text-[#2C3E3B]">
          Skor: <span className="ml-0.5 font-semibold text-[#0F766E]">{data.score}</span>
        </span>
      </div>
    );
  }

  return null;
}

/**
 * Tampilkan skor sumber SITASI dan Certiport secara terpisah di bawah badge status.
 * Menyelesaikan permintaan: "di sitasi muncul skor dan certiport juga".
 */
function renderSourceScores(programData: unknown) {
  if (!programData || typeof programData !== "object") return null;
  const data = programData as {
    exam_details?: Array<{
      sub_program?: string;
      sitasi_score?: number | null;
      sitasi_status?: string | null;
      certiport_score?: number | null;
      certiport_status?: string | null;
      certiport_only?: boolean;
    }>;
  };

  if (!Array.isArray(data.exam_details) || data.exam_details.length === 0) return null;

  const items = data.exam_details.filter(
    (d) => d.sitasi_score != null || d.certiport_score != null
  );
  if (items.length === 0) return null;

  return (
    <div className="mt-1 space-y-0.5">
      {items.map((ed, idx) => (
        <div key={idx} className="flex flex-wrap gap-1">
          {ed.sitasi_score != null && !ed.certiport_only && (
            <span
              className="inline-flex items-center rounded border border-teal-200 bg-teal-50/60 px-1 py-0.5 font-mono text-[9px] text-teal-900"
              title={`SITASI ${ed.sub_program || "Ujian"}: ${ed.sitasi_score} (${ed.sitasi_status || "—"})`}
            >
              <span className="mr-0.5 h-1.5 w-1.5 rounded-full bg-teal-600 inline-block" />
              S:{ed.sitasi_score}
              {ed.sitasi_status && (
                <span className={`ml-0.5 ${ed.sitasi_status.toUpperCase() === "LULUS" ? "text-emerald-700" : "text-rose-700"}`}>
                  ({ed.sitasi_status})
                </span>
              )}
            </span>
          )}
          {ed.certiport_score != null && (
            <span
              className="inline-flex items-center rounded border border-blue-200 bg-blue-50/60 px-1 py-0.5 font-mono text-[9px] text-blue-900"
              title={`Certiport ${ed.sub_program || "Ujian"}: ${ed.certiport_score} (${ed.certiport_status || "—"})`}
            >
              <span className="mr-0.5 h-1.5 w-1.5 rounded-full bg-blue-600 inline-block" />
              C:{ed.certiport_score}
              {ed.certiport_status && (
                <span className={`ml-0.5 ${ed.certiport_status.toUpperCase() === "PASS" ? "text-emerald-700" : "text-rose-700"}`}>
                  ({ed.certiport_status})
                </span>
              )}
            </span>
          )}
        </div>
      ))}
    </div>
  );
}

/**
 * Tampilkan kolom Title Microsoft berdasarkan status kelulusan MOS/MCF.
 * Format disetujui 2026-10-23: "MOS", "MCF", atau "MOS, MCF".
 */
function renderTitleMicrosoft(
  mosStatus: string | null | undefined,
  mcfStatus: string | null | undefined,
  kodeProdi: string
) {
  const mosLulus = mosStatus?.toUpperCase() === "VALID";
  const mcfLulus = mcfStatus?.toUpperCase() === "VALID";
  const mcfRelevant = isMcfRelevant(kodeProdi);

  if (!mosLulus && (!mcfRelevant || !mcfLulus)) {
    return <span className="text-[11px] text-[#66736F]">—</span>;
  }

  const titles: string[] = [];
  if (mosLulus) titles.push("MOS");
  if (mcfRelevant && mcfLulus) titles.push("MCF");

  return <span className="text-[11px] font-medium text-[#172321]">{titles.join(", ")}</span>;
}


export default function SyncResultDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const resolvedParams = use(params);
  const sessionId = resolvedParams.id;

  const [session, setSession] = useState<SyncSession | null>(null);
  const [results, setResults] = useState<SyncResultItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(25);

  const [statusFilter, setStatusFilter] = useState<string>("");
  const [needsReviewOnly, setNeedsReviewOnly] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeSearch, setActiveSearch] = useState("");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [selectedResult, setSelectedResult] = useState<SyncResultDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  const [downloading, setDownloading] = useState(false);
  const [exportError, setExportError] = useState("");

  const [reviewDecision, setReviewDecision] = useState<string>("KONFIRMASI_COCOK");
  const [reviewTarget, setReviewTarget] = useState<string>("ALL");
  const [reviewNote, setReviewNote] = useState<string>("");
  const [submittingReview, setSubmittingReview] = useState(false);
  const [reviewError, setReviewError] = useState("");
  const [reviewSuccess, setReviewSuccess] = useState("");

  useEffect(() => {
    async function loadSession() {
      try {
        const sessRes = await getSyncSession(sessionId);
        setSession(sessRes.data);
      } catch (cause) {
        setError(cause instanceof Error ? cause.message : "Gagal memuat sesi.");
      }
    }
    loadSession();
  }, [sessionId]);

  useEffect(() => {
    async function loadResults() {
      setLoading(true);
      setError("");
      try {
        const res = await getSyncResults(sessionId, {
          page,
          limit,
          status: statusFilter || undefined,
          search: activeSearch || undefined,
          needs_review: needsReviewOnly ? true : undefined,
        });
        setResults(res.data.items);
        setTotal(res.data.total);
      } catch (cause) {
        setError(cause instanceof Error ? cause.message : "Gagal memuat hasil.");
      } finally {
        setLoading(false);
      }
    }
    loadResults();
  }, [sessionId, page, limit, statusFilter, activeSearch, needsReviewOnly]);

  async function openDetailModal(item: SyncResultItem) {
    setLoadingDetail(true);
    // Tentukan pilihan awal review yang sesuai dengan kondisi mahasiswa
    if (item.validation_status === "VALID") {
      setReviewDecision("KONFIRMASI_COCOK");
    } else if (item.validation_status === "TIDAK_LULUS") {
      setReviewDecision("TIDAK_COCOK");
    } else {
      setReviewDecision("KONFIRMASI_COCOK");
    }
    setReviewTarget("ALL");
    setReviewNote(item.review_note?.replace(/^\[[A-Z_]+\]\s*/, "") || "");
    setReviewError("");
    setReviewSuccess("");
    try {
      const detail = await getSyncResultDetail(sessionId, item.id);
      setSelectedResult(detail.data);
      if (detail.data.review_note && !item.review_note) {
        setReviewNote(detail.data.review_note.replace(/^\[[A-Z_]+\]\s*/, ""));
      }
    } catch {
      setSelectedResult({
        ...item,
        evidence: [],
      });
    } finally {
      setLoadingDetail(false);
    }
  }

  async function handleReviewSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedResult || submittingReview) return;
    if (!reviewNote.trim()) {
      setReviewError("Catatan review wajib diisi.");
      return;
    }

    setSubmittingReview(true);
    setReviewError("");
    setReviewSuccess("");

    try {
      const res = await submitReviewResult(
        sessionId,
        selectedResult.id,
        reviewDecision,
        reviewNote.trim(),
        reviewTarget
      );
      setReviewSuccess("Keputusan review berhasil disimpan.");

      // Segarkan data detail dan perbarui status baris tabel secara sinkron
      try {
        const updatedDetail = await getSyncResultDetail(sessionId, selectedResult.id);
        setSelectedResult(updatedDetail.data);
        setResults((prev) =>
          prev.map((r) =>
            r.id === selectedResult.id
              ? {
                  ...r,
                  ...updatedDetail.data,
                }
              : r
          )
        );
      } catch {
        const newStatus = (res.data?.new_status as string) || selectedResult.validation_status;
        const newMos = (res.data?.mos_status as string) || selectedResult.mos_status;
        const newMcf = (res.data?.mcf_status as string) || selectedResult.mcf_status;
        const noteWithPrefix = `[${reviewDecision}] ${reviewNote.trim()}`;
        setSelectedResult((prev) =>
          prev
            ? {
                ...prev,
                validation_status: newStatus,
                mos_status: newMos,
                mcf_status: newMcf,
                review_note: noteWithPrefix,
                needs_review: reviewDecision !== "KONFIRMASI_COCOK",
              }
            : null
        );
        setResults((prev) =>
          prev.map((r) =>
            r.id === selectedResult.id
              ? {
                  ...r,
                  validation_status: newStatus,
                  mos_status: newMos,
                  mcf_status: newMcf,
                  review_note: noteWithPrefix,
                  needs_review: reviewDecision !== "KONFIRMASI_COCOK",
                }
              : r
          )
        );
      }

      // Refresh statistik sesi pada kartu ringkasan
      getSyncSession(sessionId).then((s) => setSession(s.data)).catch(() => {});
    } catch (cause) {
      setReviewError(cause instanceof Error ? cause.message : "Gagal menyimpan keputusan review.");
    } finally {
      setSubmittingReview(false);
    }
  }

  function handleSearchSubmit(e: React.FormEvent) {
    e.preventDefault();
    setPage(1);
    setActiveSearch(searchQuery.trim());
  }

  async function handleDownload(mode: "final" | "draft") {
    setDownloading(true);
    setExportError("");
    try {
      const blob = await downloadSyncExport(sessionId, mode);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const baseName = (session?.file_name || sessionId.slice(0, 8)).replace(/\.xlsx$/i, "");
      a.download = `wisuda_${mode}_${baseName}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (cause) {
      setExportError(cause instanceof Error ? cause.message : "Gagal mengunduh berkas hasil.");
    } finally {
      setDownloading(false);
    }
  }

  const totalPages = Math.ceil(total / limit) || 1;

  return (
    <section className="mx-auto max-w-7xl space-y-6">
      <header className="space-y-3">
        <div className="flex items-center gap-2 text-xs font-medium text-[#66736F]">
          <Link href="/sinkronisasi" className="hover:text-[#0F766E]">
            Validasi Wisuda
          </Link>
          <span>/</span>
          <Link href="/riwayat" className="hover:text-[#0F766E]">
            Riwayat Sinkronisasi
          </Link>
          <span>/</span>
          <span className="font-semibold text-[#172321]">Hasil Sesi</span>
        </div>

        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-[#172321] sm:text-3xl">
              Hasil Sinkronisasi Berkas
            </h1>
            <p className="mt-1 text-xs text-[#66736F]">
              Berkas Sumber: <span className="font-semibold text-[#172321]">{session?.file_name || "..."}</span>
              {session?.completed_at && (
                <span> · Diselesaikan pada {new Date(session.completed_at).toLocaleString("id-ID")}</span>
              )}
            </p>
          </div>
          {session && (
            <span
              className={`w-fit rounded-full border px-3 py-1 text-xs font-semibold ${
                session.status === "COMPLETED"
                  ? "border-emerald-200 bg-emerald-50 text-emerald-800"
                  : session.status === "FAILED"
                  ? "border-rose-200 bg-rose-50 text-rose-800"
                  : "border-sky-200 bg-sky-50 text-sky-800"
              }`}
            >
              ● {session.status}
            </span>
          )}
        </div>

        {session && (
          <div className="flex flex-wrap items-center gap-4 text-xs text-[#66736F]">
            <span>
              Batch Master SITASI: <code className="rounded bg-white border border-[#DDE4E1] px-1.5 py-0.5 font-mono text-xs text-[#0F766E]">{session.sitasi_import_id.slice(0, 8)}</code>
            </span>
            <span>
              Batch Master Certiport: <code className="rounded bg-white border border-[#DDE4E1] px-1.5 py-0.5 font-mono text-xs text-[#0F766E]">{session.certiport_import_id.slice(0, 8)}</code>
            </span>
          </div>
        )}
      </header>

      {/* KPI Cards */}
      {session && (
        <dl className="grid grid-cols-2 gap-3 sm:grid-cols-2 lg:grid-cols-4 lg:gap-6">
          <div className="rounded-2xl border border-[#DDE4E1] bg-white p-4 sm:p-5 shadow-xs">
            <dt className="text-[11px] font-semibold uppercase tracking-wider text-[#66736F]">Total Mahasiswa</dt>
            <dd className="mt-1 text-2xl sm:text-3xl font-bold tabular-nums text-[#172321]">{session.total_rows.toLocaleString("id-ID")}</dd>
          </div>
          <div className="rounded-2xl border border-emerald-200 bg-emerald-50/40 p-4 sm:p-5 shadow-xs">
            <dt className="text-[11px] font-semibold uppercase tracking-wider text-emerald-800">Valid (Siap)</dt>
            <dd className="mt-1 text-2xl sm:text-3xl font-bold tabular-nums text-emerald-900">{session.total_valid.toLocaleString("id-ID")}</dd>
          </div>
          <div className="rounded-2xl border border-amber-200 bg-amber-50/40 p-4 sm:p-5 shadow-xs">
            <dt className="text-[11px] font-semibold uppercase tracking-wider text-amber-900">Perlu Verifikasi</dt>
            <dd className="mt-1 text-2xl sm:text-3xl font-bold tabular-nums text-amber-950">{session.total_review.toLocaleString("id-ID")}</dd>
          </div>
          <div className="rounded-2xl border border-[#DDE4E1] bg-[#F5F7F6] p-4 sm:p-5 shadow-xs">
            <dt className="text-[11px] font-semibold uppercase tracking-wider text-[#66736F]">Tidak Ditemukan</dt>
            <dd className="mt-1 text-2xl sm:text-3xl font-bold tabular-nums text-[#172321]">{session.total_not_found.toLocaleString("id-ID")}</dd>
          </div>
        </dl>
      )}

      {/* Export Gate Action Bar */}
      <div className="flex flex-col gap-4 rounded-2xl border border-[#DDE4E1] bg-white p-5 sm:p-6 shadow-xs sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="text-sm sm:text-base font-bold text-[#172321]">Ekspor Berkas Hasil Wisuda</h3>
          <p className="mt-0.5 text-xs text-[#66736F]">
            Unduh berkas hasil dengan kolom sertifikasi terisi hanya untuk status LULUS. Gunakan pratinjau DRAFT untuk pemeriksaan internal.
          </p>
          {exportError && (
            <p role="alert" className="mt-1.5 text-xs font-medium text-rose-700">{exportError}</p>
          )}
        </div>
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 shrink-0">
          <button
            type="button"
            onClick={() => handleDownload("final")}
            disabled={downloading}
            className="inline-flex min-h-11 items-center justify-center rounded-xl bg-[#0F766E] px-4 py-2 text-xs font-semibold text-white shadow-xs hover:bg-[#0F4B46] disabled:opacity-50"
          >
            {downloading ? "Mengunduh…" : "Unduh Excel Final"}
          </button>
          <button
            type="button"
            onClick={() => handleDownload("draft")}
            disabled={downloading}
            className="inline-flex min-h-11 items-center justify-center rounded-xl border border-[#DDE4E1] bg-white px-4 py-2 text-xs font-semibold text-[#172321] hover:bg-[#F5F7F6] disabled:opacity-50"
          >
            Unduh Pratinjau (DRAFT)
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col gap-3 rounded-xl border border-[#DDE4E1] bg-white p-4 shadow-sm sm:flex-row sm:items-center sm:justify-between">
        <form onSubmit={handleSearchSubmit} className="flex flex-1 items-center gap-2">
          <input
            type="search"
            placeholder="Cari berdasarkan NIM atau Nama mahasiswa..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full max-w-sm rounded-lg border border-[#DDE4E1] bg-white px-3 py-1.5 text-xs text-[#172321] placeholder:text-[#66736F]/60 focus:border-[#0F766E] focus:outline-none focus:ring-1 focus:ring-[#0F766E]"
          />
          <button
            type="submit"
            className="rounded-lg bg-[#0F766E] px-3.5 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-[#0F4B46]"
          >
            Cari
          </button>
          {activeSearch && (
            <button
              type="button"
              onClick={() => { setSearchQuery(""); setActiveSearch(""); setPage(1); }}
              className="text-xs text-[#66736F] hover:text-[#172321]"
            >
              Reset
            </button>
          )}
        </form>

        <div className="flex flex-wrap items-center gap-4">
          <label className="flex items-center gap-2 text-xs font-medium text-[#172321] cursor-pointer">
            <input
              type="checkbox"
              checked={needsReviewOnly}
              onChange={(e) => { setNeedsReviewOnly(e.target.checked); setPage(1); }}
              className="h-4 w-4 rounded border-[#DDE4E1] text-[#0F766E] focus:ring-[#0F766E]"
            />
            Hanya Perlu Review
          </label>

          <div className="flex items-center gap-2">
            <label htmlFor="filter-status" className="text-xs text-[#66736F]">Status:</label>
            <select
              id="filter-status"
              value={statusFilter}
              onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
              className="rounded-lg border border-[#DDE4E1] bg-white px-2.5 py-1.5 text-xs text-[#172321] focus:border-[#0F766E] focus:outline-none focus:ring-1 focus:ring-[#0F766E]"
            >
              <option value="">Semua Status</option>
              <option value="VALID">VALID</option>
              <option value="PERLU_VERIFIKASI">PERLU VERIFIKASI</option>
              <option value="TIDAK_LULUS">TIDAK LULUS</option>
              <option value="PENDING">PENDING</option>
              <option value="DATA_TIDAK_DITEMUKAN">DATA TIDAK DITEMUKAN</option>
            </select>
          </div>
        </div>
      </div>

      {error && (
        <p role="alert" className="rounded-xl border border-red-200 bg-red-50 p-4 text-xs text-red-900 shadow-sm">
          {error}
        </p>
      )}

      {/* Table */}
      <div className="overflow-x-auto rounded-xl border border-[#DDE4E1] bg-white shadow-sm">
        <div className="px-4 py-2 text-[10px] text-[#66736F] sm:hidden">← Geser tabel untuk melihat selengkapnya →</div>
        <table className="w-full text-left text-xs text-[#172321]">
          <thead className="border-b border-[#DDE4E1] bg-[#F5F7F6] font-mono text-[11px] uppercase tracking-wider text-[#66736F]">
            <tr>
              <th scope="col" className="px-3 py-3 text-center w-10">No</th>
              <th scope="col" className="px-3 py-3 w-16">Kode Prodi</th>
              <th scope="col" className="px-3 py-3">Program Studi</th>
              <th scope="col" className="px-3 py-3 w-24">NIM</th>
              <th scope="col" className="px-3 py-3">Nama</th>
              <th scope="col" className="px-3 py-3">Sertifikasi MOS</th>
              <th scope="col" className="px-3 py-3">Sertifikasi MCF</th>
              <th scope="col" className="px-3 py-3">Title Microsoft</th>
              <th scope="col" className="px-3 py-3 text-right w-20">Aksi</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#DDE4E1]">
            {loading ? (
              <tr>
                <td colSpan={9} className="p-8 text-center text-xs text-[#66736F]">
                  Memuat data hasil sinkronisasi...
                </td>
              </tr>
            ) : results.length === 0 ? (
              <tr>
                <td colSpan={9} className="p-8 text-center text-xs text-[#66736F]">
                  Tidak ada baris yang cocok dengan kriteria filter.
                </td>
              </tr>
            ) : (
              results.map((row, idx) => {
                const rowNo = (page - 1) * limit + idx + 1;
                const kodeProdi = resolveKodeProdiFromNim(row.nim) || row.kode_prodi || "";
                const isMcfRelevantForProdi = isMcfRelevant(kodeProdi);
                const displayProdi = getProgramStudiName(kodeProdi) || row.program_studi || "—";

                // Bangun teks sertifikasi MOS
                const mosProg = row.mos_programs as Record<string, unknown> | null;
                const mcfProg = row.mcf_programs as Record<string, unknown> | null;

                return (
                <tr key={row.id} className="hover:bg-[#F5F7F6]/60 transition-colors">
                  <td className="px-3 py-3 align-top text-center font-mono text-xs text-[#66736F]">{rowNo}</td>
                  <td className="px-3 py-3 align-top font-mono text-xs text-[#172321]">{kodeProdi || "—"}</td>
                  <td className="px-3 py-3 align-top text-xs text-[#172321] max-w-[140px] truncate" title={displayProdi}>
                    {displayProdi}
                  </td>
                  <td className="px-3 py-3 align-top font-mono font-medium text-[#0F766E]">{row.nim}</td>
                  <td className="px-3 py-3 align-top font-medium text-[#172321]">
                    <div>{row.nama_wisuda}</div>
                    {row.nama_sitasi && row.nama_sitasi !== row.nama_wisuda && (
                      <div className="text-[11px] text-[#66736F]">SITASI: {row.nama_sitasi}</div>
                    )}
                  </td>

                  {/* Kolom Sertifikasi MOS: status + skor SITASI & Certiport */}
                  <td className="px-3 py-3 align-top">
                    <div className="space-y-1">
                      <span className={`inline-block rounded-full border px-2 py-0.5 text-[10px] font-semibold ${statusBadgeClass(row.mos_status)}`}>
                        {formatStatusLabel(row.mos_status)}
                      </span>
                      {formatScoreBadges(mosProg)}
                      {renderSourceScores(mosProg)}
                    </div>
                  </td>

                  {/* Kolom Sertifikasi MCF: hanya untuk prodi yang relevan (misal 31/32) */}
                  <td className="px-3 py-3 align-top">
                    {isMcfRelevantForProdi ? (
                      <div className="space-y-1">
                        <span className={`inline-block rounded-full border px-2 py-0.5 text-[10px] font-semibold ${statusBadgeClass(row.mcf_status)}`}>
                          {formatStatusLabel(row.mcf_status)}
                        </span>
                        {formatScoreBadges(mcfProg)}
                        {renderSourceScores(mcfProg)}
                      </div>
                    ) : (
                      <span className="text-[11px] text-[#66736F] italic">N/A</span>
                    )}
                  </td>

                  {/* Kolom Title Microsoft */}
                  <td className="px-3 py-3 align-top">
                    {renderTitleMicrosoft(row.mos_status, row.mcf_status, kodeProdi)}
                  </td>

                  <td className="px-3 py-3 align-top text-right">
                    <button
                      type="button"
                      onClick={() => openDetailModal(row)}
                      className="rounded-lg border border-teal-200 bg-[#ECFAF8] px-3 py-1 text-xs font-semibold text-[#0F766E] hover:bg-teal-100 shadow-xs"
                    >
                      Detail
                    </button>
                  </td>
                </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex flex-col items-center justify-between gap-3 text-xs text-[#66736F] sm:flex-row">
        <p>
          Menampilkan baris <span className="font-semibold text-[#172321] tabular-nums">{(page - 1) * limit + 1}</span>–<span className="font-semibold text-[#172321] tabular-nums">{Math.min(page * limit, total)}</span> dari <span className="font-semibold text-[#172321] tabular-nums">{total.toLocaleString("id-ID")}</span>
        </p>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1 || loading}
            className="rounded-lg border border-[#DDE4E1] bg-white px-3 py-1.5 text-xs font-medium text-[#172321] hover:bg-slate-50 disabled:opacity-40"
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
            className="rounded-lg border border-[#DDE4E1] bg-white px-3 py-1.5 text-xs font-medium text-[#172321] hover:bg-slate-50 disabled:opacity-40"
          >
            Berikutnya →
          </button>
        </div>
      </div>

      {/* Evidence Detail Modal (Screen 07) */}
      {selectedResult && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="modal-title"
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 p-4 backdrop-blur-xs"
        >
          <div className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-2xl border border-[#DDE4E1] bg-white p-6 shadow-2xl">
            <div className="flex items-start justify-between border-b border-[#DDE4E1] pb-4">
              <div>
                <div className="inline-flex items-center gap-1.5 rounded-full border border-teal-200 bg-teal-50 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-teal-800">
                  Panel Verifikasi Silang
                </div>
                <h3 id="modal-title" className="mt-1 text-lg font-bold text-[#172321]">
                  Rincian Bukti & Evaluasi Mahasiswa
                </h3>
                <p className="mt-0.5 font-mono text-xs text-[#66736F]">
                  Baris #{selectedResult.source_row} · NIM <span className="font-semibold text-[#0F766E]">{selectedResult.nim}</span> · {selectedResult.nama_wisuda}
                </p>
                <p className="mt-0.5 text-xs text-[#0F766E]">
                  Program Studi: <span className="font-medium text-[#172321]">{getProgramStudiName(resolveKodeProdiFromNim(selectedResult.nim) || selectedResult.kode_prodi, selectedResult.program_studi) || "—"}</span> (Kode {resolveKodeProdiFromNim(selectedResult.nim) || selectedResult.kode_prodi || "—"})
                </p>
              </div>
              <button
                type="button"
                onClick={() => setSelectedResult(null)}
                className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-700"
              >
                ✕
              </button>
            </div>

            <div className="mt-4 space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3 rounded-xl border border-[#DDE4E1] bg-[#F5F7F6] p-3.5">
                <div>
                  <span className="font-semibold text-[#66736F]">Pencocokan Nama:</span>{" "}
                  <span className="font-mono font-medium text-[#172321]">{selectedResult.name_match_type || "—"}</span>
                </div>
                <div>
                  <span className="font-semibold text-[#66736F]">Status Hasil:</span>{" "}
                  <span className={`inline-block rounded-full border px-2 py-0.5 font-semibold ${statusBadgeClass(selectedResult.validation_status)}`}>
                    {selectedResult.validation_status}
                  </span>
                </div>
                {selectedResult.nama_sitasi && (
                  <div className="col-span-2">
                    <span className="font-semibold text-[#66736F]">Nama Tercatat di SITASI:</span>{" "}
                    <span className="font-medium text-[#172321]">{selectedResult.nama_sitasi}</span>
                  </div>
                )}
                {selectedResult.review_note && (
                  <div className="col-span-2">
                    <span className="font-semibold text-amber-900">Catatan Review Aktif:</span>{" "}
                    <span className="text-amber-950">{selectedResult.review_note}</span>
                  </div>
                )}
              </div>

              {/* Ringkasan Program Sertifikasi MOS & MCF */}
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <div className="rounded-xl border border-[#DDE4E1] bg-[#F5F7F6]/70 p-3.5 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-[#172321]">Sertifikasi MOS</span>
                    <span className={`rounded-full border px-2 py-0.5 text-[10px] font-semibold ${statusBadgeClass(selectedResult.mos_status)}`}>
                      {formatStatusLabel(selectedResult.mos_status)}
                    </span>
                  </div>
                  <div className="text-xs">
                    {formatScoreBadges(selectedResult.mos_programs) || (
                      <span className="font-mono text-[11px] text-[#66736F]">Tidak ada catatan skor</span>
                    )}
                  </div>
                  {Boolean((selectedResult.mos_programs as Record<string, unknown> | null)?.sitasi_name || (selectedResult.mos_programs as Record<string, unknown> | null)?.certiport_name) && (
                    <div className="pt-2 border-t border-[#DDE4E1]/80 space-y-1 text-[11px]">
                      {Boolean((selectedResult.mos_programs as Record<string, unknown> | null)?.sitasi_name) && (
                        <div className="flex items-center justify-between text-[#66736F]">
                          <span>Nama di SITASI:</span>
                          <span className="font-medium text-[#172321]">{String((selectedResult.mos_programs as Record<string, unknown>).sitasi_name)}</span>
                        </div>
                      )}
                      {Boolean((selectedResult.mos_programs as Record<string, unknown> | null)?.certiport_name) && (
                        <div className="flex items-center justify-between text-[#66736F]">
                          <span>Nama di Certiport:</span>
                          <span className="font-medium text-[#0F766E]">{String((selectedResult.mos_programs as Record<string, unknown>).certiport_name)}</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                <div className="rounded-xl border border-[#DDE4E1] bg-[#F5F7F6]/70 p-3.5 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-[#172321]">Sertifikasi MCF</span>
                    <span className={`rounded-full border px-2 py-0.5 text-[10px] font-semibold ${statusBadgeClass(selectedResult.mcf_status)}`}>
                      {formatStatusLabel(selectedResult.mcf_status)}
                    </span>
                  </div>
                  <div className="text-xs">
                    {formatScoreBadges(selectedResult.mcf_programs) || (
                      <span className="font-mono text-[11px] text-[#66736F]">Tidak ada catatan skor</span>
                    )}
                  </div>
                  {Boolean((selectedResult.mcf_programs as Record<string, unknown> | null)?.sitasi_name || (selectedResult.mcf_programs as Record<string, unknown> | null)?.certiport_name) && (
                    <div className="pt-2 border-t border-[#DDE4E1]/80 space-y-1 text-[11px]">
                      {Boolean((selectedResult.mcf_programs as Record<string, unknown> | null)?.sitasi_name) && (
                        <div className="flex items-center justify-between text-[#66736F]">
                          <span>Nama di SITASI:</span>
                          <span className="font-medium text-[#172321]">{String((selectedResult.mcf_programs as Record<string, unknown>).sitasi_name)}</span>
                        </div>
                      )}
                      {Boolean((selectedResult.mcf_programs as Record<string, unknown> | null)?.certiport_name) && (
                        <div className="flex items-center justify-between text-[#66736F]">
                          <span>Nama di Certiport:</span>
                          <span className="font-medium text-[#0F766E]">{String((selectedResult.mcf_programs as Record<string, unknown>).certiport_name)}</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>

              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wider text-[#66736F]">
                  Bukti Verifikasi Silang per Sub-Ujian
                </h4>
                {loadingDetail ? (
                  <p className="mt-2 text-xs text-[#66736F]">Memuat rincian bukti sumber...</p>
                ) : !selectedResult.evidence || selectedResult.evidence.length === 0 ? (
                  <p className="mt-2 text-xs text-[#66736F]">Tidak ada rekam bukti yang terdaftar.</p>
                ) : (
                  <div className="mt-2 space-y-3">
                    {selectedResult.evidence.map((ev: SyncEvidenceItem, idx: number) => {
                      const isCertiportOnly = Boolean(ev.certiport_row_id && !ev.sitasi_row_id);
                      const isSitasiOnly = Boolean(ev.sitasi_row_id && !ev.certiport_row_id);

                      const hasSitasi = Boolean(ev.sitasi_row_id || (ev.sitasi_score !== null && ev.sitasi_score !== undefined) || (ev.sitasi_name && !isCertiportOnly));
                      const hasCertiport = Boolean(ev.certiport_row_id || (ev.certiport_score !== null && ev.certiport_score !== undefined) || (ev.certiport_name && !isSitasiOnly));

                      return (
                        <div
                          key={ev.id || idx}
                          className="rounded-xl border border-[#DDE4E1] bg-white p-4 shadow-xs space-y-3"
                        >
                          <div className="flex items-center justify-between border-b border-[#DDE4E1]/80 pb-2.5">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-bold text-[#172321]">
                                {ev.category}
                                {ev.exam && ev.exam !== ev.category ? ` · ${ev.exam}` : ""}
                              </span>
                              <span className="font-mono text-[11px] text-[#66736F]">
                                ({ev.match_method || "NIM_EXACT+NAME_CERTIPORT"})
                              </span>
                            </div>
                            <span
                              className={`rounded-full border px-2.5 py-0.5 text-[10px] font-semibold ${statusBadgeClass(ev.evidence_status)}`}
                            >
                              {ev.evidence_status}
                            </span>
                          </div>

                          {ev.reason && (
                            <p className="text-xs text-[#66736F] leading-relaxed">
                              {ev.reason}
                            </p>
                          )}

                          {(ev.duplicate_count ?? 0) > 0 && (
                            <p className="rounded-lg border border-[#DDE4E1] bg-[#F5F7F6] px-2.5 py-1.5 text-[11px] text-[#66736F] italic">
                              {ev.duplicate_count} bukti duplikat untuk sub-ujian ini disembunyikan — ditampilkan yang lulus.
                            </p>
                          )}

                          {/* Grid Perbandingan 2 Sumber: SITASI & Certiport */}
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                            {/* Kolom 1: Sumber SITASI */}
                            <div className="rounded-lg border border-[#DDE4E1] bg-[#F5F7F6]/50 p-3 space-y-2">
                              <div className="flex items-center justify-between">
                                <span className="inline-flex items-center gap-1.5 font-semibold text-[11px] text-[#172321]">
                                  <span className="h-2 w-2 rounded-full bg-teal-600" />
                                  Basis Data SITASI
                                </span>
                                {ev.sitasi_row_id && (
                                  <span
                                    className="font-mono text-[10px] text-[#66736F]"
                                    title={ev.sitasi_file_name ? `Sumber: ${ev.sitasi_file_name} baris ${ev.sitasi_source_row ?? ev.sitasi_row_id}` : undefined}
                                  >
                                    {ev.sitasi_file_name ? `${ev.sitasi_file_name} · ` : ""}Baris #{ev.sitasi_source_row ?? ev.sitasi_row_id}
                                  </span>
                                )}
                              </div>
                              {hasSitasi ? (
                                <div className="space-y-1.5 text-xs">
                                  <div className="flex items-start justify-between gap-2">
                                    <span className="text-[#66736F]">Nama:</span>
                                    <span className="font-medium text-[#172321] text-right">
                                      {ev.sitasi_name || (ev.sitasi_row_id ? selectedResult.nama_sitasi : null) || "—"}
                                    </span>
                                  </div>
                                  <div className="flex items-center justify-between">
                                    <span className="text-[#66736F]">Skor:</span>
                                    <span className="font-mono font-bold text-[#0F766E]">
                                      {ev.sitasi_score !== null && ev.sitasi_score !== undefined
                                        ? ev.sitasi_score
                                        : (isSitasiOnly && ev.match_score !== null ? ev.match_score : "—")}
                                    </span>
                                  </div>
                                  {ev.sitasi_status && (
                                    <div className="flex items-center justify-between">
                                      <span className="text-[#66736F]">Status:</span>
                                      <span className={`inline-block rounded px-1.5 py-0.5 text-[10px] font-semibold ${
                                        ev.sitasi_status.toUpperCase() === "LULUS"
                                          ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
                                          : "bg-rose-50 text-rose-800 border border-rose-200"
                                      }`}>
                                        {ev.sitasi_status}
                                      </span>
                                    </div>
                                  )}
                                </div>
                              ) : (
                                <p className="text-[11px] text-[#66736F] italic">
                                  Tidak ada rekaman attempt di data SITASI
                                </p>
                              )}
                            </div>

                            {/* Kolom 2: Sumber Certiport */}
                            <div className="rounded-lg border border-[#DDE4E1] bg-[#F5F7F6]/50 p-3 space-y-2">
                              <div className="flex items-center justify-between">
                                <span className="inline-flex items-center gap-1.5 font-semibold text-[11px] text-[#172321]">
                                  <span className="h-2 w-2 rounded-full bg-blue-600" />
                                  Sertifikat Certiport
                                </span>
                                {ev.certiport_row_id && (
                                  <span
                                    className="font-mono text-[10px] text-[#66736F]"
                                    title={ev.certiport_file_name ? `Sumber: ${ev.certiport_file_name} baris ${ev.certiport_source_row ?? ev.certiport_row_id}` : undefined}
                                  >
                                    {ev.certiport_file_name ? `${ev.certiport_file_name} · ` : ""}Baris #{ev.certiport_source_row ?? ev.certiport_row_id}
                                  </span>
                                )}
                              </div>
                              {hasCertiport ? (
                                <div className="space-y-1.5 text-xs">
                                  <div className="flex items-start justify-between gap-2">
                                    <span className="text-[#66736F]">Nama:</span>
                                    <span className="font-medium text-[#172321] text-right">
                                      {ev.certiport_name || selectedResult.nama_wisuda || "—"}
                                    </span>
                                  </div>
                                  <div className="flex items-center justify-between">
                                    <span className="text-[#66736F]">Skor:</span>
                                    <span className="font-mono font-bold text-blue-700">
                                      {ev.certiport_score !== null && ev.certiport_score !== undefined
                                        ? ev.certiport_score
                                        : (ev.certiport_row_id ? (ev.match_score ?? "—") : "—")}
                                    </span>
                                  </div>
                                  <div className="flex items-center justify-between">
                                    <span className="text-[#66736F]">Hasil:</span>
                                    <span className={`inline-block rounded px-1.5 py-0.5 text-[10px] font-semibold ${
                                      (ev.certiport_status || (ev.certiport_row_id ? "PASS" : "")).toUpperCase() === "PASS"
                                        ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
                                        : "bg-rose-50 text-rose-800 border border-rose-200"
                                    }`}>
                                      {ev.certiport_status || (ev.certiport_row_id ? "PASS" : "—")}
                                    </span>
                                  </div>
                                </div>
                              ) : (
                                <p className="text-[11px] text-[#66736F] italic">
                                  Belum ditemukan rekaman cocok di Certiport
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Review Audit History */}
              {selectedResult.review_history && selectedResult.review_history.length > 0 && (
                <div className="rounded-xl border border-[#DDE4E1] bg-[#F5F7F6]/60 p-3.5">
                  <h4 className="text-[11px] font-semibold uppercase tracking-wider text-[#66736F]">
                    Jejak Audit Keputusan Petugas ({selectedResult.review_history.length})
                  </h4>
                  <ul className="mt-2 divide-y divide-[#DDE4E1] text-xs">
                    {selectedResult.review_history.map((audit) => (
                      <li key={audit.id} className="py-2">
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-[#172321]">
                            {audit.reviewer_name || "Petugas"} · {audit.decision}
                          </span>
                          <span className="font-mono text-[11px] text-[#66736F]">
                            {new Date(audit.created_at).toLocaleString("id-ID")}
                          </span>
                        </div>
                        <p className="mt-0.5 text-[#66736F] italic">"{audit.note}"</p>
                        <p className="mt-0.5 text-[11px] text-[#66736F]">
                          Status: {audit.previous_status} → <span className="font-semibold text-[#172321]">{audit.new_status}</span>
                        </p>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Review Action Form (ADR-009) */}
              <form onSubmit={handleReviewSubmit} className="rounded-xl border border-teal-200 bg-[#ECFAF8]/40 p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold text-teal-950 uppercase tracking-wide">Keputusan Review Manual</h4>
                  <span className="rounded-full border border-teal-200 bg-white px-2 py-0.5 text-[10px] font-semibold text-teal-800">
                    ADR-009 Reviewer Guard
                  </span>
                </div>

                <div className="space-y-1">
                  <label htmlFor="review-decision" className="text-xs font-medium text-[#172321]">
                    Pilihan Keputusan:
                  </label>
                  <select
                    id="review-decision"
                    value={reviewDecision}
                    onChange={(e) => setReviewDecision(e.target.value)}
                    className="w-full rounded-lg border border-[#DDE4E1] bg-white px-3 py-1.5 text-xs text-[#172321] focus:border-[#0F766E] focus:outline-none"
                  >
                    <option value="KONFIRMASI_COCOK">KONFIRMASI COCOK (Verifikasi identitas sah [Wewenang khusus])</option>
                    <option value="TIDAK_COCOK">TIDAK COCOK (Bukan orang yang sama / tolak klaim)</option>
                    <option value="TUNDA_VERIFIKASI">TUNDA VERIFIKASI (Perlu periksa dokumen/bukti fisik)</option>
                  </select>
                </div>

                {isMcfRelevant(resolveKodeProdiFromNim(selectedResult.nim) || selectedResult.kode_prodi) && (
                  <div className="space-y-1">
                    <label htmlFor="review-target" className="text-xs font-medium text-[#172321]">
                      Target Program Sertifikasi:
                    </label>
                    <select
                      id="review-target"
                      value={reviewTarget}
                      onChange={(e) => setReviewTarget(e.target.value)}
                      className="w-full rounded-lg border border-[#DDE4E1] bg-white px-3 py-1.5 text-xs text-[#172321] focus:border-[#0F766E] focus:outline-none"
                    >
                      <option value="ALL">Semua Program (MOS & MCF)</option>
                      <option value="MOS">Hanya Sertifikasi MOS</option>
                      <option value="MCF">Hanya Sertifikasi MCF</option>
                    </select>
                  </div>
                )}

                <div className="space-y-1">
                  <label htmlFor="review-note" className="text-xs font-medium text-[#172321]">
                    Catatan Review (Wajib):
                  </label>
                  <textarea
                    id="review-note"
                    rows={2}
                    placeholder="Tulis alasan keputusan, nomor berkas, atau catatan verifikasi identitas..."
                    value={reviewNote}
                    onChange={(e) => setReviewNote(e.target.value)}
                    required
                    className="w-full rounded-lg border border-[#DDE4E1] bg-white p-2.5 text-xs text-[#172321] focus:border-[#0F766E] focus:outline-none"
                  />
                </div>

                <p className="text-[11px] leading-relaxed text-[#66736F]">
                  Kebijakan penunjukan reviewer (ADR-009): Konfirmasi manual tidak mengubah riwayat ujian gagal menjadi lulus, dan seluruh bukti asli tetap dipertahankan utuh.
                </p>

                {reviewError && (
                  <p role="alert" className="rounded-lg border border-red-200 bg-red-50 p-2 text-xs text-red-900">
                    {reviewError}
                  </p>
                )}
                {reviewSuccess && (
                  <p role="status" className="rounded-lg border border-emerald-200 bg-emerald-50 p-2 text-xs text-emerald-900">
                    {reviewSuccess}
                  </p>
                )}

                <div className="flex justify-end pt-1">
                  <button
                    type="submit"
                    disabled={submittingReview}
                    className="rounded-lg bg-[#0F766E] px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-[#0F4B46] disabled:opacity-50"
                  >
                    {submittingReview ? "Menyimpan…" : "Simpan Keputusan Review"}
                  </button>
                </div>
              </form>
            </div>

            <div className="mt-5 flex justify-end border-t border-[#DDE4E1] pt-4">
              <button
                type="button"
                onClick={() => setSelectedResult(null)}
                className="rounded-lg border border-[#DDE4E1] bg-white px-4 py-1.5 text-xs font-semibold text-[#172321] hover:bg-slate-50"
              >
                Tutup
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
