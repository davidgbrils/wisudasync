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

  const [reviewDecision, setReviewDecision] = useState<string>("TUNDA_VERIFIKASI");
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
    setReviewDecision("TUNDA_VERIFIKASI");
    setReviewNote("");
    setReviewError("");
    setReviewSuccess("");
    try {
      const detail = await getSyncResultDetail(sessionId, item.id);
      setSelectedResult(detail.data);
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
        reviewNote.trim()
      );
      setReviewSuccess("Keputusan review berhasil disimpan.");

      // Refresh detail data
      const updatedDetail = await getSyncResultDetail(sessionId, selectedResult.id);
      setSelectedResult(updatedDetail.data);

      // Update parent list state
      setResults((prev) =>
        prev.map((r) =>
          r.id === selectedResult.id
            ? {
                ...r,
                validation_status: (res.data.new_status as string) || r.validation_status,
                review_note: `[${reviewDecision}] ${reviewNote.trim()}`,
                needs_review: reviewDecision !== "KONFIRMASI_COCOK",
              }
            : r
        )
      );

      // Refresh session statistics
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

  async function handleDownloadDraft() {
    setDownloading(true);
    setExportError("");
    try {
      const blob = await downloadSyncExport(sessionId, "draft");
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `wisuda_sync_draft_${session?.file_name || sessionId.slice(0, 8)}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (cause) {
      setExportError(cause instanceof Error ? cause.message : "Gagal mengunduh berkas pratinjau.");
    } finally {
      setDownloading(false);
    }
  }

  const totalPages = Math.ceil(total / limit) || 1;

  return (
    <section className="mx-auto max-w-7xl space-y-6">
      <header className="space-y-3">
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <Link href="/sinkronisasi" className="hover:text-teal-800">
            ← Validasi Wisuda
          </Link>
          <span>/</span>
          <Link href="/riwayat" className="hover:text-teal-800">
            Riwayat Sinkronisasi
          </Link>
          <span>/</span>
          <span className="text-slate-700">Hasil Sesi</span>
        </div>

        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-slate-950 sm:text-3xl">
              Hasil Sinkronisasi
            </h1>
            <p className="mt-1 text-sm text-slate-600">
              File: <span className="font-semibold text-slate-900">{session?.file_name || "..."}</span>
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
              {session.status}
            </span>
          )}
        </div>

        {session && (
          <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500">
            <span>
              Batch SITASI: <code className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-slate-800">{session.sitasi_import_id.slice(0, 8)}</code>
            </span>
            <span>
              Batch Certiport: <code className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-slate-800">{session.certiport_import_id.slice(0, 8)}</code>
            </span>
          </div>
        )}
      </header>

      {/* KPI Cards */}
      {session && (
        <dl className="grid gap-3 sm:grid-cols-4">
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">Total Mahasiswa</dt>
            <dd className="mt-1 text-2xl font-semibold text-slate-950">{session.total_rows.toLocaleString("id-ID")}</dd>
          </div>
          <div className="rounded-xl border border-emerald-200 bg-emerald-50/50 p-4 shadow-sm">
            <dt className="text-xs font-semibold uppercase tracking-wide text-emerald-800">Valid</dt>
            <dd className="mt-1 text-2xl font-semibold text-emerald-900">{session.total_valid.toLocaleString("id-ID")}</dd>
          </div>
          <div className="rounded-xl border border-amber-200 bg-amber-50/50 p-4 shadow-sm">
            <dt className="text-xs font-semibold uppercase tracking-wide text-amber-900">Perlu Verifikasi</dt>
            <dd className="mt-1 text-2xl font-semibold text-amber-950">{session.total_review.toLocaleString("id-ID")}</dd>
          </div>
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 shadow-sm">
            <dt className="text-xs font-semibold uppercase tracking-wide text-slate-600">Tidak Ditemukan</dt>
            <dd className="mt-1 text-2xl font-semibold text-slate-900">{session.total_not_found.toLocaleString("id-ID")}</dd>
          </div>
        </dl>
      )}

      {/* Export Gate Action Bar */}
      <div className="flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="text-sm font-semibold text-slate-900">Ekspor Berkas Wisuda</h3>
          <p className="text-xs text-slate-500">
            Pratinjau DRAFT tersedia untuk verifikasi internal. Ekspor final resmi dikunci sampai pengesahan kebijakan ITCC.
          </p>
          {exportError && (
            <p role="alert" className="mt-1 text-xs text-red-700">{exportError}</p>
          )}
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={handleDownloadDraft}
            disabled={downloading}
            className="rounded-lg bg-teal-800 px-4 py-2 text-xs font-semibold text-white hover:bg-teal-900 disabled:opacity-50"
          >
            {downloading ? "Mengunduh…" : "Unduh Pratinjau Excel (DRAFT)"}
          </button>
          <div className="relative group">
            <button
              type="button"
              disabled
              title="Ekspor final diblokir: Menunggu pengesahan keputusan bisnis ITCC (ADR-003, ADR-005, ADR-006, ADR-010, ADR-011). Lihat docs/20_OUTPUT_MAPPING_APPROVAL.md"
              className="rounded-lg border border-slate-200 bg-slate-100 px-4 py-2 text-xs font-semibold text-slate-400 cursor-not-allowed"
            >
              Unduh Excel Final Resmi (Terkunci)
            </button>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:flex-row sm:items-center sm:justify-between">
        <form onSubmit={handleSearchSubmit} className="flex flex-1 items-center gap-2">
          <input
            type="search"
            placeholder="Cari NIM atau Nama..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full max-w-sm rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-teal-700 focus:outline-none focus:ring-1 focus:ring-teal-700"
          />
          <button
            type="submit"
            className="rounded-lg bg-teal-800 px-4 py-2 text-sm font-semibold text-white hover:bg-teal-900"
          >
            Cari
          </button>
          {activeSearch && (
            <button
              type="button"
              onClick={() => { setSearchQuery(""); setActiveSearch(""); setPage(1); }}
              className="text-xs text-slate-500 hover:text-slate-800"
            >
              Reset
            </button>
          )}
        </form>

        <div className="flex flex-wrap items-center gap-4">
          <label className="flex items-center gap-2 text-sm text-slate-700">
            <input
              type="checkbox"
              checked={needsReviewOnly}
              onChange={(e) => { setNeedsReviewOnly(e.target.checked); setPage(1); }}
              className="h-4 w-4 rounded border-slate-300 text-teal-700 focus:ring-teal-700"
            />
            Hanya Perlu Review
          </label>

          <div className="flex items-center gap-2">
            <label htmlFor="filter-status" className="text-sm text-slate-600">Status:</label>
            <select
              id="filter-status"
              value={statusFilter}
              onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-teal-700 focus:outline-none focus:ring-1 focus:ring-teal-700"
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
        <p role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-900">
          {error}
        </p>
      )}

      {/* Table */}
      <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
        <table className="w-full text-left text-sm text-slate-800">
          <thead className="border-b border-slate-200 bg-slate-50 text-xs font-semibold uppercase text-slate-600">
            <tr>
              <th scope="col" className="px-4 py-3">Baris</th>
              <th scope="col" className="px-4 py-3">NIM</th>
              <th scope="col" className="px-4 py-3">Nama Mahasiswa</th>
              <th scope="col" className="px-4 py-3">MOS</th>
              <th scope="col" className="px-4 py-3">MCF</th>
              <th scope="col" className="px-4 py-3">Status Hasil</th>
              <th scope="col" className="px-4 py-3">Catatan / Flag</th>
              <th scope="col" className="px-4 py-3 text-right">Aksi</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading ? (
              <tr>
                <td colSpan={8} className="p-8 text-center text-slate-500">
                  Memuat data hasil sinkronisasi...
                </td>
              </tr>
            ) : results.length === 0 ? (
              <tr>
                <td colSpan={8} className="p-8 text-center text-slate-500">
                  Tidak ada baris yang cocok dengan filter.
                </td>
              </tr>
            ) : (
              results.map((row) => (
                <tr key={row.id} className="hover:bg-slate-50/80">
                  <td className="px-4 py-3 font-mono text-xs text-slate-500">{row.source_row}</td>
                  <td className="px-4 py-3 font-mono font-medium text-slate-900">{row.nim}</td>
                  <td className="px-4 py-3 font-medium text-slate-900">
                    <div>{row.nama_wisuda}</div>
                    {row.nama_sitasi && row.nama_sitasi !== row.nama_wisuda && (
                      <div className="text-xs text-slate-500">SITASI: {row.nama_sitasi}</div>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-block rounded border px-2 py-0.5 text-xs font-semibold ${statusBadgeClass(row.mos_status)}`}>
                      {formatStatusLabel(row.mos_status)}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-block rounded border px-2 py-0.5 text-xs font-semibold ${statusBadgeClass(row.mcf_status)}`}>
                      {formatStatusLabel(row.mcf_status)}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-block rounded border px-2.5 py-1 text-xs font-semibold ${statusBadgeClass(row.validation_status)}`}>
                      {formatStatusLabel(row.validation_status)}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-600 max-w-xs truncate" title={row.review_note || ""}>
                    {row.review_note || "—"}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      type="button"
                      onClick={() => openDetailModal(row)}
                      className="rounded bg-teal-50 px-3 py-1 text-xs font-semibold text-teal-800 hover:bg-teal-100"
                    >
                      Detail Bukti
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex flex-col items-center justify-between gap-3 text-sm text-slate-600 sm:flex-row">
        <p>
          Menampilkan baris {(page - 1) * limit + 1}–{Math.min(page * limit, total)} dari {total.toLocaleString("id-ID")}
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

      {/* Evidence Detail Modal */}
      {selectedResult && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="modal-title"
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4"
        >
          <div className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-xl bg-white p-6 shadow-xl">
            <div className="flex items-start justify-between border-b border-slate-200 pb-4">
              <div>
                <h3 id="modal-title" className="text-lg font-semibold text-slate-950">
                  Rincian Bukti Sinkronisasi
                </h3>
                <p className="mt-0.5 text-xs text-slate-500">
                  Baris {selectedResult.source_row} · NIM {selectedResult.nim} · {selectedResult.nama_wisuda}
                </p>
              </div>
              <button
                type="button"
                onClick={() => setSelectedResult(null)}
                className="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700"
              >
                ✕
              </button>
            </div>

            <div className="mt-4 space-y-4 text-sm">
              <div className="grid grid-cols-2 gap-3 rounded-lg bg-slate-50 p-3 text-xs">
                <div>
                  <span className="font-semibold text-slate-600">Pencocokan Nama:</span>{" "}
                  <span className="font-mono text-slate-900">{selectedResult.name_match_type || "—"}</span>
                </div>
                <div>
                  <span className="font-semibold text-slate-600">Status Keseluruhan:</span>{" "}
                  <span className={`rounded border px-2 py-0.5 font-semibold ${statusBadgeClass(selectedResult.validation_status)}`}>
                    {selectedResult.validation_status}
                  </span>
                </div>
                {selectedResult.nama_sitasi && (
                  <div className="col-span-2">
                    <span className="font-semibold text-slate-600">Nama di SITASI:</span>{" "}
                    <span className="text-slate-900">{selectedResult.nama_sitasi}</span>
                  </div>
                )}
                {selectedResult.review_note && (
                  <div className="col-span-2">
                    <span className="font-semibold text-amber-900">Catatan Review:</span>{" "}
                    <span className="text-amber-950">{selectedResult.review_note}</span>
                  </div>
                )}
              </div>

              <div>
                <h4 className="font-semibold text-slate-900">Bukti Verifikasi Silang per Ujian</h4>
                {loadingDetail ? (
                  <p className="mt-2 text-xs text-slate-500">Memuat rincian bukti...</p>
                ) : !selectedResult.evidence || selectedResult.evidence.length === 0 ? (
                  <p className="mt-2 text-xs text-slate-500">Tidak ada record bukti terdaftar.</p>
                ) : (
                  <div className="mt-2 space-y-3">
                    {selectedResult.evidence.map((ev: SyncEvidenceItem, idx: number) => (
                      <div
                        key={ev.id || idx}
                        className="rounded-lg border border-slate-200 bg-white p-3 text-xs shadow-sm"
                      >
                        <div className="flex items-center justify-between font-semibold">
                          <span className="text-slate-900">
                            {ev.category} · {ev.exam}
                          </span>
                          <span
                            className={`rounded border px-2 py-0.5 text-[11px] ${statusBadgeClass(ev.evidence_status)}`}
                          >
                            {ev.evidence_status}
                          </span>
                        </div>
                        <p className="mt-1 text-slate-600">{ev.reason}</p>
                        <div className="mt-2 flex flex-wrap gap-4 text-slate-500">
                          {ev.sitasi_row_id && <span>Baris SITASI #{ev.sitasi_row_id}</span>}
                          {ev.certiport_row_id && <span>Baris Certiport #{ev.certiport_row_id}</span>}
                          {ev.match_score !== null && <span>Skor Certiport: {ev.match_score}</span>}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Review Audit History */}
              {selectedResult.review_history && selectedResult.review_history.length > 0 && (
                <div className="rounded-lg border border-slate-200 bg-slate-50/50 p-3">
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-600">
                    Jejak Audit Keputusan Review ({selectedResult.review_history.length})
                  </h4>
                  <ul className="mt-2 divide-y divide-slate-200 text-xs">
                    {selectedResult.review_history.map((audit) => (
                      <li key={audit.id} className="py-2">
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-slate-800">
                            {audit.reviewer_name || "Petugas"} · {audit.decision}
                          </span>
                          <span className="text-slate-400">
                            {new Date(audit.created_at).toLocaleString("id-ID")}
                          </span>
                        </div>
                        <p className="mt-0.5 text-slate-600 italic">"{audit.note}"</p>
                        <p className="mt-0.5 text-[11px] text-slate-500">
                          Status: {audit.previous_status} → <span className="font-semibold">{audit.new_status}</span>
                        </p>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Review Action Form */}
              <form onSubmit={handleReviewSubmit} className="rounded-lg border border-teal-200 bg-teal-50/40 p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-semibold text-teal-950">Keputusan Review Manual</h4>
                  <span className="rounded bg-teal-100/80 px-2 py-0.5 text-[11px] font-medium text-teal-900">
                    ADR-009 Reviewer Guard
                  </span>
                </div>

                <div className="space-y-1.5">
                  <label htmlFor="review-decision" className="text-xs font-medium text-slate-700">
                    Pilihan Keputusan:
                  </label>
                  <select
                    id="review-decision"
                    value={reviewDecision}
                    onChange={(e) => setReviewDecision(e.target.value)}
                    className="w-full rounded-md border border-slate-300 bg-white px-3 py-1.5 text-xs text-slate-900 focus:border-teal-700 focus:outline-none"
                  >
                    <option value="TUNDA_VERIFIKASI">TUNDA VERIFIKASI (Perlu periksa dokumen/bukti fisik)</option>
                    <option value="TIDAK_COCOK">TIDAK COCOK (Bukan orang yang sama / tolak klaim)</option>
                    <option value="KONFIRMASI_COCOK">KONFIRMASI COCOK (Verifikasi identitas sah [Wewenang khusus])</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label htmlFor="review-note" className="text-xs font-medium text-slate-700">
                    Catatan Review (Wajib):
                  </label>
                  <textarea
                    id="review-note"
                    rows={2}
                    placeholder="Tulis alasan keputusan, nomor berkas, atau catatan verifikasi identitas..."
                    value={reviewNote}
                    onChange={(e) => setReviewNote(e.target.value)}
                    required
                    className="w-full rounded-md border border-slate-300 bg-white p-2 text-xs text-slate-900 focus:border-teal-700 focus:outline-none"
                  />
                </div>

                <p className="text-[11px] leading-relaxed text-slate-500">
                  Kebijakan penunjukan reviewer (ADR-009) saat ini berstatus terbuka. Konfirmasi identitas tidak mengubah riwayat attempt gagal menjadi lulus, dan bukti asli tetap disimpan utuh.
                </p>

                {reviewError && (
                  <p role="alert" className="rounded border border-red-200 bg-red-50 p-2 text-xs text-red-900">
                    {reviewError}
                  </p>
                )}
                {reviewSuccess && (
                  <p role="status" className="rounded border border-emerald-200 bg-emerald-50 p-2 text-xs text-emerald-900">
                    {reviewSuccess}
                  </p>
                )}

                <div className="flex justify-end pt-1">
                  <button
                    type="submit"
                    disabled={submittingReview}
                    className="rounded-lg bg-teal-800 px-4 py-2 text-xs font-semibold text-white hover:bg-teal-900 disabled:opacity-50"
                  >
                    {submittingReview ? "Menyimpan…" : "Simpan Keputusan Review"}
                  </button>
                </div>
              </form>
            </div>

            <div className="mt-6 flex justify-end border-t border-slate-200 pt-4">
              <button
                type="button"
                onClick={() => setSelectedResult(null)}
                className="rounded-lg bg-slate-100 px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-200"
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
