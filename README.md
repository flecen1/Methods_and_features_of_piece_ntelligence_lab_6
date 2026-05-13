# Лабораторна робота 6 — мережа Хопфілда (Python)

Проєкт для практичної роботи з курсу M&SAI: дискретна мережа Хопфілда, літери A–Z (вектор 35 пікселів), консоль (`main.py`) і графічний інтерфейс (`gui.py`).

## Репозиторій

https://github.com/flecen1/Methods_and_features_of_piece_ntelligence_lab_6

```powershell
cd $env:USERPROFILE\Desktop
git clone https://github.com/flecen1/Methods_and_features_of_piece_ntelligence_lab_6.git
cd Methods_and_features_of_piece_ntelligence_lab_6
```

Без Git: на сторінці репозиторію **Code → Download ZIP**.

## Встановлення

```powershell
cd $env:USERPROFILE\Desktop\Methods_and_features_of_piece_ntelligence_lab_6
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

За потреби для коректного UTF-8 у консолі Windows: `$env:PYTHONUTF8=1`

## Запуск

```powershell
python main.py --help
python main.py --demo-toy --json
python main.py --variant 1 --noise 0.4 --trials 50 --seed 7 --json
python main.py --variant 1 --foreign V --json
mkdir figures
python main.py --variant 1 --plot-triptych B --noise 0.55 --plot-file figures\b.png --plot-energy --no-show
python gui.py
```

Основні параметри: `--variant` (1…20), `--noise`, `--trials`, `--seed`, `--foreign`, `--json`, `--plot-triptych`, `--plot-file`, `--plot-energy`, `--no-show`, `--alphabet` (інший шлях до `Alphabet.csv`).

Варіанти (три літери на варіант) і допоміжні функції — у файлі **`variants.py`**.

## Файли проєкту

| Файл | Роль |
|------|------|
| `main.py` | Запуск з консолі |
| `gui.py` | Вікно з кнопками |
| `hopfield.py` | Мережа (Хебб, релаксація, шум) |
| `alphabet.py` | Читання `Alphabet.csv` |
| `variants.py` | Варіанти 1…20 |
| `plotting.py` | Малюнки 7×5, triptych, енергія |
| `Alphabet.csv` | Шаблони літер |
| `build_alphabet_from_glcdfont.py` | За потреби знову зібрати `Alphabet.csv` (потрібен Інтернет) |

## Примітка про `--demo-toy`

Для малого прикладу (2 нейрони, 4 образи) у коді **не** обнуляється діагональ матриці ваг — інакше `W` стала б нульовою. Для літер (35 нейронів) діагональ обнуляється як зазвичай.

Зміст завдання, варіанти й оформлення звіту — за методичними вказівками викладача.
