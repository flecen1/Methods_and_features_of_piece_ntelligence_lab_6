# -*- coding: utf-8 -*-
"""Завантаження Alphabet.csv (35×26, стовпці A…Z)."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np


def default_alphabet_path() -> Path:
    return Path(__file__).resolve().parent / "Alphabet.csv"


def load_alphabet(path: Optional[Path] = None) -> np.ndarray:
    p = Path(path) if path else default_alphabet_path()
    if not p.is_file():
        raise FileNotFoundError(
            f"Не знайдено {p}. Запустіть python build_alphabet_from_glcdfont.py "
            "або покладіть Alphabet.csv у теку проєкту / вкажіть --alphabet."
        )
    m = np.loadtxt(p, delimiter=",", dtype=float)
    if m.shape != (35, 26):
        raise ValueError(f"Очікується форма (35,26), отримано {m.shape}")
    u = np.unique(m)
    if not np.all((u == 0) | (u == 1)):
        raise ValueError("У Alphabet.csv мають бути лише 0 та 1")
    return m


def letter_column(alphabet: np.ndarray, ch: str) -> np.ndarray:
    ch = ch.strip().upper()
    if len(ch) != 1 or not ("A" <= ch <= "Z"):
        raise ValueError(f"Некоректна літера: {ch!r}")
    j = ord(ch) - ord("A")
    return alphabet[:, j].copy()


def letter_index(ch: str) -> int:
    ch = ch.strip().upper()
    if len(ch) != 1 or not ("A" <= ch <= "Z"):
        raise ValueError(f"Некоректна літера: {ch!r}")
    return ord(ch) - ord("A")
