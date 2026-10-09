import Link from "next/link";

export default function UnauthorizedPage() {
  return (
    <main className="mx-auto max-w-xl p-10">
      <h1 className="text-2xl font-semibold">Akses belum diberikan</h1>
      <p className="mt-3 text-gray-600">Akun berhasil masuk, tetapi belum terdaftar sebagai petugas aktif ITCC.</p>
      <Link className="mt-5 inline-block underline" href="/login">Kembali ke login</Link>
    </main>
  );
}
