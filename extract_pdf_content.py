# -*- coding: utf-8 -*-
"""
Скрипт для витягнення тексту з PDF файлів для створення методичних вказівок
"""

import sys
from pathlib import Path

def install_and_import(package):
    """Встановлює пакет, якщо він не встановлений"""
    try:
        __import__(package)
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    finally:
        globals()[package] = __import__(package)

# Встановлюємо pdfplumber
install_and_import("pdfplumber")


def extract_text_from_pdf(pdf_path, output_txt_path):
    """Витягує текст з PDF файлу та зберігає його в текстовий файл"""
    print(f"Обробка: {pdf_path}")
    
    if not Path(pdf_path).exists():
        print(f"ПОМИЛКА: Файл {pdf_path} не знайдено!")
        return None
    
    extracted_text = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Кількість сторінок: {len(pdf.pages)}")
            
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    extracted_text.append(f"\n{'='*60}")
                    extracted_text.append(f"СТОРІНКА {i+1}")
                    extracted_text.append(f"{'='*60}\n")
                    extracted_text.append(text)
                    extracted_text.append("\n")
        
        # Зберігаємо результат
        full_text = "\n".join(extracted_text)
        
        with open(output_txt_path, "w", encoding="utf-8") as f:
            f.write(full_text)
        
        print(f"Текст збережено в: {output_txt_path}")
        return full_text
        
    except Exception as e:
        print(f"ПОМИЛКА при обробці {pdf_path}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def main():
    # Витягуємо текст з обох PDF файлів
    files_to_process = [
        ("Bachelor_M&SAI_LAB_6_25.pdf", "bachelor_lab6_full.txt"),
        ("Methodical_ДУІКТ_Lab7_GA_Python_Петренко_Ярослав_Олексійович_КНД-31.pdf", "methodical_lab7_full.txt"),
    ]
    
    for pdf_file, txt_file in files_to_process:
        extract_text_from_pdf(pdf_file, txt_file)
        print("-" * 60)
    
    print("\nГотово! Перевірте файли:")
    for _, txt_file in files_to_process:
        if Path(txt_file).exists():
            print(f"  ✓ {txt_file}")


if __name__ == "__main__":
    main()
