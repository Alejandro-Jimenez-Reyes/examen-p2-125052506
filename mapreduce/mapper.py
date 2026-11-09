#!/usr/bin/env python3
import sys

for linea in sys.stdin:
    campos = linea.rstrip("\n").split(",")
    if len(campos) != 8 or campos[0] == "id":  # salta encabezado y líneas malformadas
        continue
    try:
        ingreso = int(campos[5]) * float(campos[6])  # cantidad * precio_unitario
    except ValueError:
        continue
    print(f"{campos[4]}\t{ingreso:.2f}")  # producto \t ingreso
