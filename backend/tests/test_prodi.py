from app.core.prodi import (
    get_programs,
    get_mcf_required_codes,
    is_mcf_relevant,
    load_prodi_config,
    resolve_kode_prodi,
    resolve_program_studi,
)


def test_load_prodi_config():
    config = load_prodi_config()
    assert "programs" in config
    assert "mcf_required_codes" in config

    programs = get_programs()
    # Pastikan semua 19 kode prodi terdaftar
    expected_codes = [
        "10", "11", "12", "14", "15", "20", "21", "22", "23",
        "30", "31", "32", "33", "40", "41", "42", "71", "72", "80"
    ]
    for code in expected_codes:
        assert code in programs, f"Kode {code} harus terdaftar"

    assert programs["10"]["nama"] == "S2 Teknik Elektro"
    assert programs["31"]["nama"] == "S1 Teknik Informatika"
    assert programs["32"]["nama"] == "S1 Sistem Informasi"
    assert programs["33"]["nama"] == "S1 Sains Data"
    assert programs["71"]["nama"] == "D3 Teknologi Listrik"


def test_resolve_kode_prodi():
    # 1. Contoh dari pengguna: 2 digit setelah tahun angkatan 4 digit
    assert resolve_kode_prodi("202331243") == "31"
    assert resolve_kode_prodi("202110039") == "10"
    assert resolve_kode_prodi("202031001") == "31"
    assert resolve_kode_prodi("202111045") == "11"
    assert resolve_kode_prodi("202233010") == "33"
    assert resolve_kode_prodi("201971003") == "71"

    # 2. Dengan karakter pemisah non-digit (misal tanda minus atau titik)
    assert resolve_kode_prodi("2023-31-243") == "31"
    assert resolve_kode_prodi("2021.11.039") == "11"

    # 3. Ekstraksi dari NIM selalu diprioritaskan
    assert resolve_kode_prodi("202331243", "99") == "31"

    # 4. Dari prefix 2 digit (tanpa 4 digit tahun)
    assert resolve_kode_prodi("14002") == "14"

    # 5. Kasus kosong
    assert resolve_kode_prodi(None, None) == ""
    assert resolve_kode_prodi("", "") == ""
    assert resolve_kode_prodi(None, "32") == "32"


def test_resolve_program_studi():
    # 1. Lookup resmi dari kode terdaftar
    assert resolve_program_studi("10") == "S2 Teknik Elektro"
    assert resolve_program_studi("31") == "S1 Teknik Informatika"
    assert resolve_program_studi("31", "Custom Nama") == "S1 Teknik Informatika"
    assert resolve_program_studi("32") == "S1 Sistem Informasi"
    assert resolve_program_studi("33") == "S1 Sains Data"
    assert resolve_program_studi("11") == "S1 Teknik Elektro"

    # 2. Fallback untuk kode tidak terdaftar
    assert resolve_program_studi("99", "Prodi Non-Standar") == "Prodi Non-Standar"
    assert resolve_program_studi("99") == ""
    assert resolve_program_studi(None, "Prodi Manual") == "Prodi Manual"
    assert resolve_program_studi(None) == ""


def test_is_mcf_relevant():
    assert is_mcf_relevant("31") is True
    assert is_mcf_relevant("32") is True
    assert is_mcf_relevant("33") is False
    assert is_mcf_relevant("11") is False
    assert is_mcf_relevant(None) is False
    assert is_mcf_relevant("") is False
