"""Crop aset brand dari brand board ITCC Wisuda Sync.

Sumber: ../../asset.png (1536x1024, JPEG).
Output: ../public/brand/*  (+ app icon & favicon Next.js di ../app/)
Jalankan: python scripts/crop_brand_assets.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

FRONTEND = Path(__file__).resolve().parents[1]
ROOT = FRONTEND.parent
SOURCE = ROOT / "asset.png"
OUT = FRONTEND / "public" / "brand"
APP = FRONTEND / "app"

WHITE_TOL = 12


def load() -> Image.Image:
    return Image.open(SOURCE).convert("RGB")


def to_arr(img: Image.Image) -> np.ndarray:
    return np.asarray(img).astype(np.int16)


def non_white_mask(arr: np.ndarray) -> np.ndarray:
    """True untuk piksel yang bukan (hampir) putih."""
    return (255 - arr.min(axis=2)) > WHITE_TOL


def trim(arr: np.ndarray, tol: int = WHITE_TOL) -> np.ndarray:
    mask = (255 - arr.min(axis=2)) > tol
    rows = np.where(mask.any(axis=1))[0]
    cols = np.where(mask.any(axis=0))[0]
    if rows.size == 0 or cols.size == 0:
        raise ValueError("crop kosong")
    return arr[rows[0] : rows[-1] + 1, cols[0] : cols[-1] + 1]


def to_rgba_white_transparent(arr: np.ndarray, feather: bool = True) -> Image.Image:
    """Ubah background putih jadi transparan, pertahankan warna asli."""
    rgb = arr.astype(np.uint8)
    if feather:
        alpha = np.clip(255 - rgb.min(axis=2).astype(np.int16), 0, 255).astype(np.uint8)
    else:
        alpha = np.where(non_white_mask(arr), 255, 0).astype(np.uint8)
    out = np.dstack([rgb, alpha])
    return Image.fromarray(out, "RGBA")


def split_row(arr: np.ndarray, gap: int = 14, min_w: int = 8) -> list[np.ndarray]:
    """Pisahkan item sejajar dalam satu baris berdasarkan kolom kosong."""
    mask = non_white_mask(arr)
    col_has = mask.any(axis=0)
    items: list[np.ndarray] = []
    start = None
    blank = 0
    for i, has in enumerate(col_has):
        if has:
            if start is None:
                start = i
            blank = 0
        elif start is not None:
            blank += 1
            if blank >= gap:
                end = i - blank
                if end - start + 1 >= min_w:
                    items.append(arr[:, start : end + 1])
                start = None
                blank = 0
    if start is not None:
        end = len(col_has) - 1
        if end - start + 1 >= min_w:
            items.append(arr[:, start : end + 1])
    return [trim(it) for it in items]


def save(img: Image.Image, name: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    img.save(path)
    print(f"  {name:34s} {img.width}x{img.height}")
    return path


def remove_annotation_pill(arr: np.ndarray) -> np.ndarray:
    """Hapus label kecil 'HERO BANNER' di sudut kiri atas, timpa dari baris bawahnya."""
    out = arr.copy()
    h, w = out.shape[:2]
    y_lim, x_lim = min(60, h), min(170, w)
    sub = out[:y_lim, :x_lim]
    light = sub.min(axis=2) > 80
    rows = np.where(light.any(axis=1))[0]
    cols = np.where(light.any(axis=0))[0]
    if rows.size == 0:
        return out
    pad = 4
    y0, y1 = max(0, rows[0] - pad), min(h - 1, rows[-1] + pad)
    x0, x1 = max(0, cols[0] - pad), min(w - 1, cols[-1] + pad)
    src = out[min(y1 + 2, h - 1), x0 : x1 + 1]
    out[y0 : y1 + 1, x0 : x1 + 1] = src
    return out


def square(arr: np.ndarray) -> np.ndarray:
    """Potong tengah jadi persegi (sisi terpendek)."""
    h, w = arr.shape[:2]
    side = min(h, w)
    top = (h - side) // 2
    left = (w - side) // 2
    return arr[top : top + side, left : left + side]


def main() -> None:
    src = load()
    arr = to_arr(src)
    print("Aset brand:")

    # 1. Logo utama (cap + teks) dengan latar transparan
    logo_main = trim(arr[30:275, 90:870])
    save(to_rgba_white_transparent(logo_main), "logo-full.png")

    # 2. Mark cap saja (dari sisi kiri logo utama)
    mark = trim(arr[30:275, 90:278])
    save(to_rgba_white_transparent(mark), "logo-mark.png")

    # 3. Tile favicon 256 (persegi) -> app icon + favicon Next.js
    tile = square(trim(arr[63:220, 959:1120], tol=45))
    icon_rgba = to_rgba_white_transparent(tile)
    save(icon_rgba.resize((256, 256), Image.LANCZOS), "app-icon.png")
    icon_rgba.resize((256, 256), Image.LANCZOS).save(APP / "icon.png")
    print("  app/icon.png (dari tile favicon 256)")

    # 4. Banner hero (bersih, latar gelap) - hapus label anotasi
    banner = trim(arr[497:722, 17:1070], tol=6)
    banner = remove_annotation_pill(banner)
    save(Image.fromarray(banner.astype(np.uint8), "RGB"), "hero-banner.png")

    # 5. Ikon fitur (baris bawah kanan) -> 5 ikon
    feature_row = trim(arr[874:958, 1050:1520])
    feature_tiles = split_row(feature_row, gap=14, min_w=20)
    names = ["icon-sitasi.png", "icon-certiport.png", "icon-wisuda.png", "icon-sinkronisasi.png", "icon-laporan.png"]
    for feature, name in zip(feature_tiles, names):
        save(to_rgba_white_transparent(feature), name)


if __name__ == "__main__":
    main()
