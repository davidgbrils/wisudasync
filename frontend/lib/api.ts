const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export async function getJson(path: string) {
  const response = await fetch(`${API_URL}${path}`, { cache: "no-store" });
  const body = await response.json();
  if (!response.ok) throw new Error(body.detail ?? "Request gagal");
  return body;
}

export async function uploadExcel(path: string, file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    body: formData,
  });
  const body = await response.json();
  if (!response.ok) throw new Error(body.detail ?? "Upload gagal");
  return body;
}
