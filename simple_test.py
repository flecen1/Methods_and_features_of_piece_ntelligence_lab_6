
# -*- coding: utf-8 -*-
import sys

with open("test_log.txt", "w", encoding="utf-8") as f:
    f.write("Hello from simple_test.py!\n")

    try:
        import numpy as np
        f.write("NumPy imported successfully\n")
    except Exception as e:
        f.write(f"Error importing NumPy: {e}\n")
        sys.exit(1)

    try:
        from alphabet import load_alphabet
        f.write("alphabet.py imported successfully\n")
    except Exception as e:
        f.write(f"Error importing alphabet: {e}\n")
        sys.exit(1)

    try:
        alphabet = load_alphabet()
        f.write(f"Alphabet loaded, shape: {alphabet.shape}\n")
    except Exception as e:
        f.write(f"Error loading alphabet: {e}\n")
        sys.exit(1)

    f.write("Simple test passed!\n")
