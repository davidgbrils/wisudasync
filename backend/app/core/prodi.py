"""Modul helper pemetaan Program Studi dan Kode NIM."""

import json
import re
from pathlib import Path
from typing import Any

_MAPPING_FILE = Path(__file__).resolve().parent / "prodi_mapping.json"
_DEFAULT_MAPPING: dict[str, Any] = {
    "mcf_required_codes": ["31", "32"],
    "programs": {
        "10": {"nama": "S2 Teknik Elektro", "jenjang": "S2", "mcf_wajib": False},
        "11": {"nama": "S1 Teknik Elektro", "jenjang": "S1", "mcf_wajib": False},
        "12": {"nama": "S1 Teknik Mesin", "jenjang": "S1", "mcf_wajib": False},
        "14": {"nama": "S1 Teknik Tenaga Listrik", "jenjang": "S1", "mcf_wajib": False},
        "15": {"nama": "S1 Teknik Sistem Energi", "jenjang": "S1", "mcf_wajib": False},
        "20": {"nama": "S2 Teknik Mesin", "jenjang": "S2", "mcf_wajib": False},
        "21": {"nama": "S1 Teknik Sipil", "jenjang": "S1", "mcf_wajib": False},
        "22": {"nama": "S1 Teknik Geografi", "jenjang": "S1", "mcf_wajib": False},
        "23": {"nama": "S1 Teknik Lingkungan", "jenjang": "S1", "mcf_wajib": False},
        "30": {"nama": "S2 Ilmu Komputer", "jenjang": "S2", "mcf_wajib": False},
        "31": {"nama": "S1 Teknik Informatika", "jenjang": "S1", "mcf_wajib": True},
        "32": {"nama": "S1 Sistem Informasi", "jenjang": "S1", "mcf_wajib": True},
        "33": {"nama": "S1 Sains Data", "jenjang": "S1", "mcf_wajib": False},
        "40": {"nama": "S2 Teknik Mesin", "jenjang": "S2", "mcf_wajib": False},
        "41": {"nama": "S1 Bisnis Energi", "jenjang": "S1", "mcf_wajib": False},
        "42": {"nama": "S1 Teknik Industri", "jenjang": "S1", "mcf_wajib": False},
        "71": {"nama": "D3 Teknologi Listrik", "jenjang": "D3", "mcf_wajib": False},
        "72": {"nama": "D3 Teknik Mesin", "jenjang": "D3", "mcf_wajib": False},
        "80": {"nama": "Program Profesi Insinyur", "jenjang": "Profesi", "mcf_wajib": False},
    },
}


def load_prodi_config() -> dict[str, Any]:
    """Muat konfigurasi pemetaan prodi dari file JSON.

    Fallback ke _DEFAULT_MAPPING jika file tidak ditemukan atau format tidak valid.
    """
    if _MAPPING_FILE.exists():
        try:
            with open(_MAPPING_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "programs" in data:
                    return data
        except Exception:
            pass
    return _DEFAULT_MAPPING


def get_programs() -> dict[str, dict[str, Any]]:
    """Kembalikan dictionary kode -> data program studi."""
    config = load_prodi_config()
    return config.get("programs", _DEFAULT_MAPPING["programs"])


def get_mcf_required_codes() -> list[str]:
    """Kembalikan daftar kode prodi yang diwajibkan/relevan untuk MCF."""
    config = load_prodi_config()
    return config.get("mcf_required_codes", ["31", "32"])


def extract_kode_prodi_from_nim(nim: str | None) -> str:
    """Ambil kode prodi langsung dari NIM: 2 digit setelah 4 digit tahun angkatan.

    Aturan:
    - Mahasiswa ITPLN memiliki pola NIM: 4 digit tahun angkatan + 2 digit kode prodi + nomor urut.
    - Contoh:
      * 202331243 -> tahun 2023, 2 digit setelah tahun adalah '31' (S1 Teknik Informatika).
      * 202110039 -> tahun 2021, 2 digit setelah tahun adalah '10'.
      * 202111039 -> tahun 2021, 2 digit setelah tahun adalah '11' (S1 Teknik Elektro).
    - Jika NIM memakai pemisah (misal 2021-31-039), hanya karakter digit yang dihitung.
    - Fallback untuk NIM tanpa 4 digit tahun: jika 2 digit awal merupakan kode prodi terdaftar.
    """
    if not nim:
        return ""

    nim_str = str(nim).strip()
    clean_digits = re.sub(r"\D", "", nim_str)

    # 4 digit tahun angkatan + minimal 2 digit kode prodi
    if len(clean_digits) >= 6:
        return clean_digits[4:6]

    # Fallback: jika 2 digit awal adalah kode terdaftar
    programs = get_programs()
    if len(clean_digits) >= 2 and clean_digits[:2] in programs:
        return clean_digits[:2]

    return ""


def resolve_kode_prodi(nim: str | None, kode_prodi: str | None = None) -> str:
    """Tentukan kode prodi dengan memprioritaskan ekstraksi langsung dari NIM.

    Jika dari NIM tidak dapat diekstrak (misal NIM kosong / bukan angka),
    gunakan kode_prodi cadangan jika tersedia.
    """
    from_nim = extract_kode_prodi_from_nim(nim)
    if from_nim:
        return from_nim

    if kode_prodi:
        cleaned = str(kode_prodi).strip()
        if cleaned:
            return cleaned

    return ""


def resolve_program_studi(kode_prodi: str | None, current_ps: str | None = None) -> str:
    """Tentukan nama program studi dari kode prodi.

    Jika kode prodi ada di master mapping, gunakan nama resmi dari master data.
    Jika tidak ada di master mapping, gunakan current_ps jika tersedia.
    """
    if not kode_prodi:
        return str(current_ps).strip() if current_ps else ""

    clean_kode = str(kode_prodi).strip()
    programs = get_programs()
    prog_info = programs.get(clean_kode)
    if prog_info and "nama" in prog_info:
        return str(prog_info["nama"])

    return str(current_ps).strip() if current_ps else ""


def is_mcf_relevant(kode_prodi: str | None) -> bool:
    """Periksa apakah kode prodi relevan/wajib sertifikasi MCF."""
    if not kode_prodi:
        return False
    return str(kode_prodi).strip() in get_mcf_required_codes()
