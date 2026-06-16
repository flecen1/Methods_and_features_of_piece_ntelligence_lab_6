# Лабораторна робота 6 — мережа Хопфілда (Python)

Проєкт для практичної роботи з курсу M&SAI: дискретна мережа Хопфілда, літери A–Z (вектор 35 пікселів), консольний інтерфейс (`main.py`) і графічний інтерфейс (`gui.py`).

## Що містить проєкт

- `main.py` — запуск експериментів і базових сценаріїв з командного рядка
- `gui.py` — інтерфейс для перегляду результатів і параметрів
- `hopfield.py` — реалізація мережі Хопфілда, навчання та релаксація
- `alphabet.py` і `variants.py` — завантаження шаблонів літер і варіантів
- `plotting.py` — побудова зображень станів і графіків енергії
- `run_experiments.py` — скрипт для запуску набору експериментів
- `Alphabet.csv` — шаблони літер для роботи

## Встановлення

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Запуск

```powershell
python main.py --help
python main.py --demo-toy --json
python main.py --variant 1 --noise 0.4 --trials 50 --seed 7 --json
python main.py --variant 1 --foreign V --json
python main.py --variant 1 --plot-triptych B --noise 0.55 --plot-file figures\b.png --plot-energy --no-show
python gui.py
```

## Примітка про `--demo-toy`

Для малого прикладу (2 нейрони, 4 образи) у коді не обнуляється діагональ матриці ваг, щоб мережа не зводилася до нуля. Для літер (35 нейронів) діагональ обнуляється як зазвичай.
