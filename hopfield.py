# -*- coding: utf-8 -*-
"""
Дискретна мережа Хопфілда (біполярні стани ±1), правило Хебба з нормуванням 1/N.

W = (1/N) * sum_p (x_p @ x_p.T) з нульовою діагоналлю; асинхронне оновлення випадковим порядком нейронів.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np


def bin01_to_bipolar(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    return 2.0 * x - 1.0


def bipolar_to_bin01(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    return ((x + 1.0) / 2.0).clip(0.0, 1.0)


def sign_hebb(x: np.ndarray) -> np.ndarray:
    """sign(0) := +1 (узгоджено з поширеною дискретною реалізацією)."""
    return np.where(x >= -1e-15, 1.0, -1.0)


def train_weights(patterns_bipolar: np.ndarray, *, zero_diagonal: bool = True) -> np.ndarray:
    """
    patterns_bipolar: форма (N, P), кожен стовпчик — образ ±1.

    Якщо zero_diagonal=True (типово для літер): діагональ обнуляється після правила Хебба.
    Для демо з «4 кутами» у N=2 класичне обнулення дає W=0 — тоді варто передати zero_diagonal=False.
    """
    pats = np.asarray(patterns_bipolar, dtype=float)
    if pats.ndim != 2:
        raise ValueError("Очікується матриця (N, P) образів")
    n, _p = pats.shape
    w = np.einsum("ik,jk", pats, pats) / float(n)
    if zero_diagonal:
        np.fill_diagonal(w, 0.0)
    return w


def recall_async(
    w: np.ndarray,
    s0: np.ndarray,
    *,
    max_sweeps: int = 2000,
    rng: Optional[np.random.Generator] = None,
) -> Tuple[np.ndarray, int, bool]:
    """
    Асинхронні оновлення до стабільності (s == sign(W@s)) або max_sweeps проходів по всіх нейронах.

    Повертає (s_кінцевий, кількість_проходів, збігся_до_фіксованої_точки).
    """
    rng = rng or np.random.default_rng()
    s = np.asarray(s0, dtype=float).reshape(-1).copy()
    n = s.size
    converged = False
    sweeps_done = 0
    for sweep in range(max_sweeps):
        prev = s.copy()
        for i in rng.permutation(n):
            h = float(np.dot(w[i, :], s))
            s[i] = 1.0 if h >= 0.0 else -1.0
        sweeps_done = sweep + 1
        if np.array_equal(s, prev):
            converged = True
            break
    return s, sweeps_done, converged


def energy(w: np.ndarray, s: np.ndarray) -> float:
    s = np.asarray(s, dtype=float).reshape(-1)
    return -0.5 * float(s @ w @ s)


@dataclass
class RecallResult:
    initial_bipolar: np.ndarray
    final_bipolar: np.ndarray
    sweeps: int
    converged: bool
    energies: list[float]


def recall_with_energy_trace(
    w: np.ndarray,
    s0: np.ndarray,
    *,
    max_sweeps: int = 2000,
    rng: Optional[np.random.Generator] = None,
) -> RecallResult:
    rng = rng or np.random.default_rng()
    s = np.asarray(s0, dtype=float).reshape(-1).copy()
    n = s.size
    energies: list[float] = [energy(w, s)]
    sweeps_done = 0
    converged = False
    for sweep in range(max_sweeps):
        prev = s.copy()
        for i in rng.permutation(n):
            h = float(np.dot(w[i, :], s))
            s[i] = 1.0 if h >= 0.0 else -1.0
            energies.append(energy(w, s))
        sweeps_done = sweep + 1
        if np.array_equal(s, prev):
            converged = True
            break
    return RecallResult(
        initial_bipolar=np.asarray(s0, dtype=float).reshape(-1).copy(),
        final_bipolar=s,
        sweeps=sweeps_done,
        converged=converged,
        energies=energies,
    )


def noisy_initial(binary_pattern: np.ndarray, sigma: float, rng: np.random.Generator) -> np.ndarray:
    """Спотворення: L + sigma*N(0,1), далі біполярний старт через sign_hebb."""
    x = np.asarray(binary_pattern, dtype=float).reshape(-1)
    noisy = x + sigma * rng.standard_normal(size=x.shape)
    return sign_hebb(noisy)
