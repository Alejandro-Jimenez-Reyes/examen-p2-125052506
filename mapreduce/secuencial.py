#!/usr/bin/env python3
import csv, sys, time

ruta = sys.argv[1] if len(sys.argv) > 1 else "/data/ventas_125052506.csv"
inicio = time.time()

totales = {}
with open(ruta, newline="") as f:
    lector = csv.reader(f)
    next(lector)  # salta encabezado
    for fila in lector:
        try:
            ingreso = int(fila[5]) * float(fila[6])
        except (ValueError, IndexError):
            continue
        totales[fila[4]] = totales.get(fila[4], 0.0) + ingreso

top10 = sorted(totales.items(), key=lambda x: x[1], reverse=True)[:10]
for producto, total in top10:
    print(f"{producto}\t{total:.2f}")

print(f"Tiempo secuencial: {time.time() - inicio:.1f} s", file=sys.stderr)
