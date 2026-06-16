
# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path
import numpy as np

from alphabet import letter_column, load_alphabet
from hopfield import bin01_to_bipolar, bipolar_to_bin01, train_weights, noisy_initial, recall_async, recall_with_energy_trace
from plotting import plot_triptych, plot_energy
from variants import get_variant_letters
from main import run_recognition_experiment, run_foreign_letter


def log(message):
    print(message)
    with open("experiments_log.txt", "a", encoding="utf-8") as f:
        f.write(message + "\n")


def main():
    # Clear log file
    with open("experiments_log.txt", "w", encoding="utf-8") as f:
        pass

    # Configuration
    VARIANT = 1
    NOISE = 0.4
    TRIALS = 50
    SEED = 42
    FOREIGN_LETTER = "V"
    FIGS_DIR = Path("figures")
    FIGS_DIR.mkdir(exist_ok=True)

    log("=== Лабораторная работа 6: Сеть Хопфилда ===\n")

    # 1. Шумовой эксперимент
    log("1. Запуск шумового эксперимента...")
    noise_results = run_recognition_experiment(
        variant=VARIANT,
        noise=NOISE,
        trials=TRIALS,
        seed=SEED,
        alphabet_path=None,
    )
    with open(FIGS_DIR / "noise_results.json", "w", encoding="utf-8") as f:
        json.dump(noise_results, f, ensure_ascii=False, indent=2)
    log(f"   Результаты сохранены в {FIGS_DIR / 'noise_results.json'}")
    log(f"   Вариант {noise_results['variant']}, буквы: {', '.join(noise_results['letters'])}")
    for item in noise_results['per_letter']:
        log(f"   {item['letter']}: точность {item['accuracy']:.3f}, сходимость {item['converged_fraction']:.3f}")
    log("")

    # 2. Чужая буква
    log("2. Запуск эксперимента с чужой буквой...")
    foreign_results = run_foreign_letter(
        variant=VARIANT,
        foreign=FOREIGN_LETTER,
        seed=SEED,
        alphabet_path=None,
    )
    with open(FIGS_DIR / "foreign_results.json", "w", encoding="utf-8") as f:
        json.dump(foreign_results, f, ensure_ascii=False, indent=2)
    log(f"   Результаты сохранены в {FIGS_DIR / 'foreign_results.json'}")
    log(f"   Обученные буквы: {', '.join(foreign_results['trained_letters'])}")
    log(f"   Чужая буква: {foreign_results['foreign_letter']}")
    log(f"   Ближайший эталон: {foreign_results['closest_trained_letter']}")
    log("")

    # 3. Triptychs и энергия для каждой буквы
    log("3. Генерация triptychs и графиков энергии...")
    alphabet = load_alphabet()
    letters = get_variant_letters(VARIANT)
    pats_bin = np.stack([letter_column(alphabet, ch) for ch in letters], axis=1)
    pats_bip = bin01_to_bipolar(pats_bin)
    weights = train_weights(pats_bip)
    rng = np.random.default_rng(SEED)

    for i, letter in enumerate(letters):
        target_bin = pats_bin[:, i]
        noisy_bip = noisy_initial(target_bin, NOISE, rng)
        recall_res = recall_with_energy_trace(weights, noisy_bip, max_sweeps=5000, rng=rng)
        recalled_bin = bipolar_to_bin01(recall_res.final_bipolar)

        # Triptych
        triptych_path = FIGS_DIR / f"triptych_{letter}.png"
        plot_triptych(
            target_bin,
            bipolar_to_bin01(noisy_bip),
            recalled_bin,
            out_path=triptych_path,
            show=False,
            suptitle=f"Вариант {VARIANT}, буква {letter}, шум σ={NOISE}",
        )
        log(f"   Создан triptych: {triptych_path}")

        # Energy
        energy_path = FIGS_DIR / f"energy_{letter}.png"
        plot_energy(
            recall_res.energies,
            out_path=energy_path,
            show=False,
            title=f"Энергия сети для буквы {letter}",
        )
        log(f"   Создан график энергии: {energy_path}")

    log("\n=== Все эксперименты завершены ===")


if __name__ == "__main__":
    main()
