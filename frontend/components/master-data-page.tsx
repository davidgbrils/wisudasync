"use client";

import { FormEvent, useEffect, useState } from "react";
import { getJson, uploadExcel } from "@/lib/api";

type MasterType = "sitasi" | "certiport";

type Props = {
  type: MasterType;
  title: string;
};

export default function MasterDataPage({ type, title }: Props) {
  const [items, setItems] = useState<Record<string, unknown>[]>([]);
  const [total, setTotal] = useState(0);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  async function loadData() {
    try {
      const response = await getJson(`/${type}?page=1&limit=50`);
      setItems(response.data.items);
      setTotal(response.data.total);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Gagal mengambil data");
    }
  }

  useEffect(() => {
    loadData();
  }, [type]);

  async function handleUpload(event: FormEvent) {
    event.preventDefault();
    if (!file) return;

    setLoading(true);
    setMessage("");
    try {
      const response = await uploadExcel(`/${type}/import`, file);
      setMessage(`${response.message}. ${response.data.imported_rows} baris masuk.`);
      await loadData();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Upload gagal");
    } finally {
      setLoading(false);
    }
  }

  const columns =
    type === "sitasi"
      ? ["nim", "nama", "program_studi", "sertifikasi", "sub_program", "nilai", "status"]
      : ["full_name", "program_name", "certification_name", "score", "result"];

  return (
    <main className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">{title}</h1>
        <p className="text-sm text-gray-500">Total data aktif: {total}</p>
      </div>

      <form onSubmit={handleUpload} className="rounded-lg border p-4 space-y-3">
        <p className="font-medium">Upload / update data master</p>
        <input
          type="file"
          accept=".xlsx"
          onChange={(event) => setFile(event.target.files?.[0] ?? null)}
        />
        <div>
          <button
            type="submit"
            disabled={!file || loading}
            className="rounded bg-black px-4 py-2 text-white disabled:opacity-50"
          >
            {loading ? "Memproses..." : "Import Excel"}
          </button>
        </div>
        {message && <p className="text-sm">{message}</p>}
      </form>

      <div className="overflow-x-auto rounded-lg border">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              {columns.map((column) => (
                <th key={column} className="px-3 py-2 text-left font-medium">
                  {column.replaceAll("_", " ").toUpperCase()}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {items.map((item, rowIndex) => (
              <tr key={String(item.id ?? rowIndex)} className="border-t">
                {columns.map((column) => (
                  <td key={column} className="px-3 py-2 whitespace-nowrap">
                    {String(item[column] ?? "-")}
                  </td>
                ))}
              </tr>
            ))}
            {items.length === 0 && (
              <tr>
                <td colSpan={columns.length} className="p-6 text-center text-gray-500">
                  Belum ada data aktif.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </main>
  );
}
