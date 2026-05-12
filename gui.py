# -*- coding: utf-8 -*-
"""
Графічний інтерфейс для лаб. 6: вибір варіанту, шуму, літери для triptych, запуск експерименту.
"""

from __future__ import annotations

import json
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from alphabet import letter_column, load_alphabet
from hopfield import (
    bin01_to_bipolar,
    bipolar_to_bin01,
    noisy_initial,
    recall_async,
    recall_with_energy_trace,
    train_weights,
)
from plotting import plot_char
from variants import get_variant_letters


class Lab6GUI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Лаб. 6 — мережа Хопфілда (Python)")
        self.root.geometry("1080x700")

        left = ttk.Frame(self.root, padding=8)
        left.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(left, text="Варіант (1–20)").grid(row=0, column=0, sticky="w")
        self.var_variant = tk.IntVar(value=1)
        ttk.Spinbox(left, from_=1, to=20, textvariable=self.var_variant, width=6).grid(row=0, column=1)

        ttk.Label(left, text="Шум σ").grid(row=1, column=0, sticky="w", pady=4)
        self.var_noise = tk.DoubleVar(value=0.4)
        ttk.Entry(left, textvariable=self.var_noise, width=8).grid(row=1, column=1)

        ttk.Label(left, text="Випробувань").grid(row=2, column=0, sticky="w", pady=4)
        self.var_trials = tk.IntVar(value=30)
        ttk.Entry(left, textvariable=self.var_trials, width=8).grid(row=2, column=1)

        ttk.Label(left, text="Сід (опційно)").grid(row=3, column=0, sticky="w", pady=4)
        self.var_seed = tk.StringVar(value="")
        ttk.Entry(left, textvariable=self.var_seed, width=8).grid(row=3, column=1)

        ttk.Label(left, text="Літера для рисунку").grid(row=4, column=0, sticky="w", pady=4)
        self.var_letter = tk.StringVar(value="B")
        ttk.Entry(left, textvariable=self.var_letter, width=8).grid(row=4, column=1)

        ttk.Label(left, text="Чужа літера").grid(row=5, column=0, sticky="w", pady=4)
        self.var_foreign = tk.StringVar(value="V")
        ttk.Entry(left, textvariable=self.var_foreign, width=8).grid(row=5, column=1)

        ttk.Button(left, text="Експеримент (шум)", command=self._run_noise).grid(
            row=6, column=0, columnspan=2, pady=(10, 4), sticky="ew"
        )
        ttk.Button(left, text="Чужа літера", command=self._run_foreign).grid(row=7, column=0, columnspan=2, pady=4, sticky="ew")
        ttk.Button(left, text="Triptych + енергія", command=self._run_plot).grid(
            row=8, column=0, columnspan=2, pady=4, sticky="ew"
        )

        self.txt = tk.Text(left, width=44, height=22, wrap="word")
        self.txt.grid(row=9, column=0, columnspan=2, pady=8)

        right = ttk.Frame(self.root)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=4, pady=4)

        self.fig = Figure(figsize=(7.0, 6.6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _log(self, s: str) -> None:
        self.txt.insert(tk.END, s + "\n")
        self.txt.see(tk.END)

    def _parse_seed(self) -> int | None:
        t = self.var_seed.get().strip()
        if not t:
            return None
        return int(t)

    def _clear_fig(self) -> None:
        self.fig.clf()
        self.canvas.draw()

    def _run_noise(self) -> None:
        try:
            from main import run_recognition_experiment

            vid = int(self.var_variant.get())
            noise = float(self.var_noise.get())
            trials = int(self.var_trials.get())
            seed = self._parse_seed()
            out = run_recognition_experiment(variant=vid, noise=noise, trials=trials, seed=seed, alphabet_path=None)
            self._log(json.dumps(out, ensure_ascii=False, indent=2))
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Помилка", str(e))

    def _run_foreign(self) -> None:
        try:
            from main import run_foreign_letter

            vid = int(self.var_variant.get())
            fg = self.var_foreign.get().strip()
            seed = self._parse_seed()
            out = run_foreign_letter(variant=vid, foreign=fg, seed=seed, alphabet_path=None)
            self._log(json.dumps(out, ensure_ascii=False, indent=2))
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Помилка", str(e))

    def _run_plot(self) -> None:
        try:
            vid = int(self.var_variant.get())
            letters = get_variant_letters(vid)
            ch = self.var_letter.get().strip().upper()
            if ch not in letters:
                raise ValueError(f"Літера {ch} не з варіанту {letters}")
            alphabet = load_alphabet(None)
            pats_bin = np.stack([letter_column(alphabet, x) for x in letters], axis=1)
            pats_bip = bin01_to_bipolar(pats_bin)
            w = train_weights(pats_bip)
            rng = np.random.default_rng(self._parse_seed())
            li = letters.index(ch)
            target_bin = pats_bin[:, li]
            noise = float(self.var_noise.get())
            s0 = noisy_initial(target_bin, noise, rng)
            s, _, _ = recall_async(w, s0, max_sweeps=5000, rng=rng)
            s_bin = bipolar_to_bin01(s)
            res_en = recall_with_energy_trace(w, s0, max_sweeps=5000, rng=np.random.default_rng(self._parse_seed()))

            self._clear_fig()
            ax1 = self.fig.add_subplot(2, 2, 1)
            ax2 = self.fig.add_subplot(2, 2, 2)
            ax3 = self.fig.add_subplot(2, 2, 3)
            plot_char(target_bin, ax=ax1, title="Еталон")
            plot_char(bipolar_to_bin01(s0), ax=ax2, title="Спотворений")
            plot_char(s_bin, ax=ax3, title="Після мережі")
            ax4 = self.fig.add_subplot(2, 2, 4)
            ax4.plot(res_en.energies, lw=1.0)
            ax4.set_title("Енергія H(s)")
            ax4.grid(True, alpha=0.3)
            self.fig.suptitle(f"Варіант {vid}, {ch}, σ={noise}", fontsize=11)
            self.fig.tight_layout()
            self.canvas.draw()
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Помилка", str(e))

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    Lab6GUI().run()


if __name__ == "__main__":
    main()
