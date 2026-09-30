from app.services.normalization_service import normalize_code, normalize_name, normalize_upper


def test_normalize_nim_float():
    assert normalize_code(201931083.0) == "201931083"


def test_normalize_name():
    assert normalize_name(".  Fathurrozaq  ") == "FATHURROZAQ"
    assert normalize_name("A. MUH. FADEL OMAR") == "A MUH FADEL OMAR"


def test_upper_status():
    assert normalize_upper(" lulus ") == "LULUS"
