# -*- coding: utf-8 -*-
"""Побудова Alphabet.csv (35×26) з Adafruit glcdfont.c."""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np


def _parse_font_bytes(text: str) -> list[int]:
    m = re.search(r"font\[\]\s*PROGMEM\s*=\s*\{([\s\S]*?)\};", text)
    if not m:
        raise ValueError("Не знайдено масиву font[] у glcdfont.c")
    body = m.group(1)
    nums: list[int] = []
    for tok in re.findall(r"0x([0-9A-Fa-f]+)", body):
        nums.append(int(tok, 16))
    return nums


def _char_column_major_35(font_bytes: list[int], ascii_code: int) -> np.ndarray:
    """Вектор довжини 35 у column-major порядку для сітки 5×7 (див. README)."""
    off = ascii_code * 5
    block = font_bytes[off : off + 5]
    if len(block) != 5:
        raise ValueError(f"Недостатньо байтів для символу {ascii_code}")
    # 5 колонок (ширина), у кожній до 7 вертикальних пікселів (молодші біти — вгорі, як у Adafruit_GFX)
    H = np.zeros((7, 5), dtype=np.float64)
    for col in range(5):
        b = block[col]
        for row in range(7):
            H[row, col] = 1.0 if (b >> row) & 1 else 0.0
    M = H.T  # (5,7)
    return M.reshape(-1, order="F")


def build_alphabet_matrix(glcd_path: Path) -> np.ndarray:
    font_bytes = _parse_font_bytes(glcd_path.read_text(encoding="utf-8", errors="replace"))
    cols = []
    for ac in range(ord("A"), ord("Z") + 1):
        cols.append(_char_column_major_35(font_bytes, ac))
    return np.stack(cols, axis=1)  # 35 x 26


def main() -> None:
    import urllib.request

    here = Path(__file__).resolve().parent
    glcd = here / "glcdfont.c"
    if not glcd.is_file():
        url = "https://raw.githubusercontent.com/adafruit/Adafruit-GFX-Library/master/glcdfont.c"
        glcd.write_bytes(urllib.request.urlopen(url, timeout=60).read())
    M = build_alphabet_matrix(glcd)
    out = here / "Alphabet.csv"
    np.savetxt(out, M, delimiter=",", fmt="%d")
    print("OK:", out, "shape", M.shape, "unique", np.unique(M))


if __name__ == "__main__":
    main()
