
# -*- coding: utf-8 -*-
from pathlib import Path


def read_file_safe(file_path):
    for encoding in ["utf-8", "cp1251", "latin-1"]:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    return None


file1 = Path("Bachelor_MSAI_LAB6_extracted.txt")
file2 = Path("Lab7_sample_extracted.txt")

if file1.exists():
    text1 = read_file_safe(file1)
    if text1:
        print("\n--- Bachelor_MSAI_LAB6_extracted.txt ---\n")
        print(text1[:5000])
        with open("bachelor_lab6_clean.txt", "w", encoding="utf-8") as f:
            f.write(text1)

if file2.exists():
    text2 = read_file_safe(file2)
    if text2:
        print("\n--- Lab7_sample_extracted.txt ---\n")
        print(text2[:5000])
        with open("lab7_sample_clean.txt", "w", encoding="utf-8") as f:
            f.write(text2)
