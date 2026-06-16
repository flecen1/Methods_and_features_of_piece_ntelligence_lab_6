# -*- coding: utf-8 -*-
"""Компактний сучасний GUI для лабораторної роботи 6."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from alphabet import letter_column, load_alphabet
from hopfield import bin01_to_bipolar, bipolar_to_bin01, noisy_initial, recall_with_energy_trace, train_weights
from main import run_foreign_letter, run_recognition_experiment
from plotting import plot_char
from variants import get_variant_letters


class Lab6GUI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Лабораторна робота 6 — мережа Хопфілда")
        self.root.geometry("1400x880")
        self.root.minsize(1220, 760)

        self.var_variant = tk.IntVar(value=1)
        self.var_noise = tk.StringVar(value="0.40")
        self.var_trials = tk.StringVar(value="40")
        self.var_seed = tk.StringVar(value="")
        self.var_letter = tk.StringVar(value="B")
        self.var_foreign = tk.StringVar(value="V")

        self.summary_var = tk.StringVar(value="Оберіть режим зліва та запустіть розрахунок.")
        self.variant_info_var = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="Готово.")

        self.metric_title_vars = [
            tk.StringVar(value="Режим"),
            tk.StringVar(value="Літери"),
            tk.StringVar(value="Підсумок"),
        ]
        self.metric_value_vars = [
            tk.StringVar(value="-"),
            tk.StringVar(value="-"),
            tk.StringVar(value="-"),
        ]

        self._foreign_values = [chr(code) for code in range(ord("A"), ord("Z") + 1)]

        self._configure_style()
        self._build_layout()
        self.var_variant.trace_add("write", self._refresh_variant_letters)
        self._refresh_variant_letters()
        self._set_placeholder_visual()

    def _configure_style(self) -> None:
        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        bg = "#f4f7fb"
        panel = "#ffffff"
        panel_soft = "#f8fbff"
        ink = "#0f172a"
        muted = "#64748b"
        accent = "#2563eb"
        accent_dark = "#1d4ed8"
        accent_soft = "#dbeafe"
        sidebar = "#111827"
        border = "#dbe4f0"

        self.root.configure(bg=bg)
        style.configure(".", font=("Segoe UI", 10))
        style.configure("App.TFrame", background=bg)
        style.configure("Panel.TFrame", background=panel, relief="flat")
        style.configure("SoftPanel.TFrame", background=panel_soft, relief="flat")
        style.configure("Sidebar.TFrame", background=sidebar)
        style.configure("SidebarInner.TFrame", background=sidebar)
        style.configure("SidebarCard.TFrame", background="#182133", relief="flat")
        style.configure("SidebarTitle.TLabel", background=sidebar, foreground="#f8fafc", font=("Segoe UI Semibold", 20))
        style.configure("SidebarText.TLabel", background=sidebar, foreground="#9fb0c7", font=("Segoe UI", 10))
        style.configure("SidebarMuted.TLabel", background="#182133", foreground="#c4cfdf", font=("Segoe UI", 10))
        style.configure("Badge.TLabel", background=accent_soft, foreground=accent_dark, font=("Segoe UI Semibold", 9), padding=(10, 4))
        style.configure("Title.TLabel", background=panel, foreground=ink, font=("Segoe UI Semibold", 20))
        style.configure("Body.TLabel", background=panel, foreground=ink)
        style.configure("Muted.TLabel", background=panel, foreground=muted)
        style.configure("Summary.TLabel", background=panel, foreground=ink, font=("Segoe UI", 11))
        style.configure("Metric.TFrame", background=panel_soft, relief="flat")
        style.configure("MetricTitle.TLabel", background=panel_soft, foreground=muted, font=("Segoe UI", 9))
        style.configure("MetricValue.TLabel", background=panel_soft, foreground=ink, font=("Segoe UI Semibold", 14))
        style.configure("SectionTitle.TLabel", background=panel, foreground=ink, font=("Segoe UI Semibold", 12))
        style.configure("SectionHint.TLabel", background=panel, foreground=muted, font=("Segoe UI", 9))
        style.configure(
            "Primary.TButton",
            background=accent,
            foreground="white",
            borderwidth=0,
            focusthickness=0,
            padding=(14, 10),
            font=("Segoe UI Semibold", 10),
        )
        style.map(
            "Primary.TButton",
            background=[("active", accent_dark), ("pressed", accent_dark)],
            foreground=[("disabled", "#dbeafe")],
        )
        style.configure(
            "Secondary.TButton",
            background="#243041",
            foreground="white",
            borderwidth=0,
            focusthickness=0,
            padding=(14, 10),
            font=("Segoe UI Semibold", 10),
        )
        style.map("Secondary.TButton", background=[("active", "#334155"), ("pressed", "#334155")])
        style.configure(
            "Modern.TEntry",
            fieldbackground="#f8fafc",
            background="#f8fafc",
            foreground=ink,
            bordercolor=border,
            lightcolor=border,
            darkcolor=border,
            insertcolor=ink,
            padding=8,
            relief="flat",
        )
        style.configure(
            "Modern.TCombobox",
            fieldbackground="#f8fafc",
            background="#f8fafc",
            foreground=ink,
            bordercolor=border,
            lightcolor=border,
            darkcolor=border,
            arrowsize=14,
            padding=6,
            relief="flat",
        )
        style.map("Modern.TCombobox", fieldbackground=[("readonly", "#f8fafc")], selectbackground=[("readonly", "#f8fafc")])
        style.configure(
            "Modern.TSpinbox",
            fieldbackground="#f8fafc",
            background="#f8fafc",
            foreground=ink,
            bordercolor=border,
            lightcolor=border,
            darkcolor=border,
            arrowsize=14,
            padding=6,
            relief="flat",
        )
        style.configure(
            "Treeview",
            background=panel,
            fieldbackground=panel,
            foreground=ink,
            bordercolor=border,
            lightcolor=border,
            darkcolor=border,
            rowheight=34,
            font=("Segoe UI", 10),
        )
        style.map("Treeview", background=[("selected", accent_soft)], foreground=[("selected", ink)])
        style.configure("Treeview.Heading", background="#eef4fb", foreground=ink, font=("Segoe UI Semibold", 10), relief="flat")
        style.configure("TNotebook", background=bg, borderwidth=0, tabmargins=(0, 0, 0, 0))
        style.configure("TNotebook.Tab", background="#e5edf8", foreground=muted, padding=(18, 10), font=("Segoe UI Semibold", 10))
        style.map("TNotebook.Tab", background=[("selected", panel), ("active", "#edf4ff")], foreground=[("selected", accent_dark)])

    def _build_layout(self) -> None:
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        sidebar = ttk.Frame(self.root, style="Sidebar.TFrame", padding=(22, 24))
        sidebar.grid(row=0, column=0, sticky="ns")
        content = ttk.Frame(self.root, style="App.TFrame", padding=18)
        content.grid(row=0, column=1, sticky="nsew")

        self._build_sidebar(sidebar)
        self._build_content(content)

    def _build_sidebar(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)

        ttk.Label(parent, text="Hopfield Lab", style="SidebarTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            parent,
            text="Компактний інтерфейс: параметри зліва, таблиця та графіки справа.",
            style="SidebarText.TLabel",
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(6, 18))

        card = ttk.Frame(parent, style="SidebarCard.TFrame", padding=16)
        card.grid(row=2, column=0, sticky="ew")
        card.columnconfigure(1, weight=1)

        ttk.Label(card, text="Варіант", style="SidebarMuted.TLabel").grid(row=0, column=0, sticky="w", pady=6)
        ttk.Spinbox(card, from_=1, to=20, textvariable=self.var_variant, width=8, wrap=True, style="Modern.TSpinbox").grid(
            row=0, column=1, sticky="ew", padx=(10, 0), pady=6
        )

        ttk.Label(card, text="Шум σ", style="SidebarMuted.TLabel").grid(row=1, column=0, sticky="w", pady=6)
        ttk.Entry(card, textvariable=self.var_noise, style="Modern.TEntry").grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=6)

        ttk.Label(card, text="Випробувань", style="SidebarMuted.TLabel").grid(row=2, column=0, sticky="w", pady=6)
        ttk.Entry(card, textvariable=self.var_trials, style="Modern.TEntry").grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=6)

        ttk.Label(card, text="Seed", style="SidebarMuted.TLabel").grid(row=3, column=0, sticky="w", pady=6)
        ttk.Entry(card, textvariable=self.var_seed, style="Modern.TEntry").grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=6)

        ttk.Label(card, text="Літера (triptych)", style="SidebarMuted.TLabel").grid(row=4, column=0, sticky="w", pady=6)
        self.letter_combo = ttk.Combobox(card, textvariable=self.var_letter, state="readonly", style="Modern.TCombobox")
        self.letter_combo.grid(row=4, column=1, sticky="ew", padx=(10, 0), pady=6)

        ttk.Label(card, text="Чужа літера", style="SidebarMuted.TLabel").grid(row=5, column=0, sticky="w", pady=6)
        self.foreign_combo = ttk.Combobox(
            card,
            textvariable=self.var_foreign,
            state="readonly",
            values=self._foreign_values,
            style="Modern.TCombobox",
        )
        self.foreign_combo.grid(row=5, column=1, sticky="ew", padx=(10, 0), pady=6)

        ttk.Label(card, textvariable=self.variant_info_var, style="SidebarMuted.TLabel", wraplength=250, justify="left").grid(
            row=6, column=0, columnspan=2, sticky="w", pady=(10, 0)
        )

        buttons = ttk.Frame(parent, style="SidebarInner.TFrame")
        buttons.grid(row=3, column=0, sticky="ew", pady=(18, 0))
        buttons.columnconfigure(0, weight=1)

        ttk.Button(buttons, text="Шумовий експеримент", command=self._run_noise, style="Primary.TButton").grid(
            row=0, column=0, sticky="ew", pady=(0, 8)
        )
        ttk.Button(buttons, text="Чужа літера", command=self._run_foreign, style="Secondary.TButton").grid(
            row=1, column=0, sticky="ew", pady=8
        )
        ttk.Button(buttons, text="Triptych + енергія", command=self._run_plot, style="Secondary.TButton").grid(
            row=2, column=0, sticky="ew", pady=8
        )

        ttk.Label(parent, textvariable=self.status_var, style="SidebarText.TLabel", wraplength=260, justify="left").grid(
            row=4, column=0, sticky="sw", pady=(18, 0)
        )

    def _build_content(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(2, weight=1)

        title_card = ttk.Frame(parent, style="Panel.TFrame", padding=22)
        title_card.grid(row=0, column=0, sticky="ew")
        title_card.columnconfigure(0, weight=1)
        ttk.Label(title_card, text="Лабораторна робота 6", style="Badge.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(title_card, text="Мережа Хопфілда для розпізнавання образів", style="Title.TLabel").grid(
            row=1, column=0, sticky="w", pady=(12, 0)
        )
        ttk.Label(
            title_card,
            text="Інтерфейс для демонстрації результатів, скріншотів і перевірки експериментів.",
            style="SectionHint.TLabel",
        ).grid(row=2, column=0, sticky="w", pady=(6, 0))
        ttk.Label(
            title_card,
            textvariable=self.summary_var,
            style="Muted.TLabel",
            wraplength=920,
            justify="left",
        ).grid(row=3, column=0, sticky="w", pady=(12, 0))

        metrics = ttk.Frame(parent, style="App.TFrame")
        metrics.grid(row=1, column=0, sticky="ew", pady=(14, 14))
        metrics.columnconfigure((0, 1, 2), weight=1)

        for index in range(3):
            card = ttk.Frame(metrics, style="Metric.TFrame", padding=18)
            card.grid(row=0, column=index, sticky="ew", padx=(0 if index == 0 else 7, 0 if index == 2 else 7))
            ttk.Label(card, textvariable=self.metric_title_vars[index], style="MetricTitle.TLabel").grid(
                row=0, column=0, sticky="w"
            )
            ttk.Label(card, textvariable=self.metric_value_vars[index], style="MetricValue.TLabel").grid(
                row=1, column=0, sticky="w", pady=(8, 0)
            )

        notebook = ttk.Notebook(parent)
        notebook.grid(row=2, column=0, sticky="nsew")

        results_tab = ttk.Frame(notebook, style="Panel.TFrame", padding=16)
        charts_tab = ttk.Frame(notebook, style="Panel.TFrame", padding=16)
        notebook.add(results_tab, text="Результати")
        notebook.add(charts_tab, text="Візуалізація")

        results_tab.columnconfigure(0, weight=1)
        results_tab.rowconfigure(1, weight=1)

        ttk.Label(results_tab, text="Зведена таблиця", style="SectionTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            results_tab,
            text="Ключові показники поточного режиму.",
            style="SectionHint.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        columns = ("name", "value", "note")
        self.results_table = ttk.Treeview(results_tab, columns=columns, show="headings")
        self.results_table.heading("name", text="Показник")
        self.results_table.heading("value", text="Значення")
        self.results_table.heading("note", text="Коментар")
        self.results_table.column("name", width=220, anchor="w")
        self.results_table.column("value", width=170, anchor="center")
        self.results_table.column("note", width=420, anchor="w")
        self.results_table.grid(row=2, column=0, sticky="nsew", pady=(14, 0))

        charts_tab.columnconfigure(0, weight=1)
        charts_tab.rowconfigure(0, weight=1)
        self.fig = Figure(figsize=(8.5, 6.0), dpi=110, facecolor="white", constrained_layout=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=charts_tab)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    def _set_status(self, text: str) -> None:
        self.status_var.set(text)

    def _set_metrics(self, title1: str, value1: str, title2: str, value2: str, title3: str, value3: str) -> None:
        items = ((title1, value1), (title2, value2), (title3, value3))
        for index, (title, value) in enumerate(items):
            self.metric_title_vars[index].set(title)
            self.metric_value_vars[index].set(value)

    def _clear_table(self) -> None:
        for item_id in self.results_table.get_children():
            self.results_table.delete(item_id)

    def _add_table_row(self, name: str, value: str, note: str = "") -> None:
        self.results_table.insert("", tk.END, values=(name, value, note))

    def _set_placeholder_visual(self) -> None:
        self.fig.clf()
        ax = self.fig.add_subplot(1, 1, 1)
        ax.axis("off")
        ax.text(0.5, 0.62, "Режим перегляду", ha="center", va="center", fontsize=23, fontweight="bold", color="#0f172a")
        ax.text(
            0.5,
            0.42,
            "Зліва — параметри.\nСправа — таблиця та графіки.",
            ha="center",
            va="center",
            fontsize=12,
            color="#64748b",
        )
        self.canvas.draw()

    def _variant_letters(self) -> tuple[str, str, str]:
        return get_variant_letters(int(self.var_variant.get()))

    def _refresh_variant_letters(self, *_args) -> None:
        try:
            letters = self._variant_letters()
        except Exception:
            return
        self.variant_info_var.set(f"Навчальні літери: {', '.join(letters)}")
        self.letter_combo.configure(values=letters)
        if self.var_letter.get() not in letters:
            self.var_letter.set(letters[0])
        foreign_vals = [ch for ch in self._foreign_values if ch not in letters]
        self.foreign_combo.configure(values=foreign_vals)
        if self.var_foreign.get() in letters or self.var_foreign.get() not in foreign_vals:
            self.var_foreign.set(foreign_vals[0] if foreign_vals else "V")

    def _parse_seed(self) -> int | None:
        seed_text = self.var_seed.get().strip()
        return None if not seed_text else int(seed_text)

    def _read_numeric_inputs(self) -> tuple[int, float, int, int | None]:
        variant = int(self.var_variant.get())
        if not 1 <= variant <= 20:
            raise ValueError("Варіант має бути від 1 до 20.")

        noise = float(self.var_noise.get().strip())
        if noise < 0:
            raise ValueError("Шум не може бути від’ємним.")

        trials = int(self.var_trials.get().strip())
        if trials <= 0:
            raise ValueError("Кількість випробувань має бути більше нуля.")

        return variant, noise, trials, self._parse_seed()

    def _load_variant_data(self, variant: int) -> tuple[np.ndarray, tuple[str, str, str], np.ndarray, np.ndarray]:
        alphabet = load_alphabet(None)
        letters = get_variant_letters(variant)
        patterns_bin = np.stack([letter_column(alphabet, letter) for letter in letters], axis=1)
        weights = train_weights(bin01_to_bipolar(patterns_bin))
        return alphabet, letters, patterns_bin, weights

    def _draw_noise_visual(self, patterns_bin: np.ndarray, letters: tuple[str, str, str], accuracies: list[float], noise: float) -> None:
        self.fig.clf()
        grid = self.fig.add_gridspec(2, 3, height_ratios=[1, 1.15])
        for index, letter in enumerate(letters):
            ax = self.fig.add_subplot(grid[0, index])
            plot_char(patterns_bin[:, index], ax=ax, title=f"Еталон {letter}")
        chart_ax = self.fig.add_subplot(grid[1, :])
        bars = chart_ax.bar(list(letters), accuracies, color=["#3b82f6", "#10b981", "#f59e0b"], width=0.55)
        chart_ax.set_ylim(0.0, 1.05)
        chart_ax.set_title(f"Точність розпізнавання при σ={noise}")
        chart_ax.set_ylabel("Accuracy")
        chart_ax.grid(axis="y", alpha=0.25)
        for bar, value in zip(bars, accuracies):
            chart_ax.text(bar.get_x() + bar.get_width() / 2, value + 0.03, f"{value:.2f}", ha="center")
        self.canvas.draw()

    def _draw_foreign_visual(
        self,
        patterns_bin: np.ndarray,
        letters: tuple[str, str, str],
        foreign_letter: str,
        foreign_bin: np.ndarray,
        final_bin: np.ndarray,
        closest_letter: str,
        distances: list[int],
    ) -> None:
        self.fig.clf()
        grid = self.fig.add_gridspec(2, 3, height_ratios=[1, 1.15])
        for index, letter in enumerate(letters):
            ax = self.fig.add_subplot(grid[0, index])
            plot_char(patterns_bin[:, index], ax=ax, title=f"Еталон {letter}")
        ax_foreign = self.fig.add_subplot(grid[1, 0])
        plot_char(foreign_bin, ax=ax_foreign, title=f"Чужа {foreign_letter}")
        ax_final = self.fig.add_subplot(grid[1, 1])
        plot_char(final_bin, ax=ax_final, title=f"Результат → {closest_letter}")
        ax_bar = self.fig.add_subplot(grid[1, 2])
        ax_bar.bar(list(letters), distances, color="#8b5cf6", width=0.55)
        ax_bar.set_title("Відстань Геммінга")
        ax_bar.grid(axis="y", alpha=0.25)
        self.canvas.draw()

    def _draw_triptych_visual(
        self,
        target_bin: np.ndarray,
        noisy_bin: np.ndarray,
        recalled_bin: np.ndarray,
        energies: list[float],
        letter: str,
        noise: float,
    ) -> None:
        self.fig.clf()
        grid = self.fig.add_gridspec(2, 3, height_ratios=[1, 1.2])
        ax1 = self.fig.add_subplot(grid[0, 0])
        plot_char(target_bin, ax=ax1, title=f"Еталон {letter}")
        ax2 = self.fig.add_subplot(grid[0, 1])
        plot_char(noisy_bin, ax=ax2, title=f"Спотворений, σ={noise}")
        ax3 = self.fig.add_subplot(grid[0, 2])
        plot_char(recalled_bin, ax=ax3, title="Після мережі")
        ax4 = self.fig.add_subplot(grid[1, :])
        ax4.plot(energies, color="#ef4444", lw=1.7)
        ax4.set_title("Енергія мережі")
        ax4.set_xlabel("Крок оновлення")
        ax4.set_ylabel("H(s)")
        ax4.grid(True, alpha=0.25)
        self.canvas.draw()

    def _run_noise(self) -> None:
        try:
            variant, noise, trials, seed = self._read_numeric_inputs()
            _alphabet, letters, patterns_bin, _weights = self._load_variant_data(variant)
            result = run_recognition_experiment(
                variant=variant,
                noise=noise,
                trials=trials,
                seed=seed,
                alphabet_path=None,
            )

            per_letter = result["per_letter"]
            accuracies = [float(item["accuracy"]) for item in per_letter]
            avg_accuracy = sum(accuracies) / len(accuracies)
            best = max(per_letter, key=lambda item: float(item["accuracy"]))

            self.summary_var.set(
                f"Шумовий експеримент завершено. Середня точність {avg_accuracy:.3f}, "
                f"найкраща літера {best['letter']} — {best['accuracy']:.3f}."
            )
            self._set_metrics(
                "Режим", "Шум",
                "Літери", ", ".join(letters),
                "Середня точність", f"{avg_accuracy:.3f}",
            )
            self._clear_table()
            for item in per_letter:
                self._add_table_row(
                    f"Літера {item['letter']}",
                    f"{float(item['accuracy']):.3f}",
                    f"Збіжність {float(item['converged_fraction']):.3f}",
                )
            self._draw_noise_visual(patterns_bin, letters, accuracies, noise)
            self._set_status("Шумовий експеримент виконано.")
        except Exception as exc:  # noqa: BLE001
            self._set_status("Помилка шумового експерименту.")
            messagebox.showerror("Помилка", str(exc))

    def _run_foreign(self) -> None:
        try:
            variant, _noise, _trials, seed = self._read_numeric_inputs()
            alphabet, letters, patterns_bin, _weights = self._load_variant_data(variant)
            foreign = self.var_foreign.get().strip().upper()
            if foreign in letters:
                raise ValueError("Чужа літера не повинна збігатися з навчальними.")

            result = run_foreign_letter(variant=variant, foreign=foreign, seed=seed, alphabet_path=None)
            final_bin = bipolar_to_bin01(np.asarray(result["final_bipolar"], dtype=float))
            foreign_bin = letter_column(alphabet, foreign)
            closest = result["closest_trained_letter"]
            distances = [int(value) for value in result["hamming_bipolar_to_trained"]]

            self.summary_var.set(
                f"Літера {foreign} після релаксації найближча до {closest}. "
                f"Збіжність: {'так' if result['converged'] else 'ні'}, проходів: {result['sweeps']}."
            )
            self._set_metrics(
                "Режим", "Чужа літера",
                "Літери", ", ".join(letters),
                "Найближчий еталон", closest,
            )
            self._clear_table()
            self._add_table_row("Чужа літера", foreign, "Не в навчанні")
            self._add_table_row("Проходів", str(result["sweeps"]), "Ітерації релаксації")
            self._add_table_row("Збіжність", "Так" if result["converged"] else "Ні", "")
            for letter, distance in zip(letters, distances):
                self._add_table_row(f"Відстань до {letter}", str(distance), "Геммінг")
            self._draw_foreign_visual(patterns_bin, letters, foreign, foreign_bin, final_bin, closest, distances)
            self._set_status("Аналіз чужої літери виконано.")
        except Exception as exc:  # noqa: BLE001
            self._set_status("Помилка аналізу чужої літери.")
            messagebox.showerror("Помилка", str(exc))

    def _run_plot(self) -> None:
        try:
            variant, noise, _trials, seed = self._read_numeric_inputs()
            _alphabet, letters, patterns_bin, weights = self._load_variant_data(variant)
            letter = self.var_letter.get().strip().upper()
            if letter not in letters:
                raise ValueError("Обрана літера не входить у поточний варіант.")

            index = letters.index(letter)
            target_bin = patterns_bin[:, index]
            rng = np.random.default_rng(seed)
            s0 = noisy_initial(target_bin, noise, rng)
            recall_result = recall_with_energy_trace(weights, s0, max_sweeps=5000, rng=rng)
            noisy_bin = bipolar_to_bin01(s0)
            recalled_bin = bipolar_to_bin01(recall_result.final_bipolar)
            matched = bool(np.allclose(recalled_bin, target_bin))

            self.summary_var.set(
                f"Triptych для {letter}. Проходів: {recall_result.sweeps}, "
                f"збіжність: {'так' if recall_result.converged else 'ні'}, "
                f"збіг з еталоном: {'так' if matched else 'ні'}."
            )
            self._set_metrics(
                "Режим", "Triptych",
                "Літери", ", ".join(letters),
                "Підсумок", "Збіг" if matched else "Немає збігу",
            )
            self._clear_table()
            self._add_table_row("Літера", letter, "Еталон")
            self._add_table_row("Шум σ", f"{noise:.2f}", "Рівень спотворення")
            self._add_table_row("Проходів", str(recall_result.sweeps), "Асинхронна релаксація")
            self._add_table_row("Збіжність", "Так" if recall_result.converged else "Ні", "")
            self._add_table_row("Збіг", "Так" if matched else "Ні", "Фінальний стан")
            self._draw_triptych_visual(target_bin, noisy_bin, recalled_bin, recall_result.energies, letter, noise)
            self._set_status("Triptych побудовано.")
        except Exception as exc:  # noqa: BLE001
            self._set_status("Помилка побудови triptych.")
            messagebox.showerror("Помилка", str(exc))

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    Lab6GUI().run()


if __name__ == "__main__":
    main()
