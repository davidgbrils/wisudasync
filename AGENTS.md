# Instruksi AI Coding Agent Proyek ITCC Wisuda Sync

File ini adalah sumber instruksi agent utama untuk seluruh repository. Baca dan ikuti sebelum mengerjakan task.

## 1. Langkah awal setiap sesi

1. Baca `AGENTS.md`, `docs/14_DECISIONS.md`, `docs/18_CHANGELOG.md`, dan `docs/19_AI_PROGRESS.md` jika tersedia.
2. Periksa skill di `.agents/skills`, lalu baca seluruh `SKILL.md` untuk setiap skill yang relevan.
3. Periksa struktur repository, implementasi, dan status Git aktual. Dokumentasi bukan bukti bahwa fitur sudah tersedia.
4. Baca hanya dokumen tahap dan file kode yang relevan. Jangan dump seluruh repository berulang kali.
5. Jika sumber wajib tidak ada, laporkan file yang hilang dan jangan menebak isinya.

## 2. Sumber acuan berurutan

Gunakan urutan berikut saat sumbernya relevan dengan task:

1. `AGENTS.md` untuk aturan agent.
2. `docs/02_PRD.md` dan `docs/03_SRS.md` untuk fitur dan kebutuhan.
3. `docs/04_ARCHITECTURE.md` dan `docs/07_DATABASE_DESIGN.md` untuk arsitektur dan database.
4. `docs/05_DATA_DICTIONARY.md` dan `docs/06_BUSINESS_RULES.md` untuk data dan aturan bisnis.
5. `docs/08_API_CONTRACT.md` dan `docs/09_UI_UX_SPEC.md` untuk kontrak API dan UI/UX.
6. `docs/10_TEST_PLAN.md` dan `docs/11_SECURITY_PRIVACY.md` untuk pengujian dan keamanan.
7. `docs/14_DECISIONS.md`, `docs/15_ACCEPTANCE.md`, `docs/17_OPERATIONS.md`, dan `docs/18_CHANGELOG.md` untuk keputusan, penerimaan, operasi, dan riwayat perubahan.

Data asli wisuda, SITASI, dan Certiport hanya boleh digunakan di lingkungan berizin. Tes otomatis wajib menggunakan fixture anonim.

## 3. Peran dan stack

Bertindak sebagai pendamping pengembangan project magang mahasiswa Teknik Informatika. Buat solusi yang sederhana, dapat dijelaskan, diuji, dan dipelihara mahasiswa. Gunakan Bahasa Indonesia untuk komentar penting, dokumentasi, dan penjelasan. Gunakan nama fungsi dan variabel Python/TypeScript yang konsisten dan jelas.

- Frontend: Next.js App Router, TypeScript, dan Tailwind CSS.
- Backend: Python dan FastAPI.
- Pemrosesan data: Pandas/OpenPyXL. RapidFuzz hanya boleh menyarankan kandidat.
- Database, Auth, dan private Storage: Supabase PostgreSQL/Auth.
- Alur data mahasiswa: browser ke FastAPI ke Supabase. Secret dan service-role key hanya boleh berada di server.

Ketentuan arsitektur ini tidak boleh diubah diam-diam. Catat usulan perubahan sebagai keputusan terbuka sebelum implementasi.

## 4. Aturan data dan pencocokan

1. Lanjutkan kode Phase 4. Jangan membangun ulang repository tanpa alasan teknis yang jelas.
2. Wisuda ke SITASI memakai exact NIM sebagai string. Nama hanya pembanding sekunder. Periksa seluruh attempt; jangan menganggap satu NIM hanya mempunyai satu ujian dan jangan memakai `.first()` sebagai hasil akhir.
3. Certiport tidak mempunyai NIM. Untuk SITASI ke Certiport, periksa nama ternormalisasi, keunikan kandidat, program, sub-ujian, dan hasil.
4. Kandidat fuzzy atau ambigu tidak pernah otomatis `VALID`. Tampilkan untuk review manusia.
5. Status hasil yang diizinkan: `VALID`, `PERLU_VERIFIKASI`, `TIDAK_LULUS`, `PENDING`, dan `DATA_TIDAK_DITEMUKAN`.
6. Simpan status dan bukti MOS serta MCF secara terpisah.
7. Mapping final kolom `Sertifikasi MOS`, `Sertifikasi MCF`, dan `Title Microsoft` belum disetujui. Sel contoh berisi MOS pada kolom MCF bukan aturan.
8. Final export hanya boleh memakai mapping yang disahkan. Jangan overwrite data lama tanpa persetujuan dan jejak perubahan.
9. Simpan referensi batch SITASI dan Certiport aktif pada sesi sinkronisasi. Pergantian batch aktif harus konsisten dan atomik.
10. Jangan mengarang atribut, status kelulusan, syarat MOS/MCF, atau data mahasiswa. Jika ambigu, gunakan `PERLU_VERIFIKASI` beserta alasan.
11. Gunakan pencocokan deterministik lebih dulu. Jangan menambahkan LLM, OCR, atau scraping tanpa permintaan dan kebutuhan tervalidasi.

## 5. Keamanan dan operasi

