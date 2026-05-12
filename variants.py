# -*- coding: utf-8 -*-
"""Таблиця 7.1 — варіанти (три літери для навчання)."""

from __future__ import annotations

from typing import Dict, Tuple

# № варіанту 1..20 -> три літери
VARIANT_LETTERS: Dict[int, Tuple[str, str, str]] = {
    1: ("B", "D", "Y"),
    2: ("F", "U", "M"),
    3: ("N", "D", "X"),
    4: ("L", "O", "S"),
    5: ("G", "J", "Z"),
    6: ("C", "I", "Z"),
    7: ("D", "V", "J"),
    8: ("N", "P", "A"),
    9: ("K", "L", "B"),
    10: ("R", "C", "Z"),
    11: ("C", "H", "I"),
    12: ("E", "K", "V"),
    13: ("P", "Q", "Z"),
    14: ("T", "W", "A"),
    15: ("S", "T", "O"),
    16: ("F", "Y", "S"),
    17: ("Z", "O", "I"),
    18: ("M", "W", "H"),
    19: ("T", "W", "R"),
    20: ("Q", "F", "U"),
}


def get_variant_letters(variant_id: int) -> Tuple[str, str, str]:
    if variant_id not in VARIANT_LETTERS:
        raise ValueError(f"Варіант має бути 1..20, отримано {variant_id}")
    return VARIANT_LETTERS[variant_id]


def variant_from_journal_order(index_in_group_list: int) -> int:
    """
    Номер студента в алфавітному списку групи (1, 2, 3, …) → варіант 1…20 циклічно.

    Формула: v = ((n − 1) mod 20) + 1.
    """
    n = int(index_in_group_list)
    if n < 1:
        raise ValueError("Номер у списку групи має бути >= 1")
    return (n - 1) % 20 + 1


def variant_from_gradebook_last_two_digits(two_digits: int) -> int:
    """
    Останні дві цифри залікової книжки як ціле k від 0 до 99 → варіант 1…20.

    Формула: k = two_digits mod 100; якщо k == 0 → 20; інакше v = ((k − 1) mod 20) + 1.
    """
    k = int(two_digits) % 100
    if k <= 0:
        return 20
    return (k - 1) % 20 + 1
