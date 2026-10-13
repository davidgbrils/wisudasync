import Link from "next/link";

import PublicNavbar from "@/components/public-navbar";

const features = [
  {
    title: "Validasi File Wisuda",
    description:
      "Periksa template, kolom wajib, dan baris kosong sebelum sinkronisasi dijalankan sehingga kesalahan format terdeteksi lebih awal.",
  },
  {
    title: "Master SITASI & Certiport",
    description:
      "Unggah dan kelola batch master yang menjadi acuan pencocokan. Batch aktif selalu ditampilkan sebagai konteks proses.",
  },
  {
    title: "Pencocokan Deterministik",
    description:
      "Wisuda ke SITASI memakai NIM exact sebagai string, sedangkan Certiport memakai nama ternormalisasi tanpa mengarang identitas.",
  },
  {
    title: "Review oleh Petugas",
    description:
      "Kandidat ambigu atau skor fuzzy tidak pernah otomatis VALID. Petugas memutuskan cocok, tidak cocok, atau tunda.",
  },
  {
    title: "Jejak Audit Terpisah",
    description:
      "Keputusan review, alasan, dan waktu dicatat. Status hasil MOS dan MCF disimpan terpisah tanpa saling menimpa.",
  },
  {
    title: "Ekspor Excel",
    description:
      "Unduh draf atau hasil final sesuai mapping kolom yang telah disahkan. Data lama tidak ditimpa tanpa persetujuan.",
  },
];

const steps = [
  { step: "01", title: "Unggah Master", description: "Impor data acuan SITASI dan Certiport, lalu tetapkan batch aktif." },
  { step: "02", title: "Validasi Wisuda", description: "Unggah data wisuda dan pastikan format serta kolomnya sesuai template." },
  { step: "03", title: "Proses & Review", description: "Jalankan sinkronisasi, lalu periksa hasil yang berstatus perlu verifikasi." },
  { step: "04", title: "Unduh Hasil", description: "Ekspor hasil ke Excel berdasarkan aturan keluaran yang telah disetujui." },
];

