import { createSupabaseBrowserClient } from "@/lib/supabase/client";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export type ActiveBatch = {
  id: string;
  total_rows: number;
  imported_rows: number;
  status: string;
  completed_at: string | null;
};

export type MasterRow = Record<string, string | number | null> & { id?: string | number };
export type MasterListResponse = {
  success: boolean;
  data: { items: MasterRow[]; total: number; page: number; limit: number };
};
export type BatchResponse = { success: boolean; data: ActiveBatch | null };
export type WisudaValidationIssue = {
  source_row: number | null;
  field: string;
  code: string;
  message: string;
};
export type WisudaValidation = {
  success: boolean;
  data: {
    is_valid: boolean;
    sheet_name: string;
    columns: string[];
    layout_matches_template: boolean;
    missing_columns: string[];
    student_count: number;
    empty_row_count: number;
    empty_rows: number[];
    empty_rows_truncated: boolean;
    issues: WisudaValidationIssue[];
    issues_truncated: boolean;
    active_masters: { sitasi: ActiveBatch | null; certiport: ActiveBatch | null };
  };
};

export type SyncSession = {
  id: string;
  session_id?: string;
  file_name: string;
  sitasi_import_id: string;
  certiport_import_id: string;
  total_rows: number;
  total_valid: number;
  total_review: number;
  total_not_found: number;
  status: "UPLOADED" | "PROCESSING" | "COMPLETED" | "FAILED";
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
};

export type SyncResultItem = {
  id: string;
  sync_session_id: string;
  source_row: number;
  nim: string;
  nama_wisuda: string;
  kode_prodi: string | null;
  program_studi: string | null;
  nama_sitasi: string | null;
  name_match_type: string | null;
  mos_status: string | null;
  mcf_status: string | null;
  validation_status: string;
  needs_review: boolean;
  review_note: string | null;
  mos_programs?: Record<string, unknown> | null;
  mcf_programs?: Record<string, unknown> | null;
};

export type SyncEvidenceItem = {
  id: string;
  result_id: string;
  category: string | null;
  exam: string | null;
  sitasi_row_id: number | null;
  certiport_row_id: number | null;
  match_method: string | null;
  match_score: number | null;
  evidence_status: string | null;
  reason: string | null;
  created_at: string;
  sitasi_name?: string | null;
  sitasi_score?: number | null;
  sitasi_status?: string | null;
  certiport_name?: string | null;
  certiport_score?: number | null;
  certiport_status?: string | null;
};

export type ReviewAuditItem = {
  id: string;
  result_id: string;
  reviewed_by: string | null;
  reviewer_name: string | null;
  decision: string;
  note: string;
  previous_status: string;
  new_status: string;
  created_at: string;
};

export type SyncResultDetail = SyncResultItem & {
  evidence: SyncEvidenceItem[];
  review_history?: ReviewAuditItem[];
};

export type SyncListResponse = {
  success: boolean;
  data: {
    items: SyncSession[];
    total: number;
    page: number;
    limit: number;
  };
};

export type SyncResultsResponse = {
  success: boolean;
  data: {
    items: SyncResultItem[];
    total: number;
    page: number;
    limit: number;
  };
};

async function authorizedHeaders(): Promise<HeadersInit> {
  const { data: { session }, error } = await createSupabaseBrowserClient().auth.getSession();
  if (error || !session?.access_token) throw new Error("Sesi login berakhir. Silakan masuk kembali.");
  return { Authorization: `Bearer ${session.access_token}` };
}

function safeError(status: number, fallback: string, isUpload = false): string {
  if (status === 401) return "Sesi login berakhir. Silakan masuk kembali.";
  if (status === 403) return "Akun ini tidak memiliki akses petugas.";
  if (isUpload && status === 413) return "Ukuran file melewati batas 10 MiB.";
  if (isUpload && (status === 400 || status === 422)) return "File belum sesuai format atau template yang diwajibkan.";
  return fallback;
}

