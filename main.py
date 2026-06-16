# -*- coding: utf-8 -*-
"""
Лабораторна робота 6 — мережа Хопфілда (Python).

Приклади:
  python main.py --demo-toy
  python main.py --variant 1 --noise 0.4 --trials 30 --json
  python main.py --variant 1 --foreign V --json
  python main.py --variant 1 --plot-triptych B --noise 0.6 --plot-file out/b.png --no-show
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Optional

import numpy as np

from alphabet import letter_column, load_alphabet
from hopfield import (
    bin01_to_bipolar,
    bipolar_to_bin01,
    noisy_initial,
    recall_async,
    recall_with_energy_trace,
    train_weights,
)
from plotting import plot_energy, plot_triptych
from variants import get_variant_letters


def _rng(seed: Optional[int]) -> np.random.Generator:
    return np.random.default_rng(seed)


def _bipolar_match(a: np.ndarray, b: np.ndarray) -> bool:
    return bool(np.all(np.sign(a) == np.sign(b)))


def demo_toy() -> dict:
    """
    Приклад: 2 нейрони, 4 біполярні образи (кути квадрата), матриця 2×4.

    Для цього набору класичне обнулення діагоналі дає W=0, тому тут використовуємо zero_diagonal=False
    (зберігаємо діагональні зв’язки), щоб мережа не була тривіальною.
    """
    t1 = np.array(
        [
            [1.0, -1.0, 1.0, -1.0],
            [-1.0, 1.0, 1.0, -1.0],
        ],
        dtype=float,
    )
    w = train_weights(t1, zero_diagonal=False)
    # перевірка, що еталонні стовпці — атрактори (1 крок асинхрону вже стабільні)
    stable = []
    for k in range(t1.shape[1]):
        col = t1[:, k].copy()
        s, sweeps, conv = recall_async(w, col, max_sweeps=50, rng=np.random.default_rng(0))
        stable.append(
            {
                "pattern_index": k + 1,
                "target": col.tolist(),
                "final": s.tolist(),
                "sweeps": sweeps,
                "converged": conv,
                "matches_target": _bipolar_match(s, col),
            }
        )
    return {"weights": w.tolist(), "stability_check": stable}


def run_recognition_experiment(
    *,
    variant: int,
    noise: float,
    trials: int,
    seed: Optional[int],
    alphabet_path: Optional[Path],
) -> dict:
    alphabet = load_alphabet(alphabet_path)
    letters = get_variant_letters(variant)
    pats_bin = np.stack([letter_column(alphabet, ch) for ch in letters], axis=1)
    pats_bip = bin01_to_bipolar(pats_bin)
    w = train_weights(pats_bip)
    rng = _rng(seed)

    per_letter: List[dict] = []
    for li, ch in enumerate(letters):
        target_bin = pats_bin[:, li]
        target_bip = pats_bip[:, li]
        successes = 0
        convs = 0
        for _ in range(trials):
            s0 = noisy_initial(target_bin, noise, rng)
            s, _sw, conv = recall_async(w, s0, max_sweeps=5000, rng=rng)
            if conv:
                convs += 1
            # успіх: збіг з еталоном цієї літери
            if _bipolar_match(s, target_bip):
                successes += 1
        per_letter.append(
            {
                "letter": ch,
                "accuracy": successes / float(trials),
                "converged_fraction": convs / float(trials),
                "noise_sigma": noise,
                "trials": trials,
            }
        )
    return {
        "variant": variant,
        "letters": list(letters),
        "noise_sigma": noise,
        "trials": trials,
        "per_letter": per_letter,
    }


def run_foreign_letter(
    *,
    variant: int,
    foreign: str,
    seed: Optional[int],
    alphabet_path: Optional[Path],
) -> dict:
    alphabet = load_alphabet(alphabet_path)
    letters = get_variant_letters(variant)
    foreign = foreign.strip().upper()
    if foreign in letters:
        raise ValueError("Чужа літера не повинна збігатися з навчальними літерами варіанту.")
    pats_bin = np.stack([letter_column(alphabet, ch) for ch in letters], axis=1)
    pats_bip = bin01_to_bipolar(pats_bin)
    w = train_weights(pats_bip)
    rng = _rng(seed)

    fcol = letter_column(alphabet, foreign)
    fbip = bin01_to_bipolar(fcol)
    s, sweeps, conv = recall_async(w, fbip, max_sweeps=5000, rng=rng)
    s_bin = bipolar_to_bin01(s)

    # найближчий еталон за відстанню Геммінга у біполярному просторі
    dists = [int(np.sum(np.sign(s) != np.sign(pats_bip[:, i]))) for i in range(3)]
    best_i = int(np.argmin(dists))
    return {
        "variant": variant,
        "trained_letters": list(letters),
        "foreign_letter": foreign,
        "final_bipolar": s.tolist(),
        "sweeps": sweeps,
        "converged": conv,
        "closest_trained_letter": letters[best_i],
        "hamming_bipolar_to_trained": dists,
        "final_binary_preview": np.round(s_bin, 3).tolist(),
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Лаб. 6 — мережа Хопфілда (Python)")
    p.add_argument("--demo-toy", action="store_true", help="Демо: 2 нейрони, 4 біполярні образи")
    p.add_argument("--variant", type=int, default=None, help="Номер варіанту 1..20 (табл. 7.1)")
    p.add_argument("--alphabet", type=str, default=None, help="Шлях до Alphabet.csv")
    p.add_argument("--noise", type=float, default=0.4, help="Сила гаусового шуму (як randn*sigma)")
    p.add_argument("--trials", type=int, default=40, help="Кількість випадкових спотворень на літеру")
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--foreign", type=str, default=None, help="Літера поза навчальною вибіркою (напр. V)")
    p.add_argument("--json", action="store_true")
    p.add_argument("--plot-triptych", type=str, default=None, help="Побудувати 3 панелі для літери з варіанту")
    p.add_argument("--plot-file", type=str, default=None)
    p.add_argument("--plot-energy", action="store_true", help="Графік енергії для triptych")
    p.add_argument("--no-show", action="store_true")
    args = p.parse_args()

    alphabet_path = Path(args.alphabet) if args.alphabet else None

    if args.demo_toy:
        out = demo_toy()
        if args.json:
            print(json.dumps(out, ensure_ascii=False, indent=2))
        else:
            print("Демо (2 нейрони, 4 образи). Матриця ваг W:")
            for row in out["weights"]:
                print(" ", " ".join(f"{v:8.4f}" for v in row))
            print("Перевірка стабільності еталонів:")
            for row in out["stability_check"]:
                print(row)
        return

    if args.variant is None:
        raise SystemExit("Вкажіть --variant 1..20 або використайте --demo-toy.")

    if args.foreign:
        out = run_foreign_letter(
            variant=args.variant,
            foreign=args.foreign,
            seed=args.seed,
            alphabet_path=alphabet_path,
        )
        if args.json:
            print(json.dumps(out, ensure_ascii=False, indent=2))
        else:
            print("Навчені:", ", ".join(out["trained_letters"]))
            print("Чужа літера:", out["foreign_letter"])
            print("Найближчий еталон:", out["closest_trained_letter"], "геммінг:", out["hamming_bipolar_to_trained"])
            print("Збіжність:", out["converged"], "проходів:", out["sweeps"])
        return

    exp = run_recognition_experiment(
        variant=args.variant,
        noise=args.noise,
        trials=args.trials,
        seed=args.seed,
        alphabet_path=alphabet_path,
    )

    if args.plot_triptych:
        ch = args.plot_triptych.strip().upper()
        letters = tuple(exp["letters"])
        if ch not in letters:
            raise SystemExit(f"Літера {ch} не з варіанту {letters}")
        alphabet = load_alphabet(alphabet_path)
        pats_bin = np.stack([letter_column(alphabet, x) for x in letters], axis=1)
        pats_bip = bin01_to_bipolar(pats_bin)
        w = train_weights(pats_bip)
        rng = _rng(args.seed)
        li = letters.index(ch)
        target_bin = pats_bin[:, li]
        s0 = noisy_initial(target_bin, args.noise, rng)
        recall_res = recall_with_energy_trace(w, s0, max_sweeps=5000, rng=rng)
        s_bin = bipolar_to_bin01(recall_res.final_bipolar)
        out_p = Path(args.plot_file) if args.plot_file else None
        plot_triptych(
            target_bin,
            bipolar_to_bin01(s0),
            s_bin,
            out_path=out_p,
            show=not args.no_show,
            suptitle=f"Варіант {args.variant}, літера {ch}, шум σ={args.noise}",
        )
        if args.plot_energy:
            pe = out_p.with_name(out_p.stem + "_energy.png") if out_p else None
            plot_energy(recall_res.energies, out_path=pe, show=not args.no_show)

    if args.json:
        print(json.dumps(exp, ensure_ascii=False, indent=2))
    else:
        print("Варіант", exp["variant"], "літери:", ", ".join(exp["letters"]))
        print("Шум σ =", exp["noise_sigma"], "випробувань на літеру:", exp["trials"])
        for row in exp["per_letter"]:
            print(
                f"  {row['letter']}: точність {row['accuracy']:.3f}, "
                f"частка збіжностей {row['converged_fraction']:.3f}"
            )


if __name__ == "__main__":
    main()
