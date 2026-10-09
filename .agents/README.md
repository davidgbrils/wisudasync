# Project Agent Skills

Folder ini menyimpan salinan lokal skill yang sudah terpasang di environment David agar instruksi dan file pendukungnya terlihat dari repository ini.

## Sumber

- `C:\Users\LENOVO\.agents\skills`: sumber utama untuk skill yang terpasang melalui ekosistem agent.
- `C:\Users\LENOVO\.codex\skills\i-have-adhd`: skill Codex tambahan yang tidak ada di sumber utama.
- Skill bawaan `C:\Users\LENOVO\.codex\skills\.system` tidak disalin karena dikelola oleh Codex, bukan instalasi user.

## Struktur

Setiap skill berada di `.agents/skills/<nama-skill>/` dan mempertahankan seluruh file pendukung dari sumbernya. Entry point tiap skill adalah `SKILL.md`.

## Aktivasi di proyek

`AGENTS.md` di root repository mengaktifkan kebijakan skill proyek. Setiap sesi wajib memeriksa folder ini, membaca penuh `SKILL.md` yang relevan, lalu menggunakan semua skill yang sesuai dengan task.

`i-have-adhd` dan `caveman` menjadi gaya kerja default. Skill spesialis seperti debugging, implementasi, refactor, Supabase, UI, dan validasi hanya digunakan saat konteks task cocok. Skill yang tidak relevan atau bertentangan tidak dipaksakan.

Salinan lokal ini adalah snapshot. Perubahan atau pembaruan skill global tidak otomatis tersinkron ke folder proyek.
