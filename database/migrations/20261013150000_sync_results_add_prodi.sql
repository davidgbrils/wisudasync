-- Migration: Menambahkan kolom kode_prodi dan program_studi pada sync_results.
-- Kolom ini menyimpan data prodi dari workbook wisuda agar tabel hasil
-- dapat menampilkan No, Kode Prodi, Program Studi sesuai permintaan petugas.

begin;

alter table public.sync_results
    add column if not exists kode_prodi text,
    add column if not exists program_studi text;

commit;
