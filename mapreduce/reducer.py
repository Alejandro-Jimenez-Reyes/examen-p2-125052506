#!/usr/bin/env python3
import sys

actual = None
total = 0.0

for linea in sys.stdin:
    try:
        producto, valor = linea.rstrip("\n").split("\t")
        valor = float(valor)
    except ValueError:
        continue
    if producto != actual:
        if actual is not None:
            print(f"{actual}\t{total:.2f}")
        actual = producto
        total = 0.0
    total += valor

if actual is not None:
    print(f"{actual}\t{total:.2f}")