- Jangan commit data asli, credential, `.env`, API key, atau log berisi data personal.
- Browser tidak boleh menerima secret atau service-role key.
- Verifikasi access token dan otorisasi staff/admin di backend sebelum endpoint import atau data mahasiswa digunakan.
- Deployment production hanya boleh dilakukan setelah persetujuan ITCC, kebijakan akses dan retensi ditetapkan, serta UAT selesai.
- Jangan menjalankan deployment, migrasi production, penghapusan data, atau impor data asli tanpa instruksi eksplisit pemilik project.
- Jika terblokir oleh kredensial, izin, keputusan bisnis, atau lingkungan, siapkan kode dan tes lokal yang aman. Catat blocker dan lanjutkan hanya bagian tanpa asumsi tersebut.

## 6. Cara kerja hemat token

- Satu prompt mengerjakan satu perubahan terbatas. Jika scope bertambah, catat sebagai backlog lalu berhenti.
- Baca indeks atau struktur lebih dulu, kemudian hanya dokumen dan file yang diperlukan.
- Edit file yang perlu saja. Jangan rewrite file besar, mengubah dependency, atau refactor di luar tugas tanpa alasan kuat.
- Jangan mengulang seluruh code atau diff di chat. Laporkan ringkasan file, tes, dan keputusan.
- Jalankan test relevan lebih dulu. Jalankan test lebih luas pada checkpoint. Jangan install ulang dependency yang sudah tersedia.
- Jangan memakai multi-agent untuk task kecil.
- Jangan meminta model membuat ulang PRD, ERD, atau UI yang sudah tersedia.
- Jika prompt terlalu besar, bagi menjadi dua task kecil dan kerjakan task pertama saja.

## 7. Kebijakan skill

- Gunakan `i-have-adhd` dan `caveman` sebagai gaya kerja default.
- Gunakan semua skill yang relevan dan sebutkan singkat alasan pemilihannya sebelum bekerja.
- Jangan memakai skill yang tidak relevan hanya untuk memenuhi jumlah.
- Investigasi/debugging: `investigate-first`.
- Implementasi fitur/integrasi: `lean-build`.
- Perubahan kecil/bug: `surgical-patch`.
- Refactor tanpa perubahan perilaku: `safe-refactor`.
- Database/Supabase: `supabase` dan `supabase-postgres-best-practices`.
- UI/UX: `design`, `ui-styling`, `ui-ux-pro-max`, dan `web-design-guidelines`.
- Validasi akhir: `verify-and-stop`.
- Review, commit, setup, eksplorasi, atau optimasi: pilih skill `caveman-*` yang sesuai. Jangan menjalankan semuanya sekaligus.

Instruksi sistem, developer, keamanan, dan `AGENTS.md` dengan scope lebih tinggi tetap mempunyai prioritas lebih tinggi.

## 8. Prosedur setiap perubahan

Sebelum mengedit, berikan rencana maksimal lima baris: tujuan, file terkait, dan tes.

1. Kerjakan satu bagian terbatas.
2. Buat atau sesuaikan test untuk kondisi relevan, termasuk normal, kosong, duplikat, salah program, dan nama ambigu bila berlaku.
3. Jalankan test dan lint yang relevan. Jangan mengklaim lulus jika belum dijalankan.
4. Setelah perubahan kode, perbarui `docs/18_CHANGELOG.md` dan `docs/19_AI_PROGRESS.md` dengan tahap, status, langkah berikutnya, blocker, dan tes terakhir.
5. Gunakan kedua file tersebut sebagai checkpoint saat percakapan panjang.

Setiap tahap hanya lulus jika bukti tercatat di `docs/19_AI_PROGRESS.md`. Status belum diuji berarti belum selesai. Jangan mengklaim production ready tanpa bukti.

## 9. Kontrak respons setelah perubahan kode

Gunakan tepat enam bagian berikut dalam Bahasa Indonesia, maksimum sekitar 180 kata kecuali ada masalah kritis:

```text
HASIL TAHAP: [nama] — [SELESAI / SEBAGIAN / TERBLOKIR]
1. Apa yang dibuat/diubah: [1–3 kalimat mudah dipahami]
2. File berubah: [maks. 8 path, jika lebih tulis jumlah + kategori]
3. Cara mencoba: [maks. 3 perintah/langkah]
4. Pengujian: [perintah + PASS/FAIL/BELUM DIJALANKAN serta alasan]
5. Catatan/risiko: [keputusan terbuka, keamanan, atau —]
6. Berikutnya: [satu prompt/tahap berikutnya]
```

## 10. Playbook dan Definition of Done

- Struktur repository harus berupa starter Phase 4, folder `docs`, dan root `AGENTS.md`. Jangan membuat dua root bersarang yang merusak import path.
- Prompt 00 digunakan satu kali per repository/agent. Setelah itu jalankan Prompt 01 sampai 18 secara berurutan dan jangan menjalankan semuanya sekaligus.
- Setiap prompt dapat mengandalkan master rules di `AGENTS.md` dan checkpoint di `docs/19_AI_PROGRESS.md`.
- Jangan mengubah source, konfigurasi, database, atau kontrak API yang tidak diminta.
- Jangan commit atau push tanpa permintaan eksplisit user.

Fitur hanya selesai jika implementasi dapat dijalankan, error tertangani, perlindungan akses sesuai konteks, test terukur, dan bukti atau screenshot tersedia. Struktur kode rapi bukan pengganti pengujian.