const statuses = [
  { label: "VALID", className: "bg-emerald-50 text-emerald-800 border-emerald-200", note: "Cocok dan memenuhi syarat." },
  { label: "PERLU_VERIFIKASI", className: "bg-amber-50 text-amber-800 border-amber-200", note: "Kandidat ambigu, butuh keputusan petugas." },
  { label: "TIDAK_LULUS", className: "bg-red-50 text-red-800 border-red-200", note: "Tercocok namun tidak lulus syarat." },
  { label: "PENDING", className: "bg-sky-50 text-sky-800 border-sky-200", note: "Menunggu diproses atau ditinjau." },
  { label: "DATA_TIDAK_DITEMUKAN", className: "bg-slate-100 text-slate-700 border-slate-200", note: "Tidak ada data acuan yang cocok." },
];

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white">
      <PublicNavbar />

      <main>
        <section className="border-b border-slate-200 bg-gradient-to-b from-slate-50 to-white">
          <div className="mx-auto grid max-w-6xl gap-12 px-4 py-16 sm:px-6 lg:grid-cols-2 lg:items-center lg:py-24">
            <div>
              <span className="inline-flex items-center gap-2 rounded-full border border-teal-200 bg-teal-50 px-3 py-1 text-xs font-semibold text-teal-800">
                Internal ITCC · ITPLN
              </span>
              <h1 className="mt-5 text-4xl font-semibold leading-tight tracking-tight text-slate-900 sm:text-5xl">
                Sinkronisasi data sertifikasi wisuda, rapi dan dapat diaudit.
              </h1>
              <p className="mt-5 max-w-xl text-base leading-7 text-slate-600">
                ITCC Wisuda Sync menyatukan data wisuda, SITASI, dan Certiport dalam satu alur: unggah master,
                validasi berkas, proses pencocokan, review manual, lalu ekspor. Setiap keputusan tercatat.
              </p>
              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <Link
                  href="/login"
                  className="inline-flex min-h-11 items-center justify-center rounded-md bg-teal-800 px-6 text-sm font-medium text-white transition hover:bg-teal-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700"
                >
                  Masuk ke Sistem
                </Link>
                <Link
                  href="/login?mode=register"
                  className="inline-flex min-h-11 items-center justify-center rounded-md border border-slate-300 px-6 text-sm font-medium text-slate-700 transition hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700"
                >
                  Daftar Akun Petugas
                </Link>
              </div>
              <p className="mt-4 text-xs text-slate-500">
                Akses terbatas untuk petugas ITCC. Akun diverifikasi sebelum dapat mengimpor data.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex items-center justify-between border-b border-slate-200 pb-4">
                <p className="text-sm font-semibold text-slate-900">Ringkasan Proses</p>
                <span className="rounded bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">contoh tampilan</span>
              </div>
              <dl className="mt-4 grid grid-cols-2 gap-4">
                <div className="rounded-lg border border-slate-200 p-4">
                  <dt className="text-xs font-medium text-slate-500">Total baris</dt>
                  <dd className="mt-1 text-2xl font-semibold text-slate-900">424</dd>
                </div>
                <div className="rounded-lg border border-slate-200 p-4">
                  <dt className="text-xs font-medium text-slate-500">Perlu verifikasi</dt>
                  <dd className="mt-1 text-2xl font-semibold text-amber-700">37</dd>
                </div>
                <div className="rounded-lg border border-slate-200 p-4">
                  <dt className="text-xs font-medium text-slate-500">Tidak ditemukan</dt>
                  <dd className="mt-1 text-2xl font-semibold text-slate-900">12</dd>
                </div>
                <div className="rounded-lg border border-slate-200 p-4">
                  <dt className="text-xs font-medium text-slate-500">Selesai diproses</dt>
                  <dd className="mt-1 text-2xl font-semibold text-emerald-700">375</dd>
                </div>
              </dl>
              <p className="mt-4 text-xs text-slate-500">Angka di atas hanya ilustrasi, bukan hasil sinkronisasi yang sudah diuji.</p>
            </div>

            <div className="overflow-hidden rounded-2xl border border-slate-200 shadow-sm lg:col-span-2">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src="/brand/hero-banner.png"
                alt="ITCC Wisuda Sync: menyatukan data wisuda, SITASI, dan Certiport secara akurat, aman, dan efisien"
                width={1053}
                height={225}
                className="w-full"
              />
            </div>
          </div>
        </section>

        <section id="fitur" className="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:py-24">
          <div className="max-w-2xl">
            <h2 className="text-3xl font-semibold tracking-tight text-slate-900">Fitur utama</h2>
            <p className="mt-3 text-base leading-7 text-slate-600">
              Dibangun mengikuti aturan bisnis ITCC: pencocokan deterministik lebih dulu, keputusan ambigu diserahkan ke manusia.
            </p>
          </div>
          <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((feature) => (
              <article key={feature.title} className="rounded-xl border border-slate-200 bg-white p-6 transition hover:border-teal-300 hover:shadow-sm">
                <span aria-hidden="true" className="grid h-9 w-9 place-items-center rounded-lg bg-teal-50 text-sm font-bold text-teal-800">
                  {feature.title.charAt(0)}
                </span>
                <h3 className="mt-4 text-base font-semibold text-slate-900">{feature.title}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-600">{feature.description}</p>
              </article>
            ))}
          </div>
        </section>

        <section id="cara-kerja" className="border-y border-slate-200 bg-slate-50">
          <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:py-24">
            <div className="max-w-2xl">
              <h2 className="text-3xl font-semibold tracking-tight text-slate-900">Cara kerja</h2>
              <p className="mt-3 text-base leading-7 text-slate-600">Empat langkah dari berkas mentah hingga hasil yang dapat diunduh.</p>
            </div>
            <ol className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
              {steps.map((item) => (
                <li key={item.step} className="rounded-xl border border-slate-200 bg-white p-6">
                  <span className="text-sm font-bold text-teal-800">{item.step}</span>
                  <h3 className="mt-3 text-base font-semibold text-slate-900">{item.title}</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-600">{item.description}</p>
                </li>
              ))}
            </ol>
          </div>
        </section>

        <section id="status" className="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:py-24">
          <div className="max-w-2xl">
            <h2 className="text-3xl font-semibold tracking-tight text-slate-900">Status hasil</h2>
            <p className="mt-3 text-base leading-7 text-slate-600">
              Setiap hasil selalu memakai teks status, bukan hanya warna, agar tetap jelas dan mudah diverifikasi.
            </p>
          </div>
          <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {statuses.map((status) => (
              <div key={status.label} className="flex items-start gap-3 rounded-xl border border-slate-200 bg-white p-5">
                <span className={`mt-0.5 shrink-0 rounded-full border px-3 py-1 text-xs font-semibold ${status.className}`}>
                  {status.label}
                </span>
                <p className="text-sm leading-6 text-slate-600">{status.note}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="border-t border-slate-200 bg-teal-900">
          <div className="mx-auto flex max-w-6xl flex-col items-start gap-6 px-4 py-14 sm:px-6 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h2 className="text-2xl font-semibold text-white">Siap memulai sinkronisasi?</h2>
              <p className="mt-2 text-sm leading-6 text-teal-100">Masuk dengan akun petugas atau daftarkan akun baru untuk diverifikasi.</p>
            </div>
            <div className="flex w-full flex-col gap-3 sm:w-auto sm:flex-row">
              <Link
                href="/login"
                className="inline-flex min-h-11 items-center justify-center rounded-md bg-white px-6 text-sm font-medium text-teal-900 transition hover:bg-teal-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
              >
                Masuk
              </Link>
              <Link
                href="/login?mode=register"
                className="inline-flex min-h-11 items-center justify-center rounded-md border border-teal-300 px-6 text-sm font-medium text-white transition hover:bg-teal-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
              >
                Daftar
              </Link>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-col gap-2 px-4 py-8 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <p>ITCC Wisuda Sync · Aplikasi internal pengelolaan data sertifikasi.</p>
          <p>Akses terbatas untuk petugas ITCC.</p>
        </div>
      </footer>
    </div>
  );
}
