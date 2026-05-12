# -*- coding: utf-8 -*-
"""Візуалізація 35-вектора як сітки 7×5."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np


def vector_to_display_grid(vec35: np.ndarray) -> np.ndarray:
    v = np.asarray(vec35, dtype=float).reshape(35)
    m57 = v.reshape(5, 7, order="F")
    return m57.T  # 7 x 5


def plot_char(
    vec35: np.ndarray,
    *,
    ax=None,
    title: Optional[str] = None,
    cmap: str = "Greys",
):
    g = vector_to_display_grid(vec35)
    created = ax is None
    if created:
        _, ax = plt.subplots(figsize=(1.6, 2.0))
    ax.imshow(g, cmap=cmap, vmin=0.0, vmax=1.0, interpolation="nearest")
    ax.set_xticks([])
    ax.set_yticks([])
    if title:
        ax.set_title(title, fontsize=10)
    if created:
        return ax.figure
    return None


def plot_triptych(
    clean: np.ndarray,
    noisy_bin: np.ndarray,
    recalled_bin: np.ndarray,
    *,
    out_path: Optional[Path] = None,
    show: bool = True,
    suptitle: Optional[str] = None,
):
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.6))
    plot_char(clean, ax=axes[0], title="Еталон")
    plot_char(noisy_bin, ax=axes[1], title="Спотворений вхід")
    plot_char(recalled_bin, ax=axes[2], title="Після мережі")
    for ax in axes:
        ax.set_xlabel("")
    if suptitle:
        fig.suptitle(suptitle, fontsize=11)
    fig.tight_layout()
    if out_path:
        fig.savefig(out_path, dpi=160)
    if show:
        plt.show()
    else:
        plt.close(fig)
    return fig


def plot_energy(energies: list[float], *, out_path: Optional[Path] = None, show: bool = True, title: str = "Енергія H"):
    fig, ax = plt.subplots(figsize=(6.0, 3.2))
    ax.plot(energies, lw=1.2)
    ax.set_title(title)
    ax.set_xlabel("Крок оновлення (асинхрон)")
    ax.set_ylabel("H(s)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    if out_path:
        fig.savefig(out_path, dpi=160)
    if show:
        plt.show()
    else:
        plt.close(fig)
    return fig
