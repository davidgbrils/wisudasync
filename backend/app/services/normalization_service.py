import math
import re
import unicodedata
from typing import Any


EMPTY_VALUES = {"", "NAN", "NONE", "NULL", "NAT"}


def is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return str(value).strip().upper() in EMPTY_VALUES


def clean_text(value: Any) -> str | None:
    if is_empty(value):
        return None
    return " ".join(str(value).strip().split())


def normalize_code(value: Any) -> str | None:
    """Untuk NIM/kode/angkatan yang kadang dibaca Excel sebagai 123.0."""
    if is_empty(value):
        return None

    if isinstance(value, bool):
        return str(value)

    if isinstance(value, int):
        return str(value)

    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return str(value).strip()

    text = str(value).strip()
    if re.fullmatch(r"\d+\.0", text):
        return text[:-2]
    return text


def normalize_name(value: Any) -> str | None:
    """Normalisasi untuk exact matching nama, bukan untuk mengambil keputusan fuzzy."""
    text = clean_text(value)
    if not text:
        return None

    text = unicodedata.normalize("NFKC", text).upper()
    # Tanda baca menjadi spasi. Huruf/angka Unicode tetap dipertahankan.
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    text = " ".join(text.split())
    return text or None


def normalize_upper(value: Any) -> str | None:
    text = clean_text(value)
    return text.upper() if text else None


def to_number(value: Any) -> float | int | None:
    if is_empty(value):
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if isinstance(value, float) and value.is_integer():
            return int(value)
        return value
    text = str(value).strip().replace(",", ".")
    try:
        number = float(text)
        return int(number) if number.is_integer() else number
    except ValueError:
        return None