export async function getJson<T = Record<string, unknown>>(path: string): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      headers: await authorizedHeaders(),
      cache: "no-store",
    });
  } catch (error) {
    if (error instanceof Error && error.message.startsWith("Sesi login")) throw error;
    throw new Error("Layanan data belum dapat dijangkau. Periksa koneksi backend.");
  }
  if (!response.ok) throw new Error(safeError(response.status, "Data belum dapat dimuat. Coba lagi."));
  try {
    return await response.json() as T;
  } catch {
    throw new Error("Respons data tidak dapat dibaca. Coba lagi.");
  }
}

export async function uploadExcel<T = unknown>(path: string, file: File): Promise<T> {
  const formData = new FormData();
  formData.append("file", file);

  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      method: "POST",
      headers: await authorizedHeaders(),
      body: formData,
    });
  } catch (error) {
    if (error instanceof Error && error.message.startsWith("Sesi login")) throw error;
    throw new Error("Layanan import belum dapat dijangkau. Periksa koneksi backend.");
  }
  if (!response.ok) throw new Error(safeError(response.status, "Import gagal diproses. Coba lagi.", true));
  return await response.json() as T;
}

export async function startSync(file: File): Promise<{ success: boolean; data: SyncSession }> {
  return uploadExcel<{ success: boolean; data: SyncSession }>("/sync", file);
}

export async function getSyncSessions(page = 1, limit = 20): Promise<SyncListResponse> {
  return getJson<SyncListResponse>(`/sync?page=${page}&limit=${limit}`);
}

export async function getSyncSession(id: string): Promise<{ success: boolean; data: SyncSession }> {
  return getJson<{ success: boolean; data: SyncSession }>(`/sync/${id}`);
}

export async function getSyncResults(
  sessionId: string,
  params?: { page?: number; limit?: number; status?: string; search?: string; needs_review?: boolean }
): Promise<SyncResultsResponse> {
  const query = new URLSearchParams();
  if (params?.page) query.set("page", String(params.page));
  if (params?.limit) query.set("limit", String(params.limit));
  if (params?.status) query.set("status", params.status);
  if (params?.search) query.set("search", params.search);
  if (params?.needs_review !== undefined) query.set("needs_review", String(params.needs_review));
  const qs = query.toString();
  return getJson<SyncResultsResponse>(`/sync/${sessionId}/results${qs ? `?${qs}` : ""}`);
}

export async function getSyncResultDetail(sessionId: string, resultId: string): Promise<{ success: boolean; data: SyncResultDetail }> {
  return getJson<{ success: boolean; data: SyncResultDetail }>(`/sync/${sessionId}/results/${resultId}`);
}

export async function submitReviewResult(
  sessionId: string,
  resultId: string,
  decision: string,
  note: string
): Promise<{ success: boolean; data: Record<string, unknown> }> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}/sync/${sessionId}/results/${resultId}/review`, {
      method: "PATCH",
      headers: {
        ...(await authorizedHeaders()),
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ decision, note }),
    });
  } catch (error) {
    if (error instanceof Error && error.message.startsWith("Sesi login")) throw error;
    throw new Error("Layanan review belum dapat dijangkau.");
  }
  if (!response.ok) {
    const errorBody = await response.json().catch(() => null) as { detail?: string } | null;
    const detail = errorBody?.detail || safeError(response.status, "Gagal menyimpan keputusan review.");
    throw new Error(detail);
  }
  return await response.json();
}

export async function downloadSyncExport(sessionId: string, mode: "draft" | "final" = "draft"): Promise<Blob> {
  const response = await fetch(`${API_URL}/sync/${sessionId}/export?mode=${mode}`, {
    headers: await authorizedHeaders(),
  });
  if (!response.ok) {
    const errorBody = await response.json().catch(() => null) as { detail?: string } | null;
    const detail = errorBody?.detail || safeError(response.status, "Gagal mengunduh berkas ekspor.");
    throw new Error(detail);
  }
  return await response.blob();
}

export type RegisterStaffResponse = {
  success: boolean;
  message: string;
  data: {
    id: string;
    email: string;
    display_name: string;
    role: string;
  };
};

export async function registerStaff(payload: {
  email: string;
  password: string;
  display_name: string;
}): Promise<RegisterStaffResponse> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new Error("Layanan pendaftaran akun belum dapat dijangkau.");
  }
  if (!response.ok) {
    const errorBody = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(errorBody?.detail || "Gagal melakukan pendaftaran akun petugas.");
  }
  return await response.json();
}
