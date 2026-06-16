
# -*- coding: utf-8 -*-
import PyPDF2
from pathlib import Path


def extract_pdf_text(pdf_path):
    print(f"Extracting text from {pdf_path}...")
    text = ""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for i, page in enumerate(reader.pages):
            text += f"\n--- Page {i+1} ---\n"
            text += page.extract_text() or ""
    return text


def main():
    pdf1 = Path("Bachelor_M&SAI_LAB_6_25.pdf")
    pdf2 = Path("Methodical_ДУІКТ_Lab7_GA_Python_Петренко_Ярослав_Олексійович_КНД-31.pdf")

    if pdf1.exists():
        text1 = extract_pdf_text(pdf1)
        with open("bachelor_lab6_text.txt", "w", encoding="utf-8") as f:
            f.write(text1)
        print(f"Text saved to bachelor_lab6_text.txt")

    if pdf2.exists():
        text2 = extract_pdf_text(pdf2)
        with open("methodical_lab7_text.txt", "w", encoding="utf-8") as f:
            f.write(text2)
        print(f"Text saved to methodical_lab7_text.txt")


if __name__ == "__main__":
    main()
