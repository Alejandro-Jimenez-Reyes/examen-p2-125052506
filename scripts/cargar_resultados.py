import os, sys
from decimal import Decimal
import psycopg2

# Lee directamente la salida del job (part-00000) y se queda con el top 10
ruta = sys.argv[1] if len(sys.argv) > 1 else "/salida/job_top10/part-00000"

filas = []
with open(ruta) as f:
    for linea in f:
        try:
            producto, ingreso = linea.rstrip("\n").split("\t")
            filas.append((producto, Decimal(ingreso)))
        except Exception:
            continue

top10 = sorted(filas, key=lambda x: x[1], reverse=True)[:10]

con = psycopg2.connect(
    host="db",
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
)
try:
    with con, con.cursor() as cur:
        cur.execute("""CREATE TABLE IF NOT EXISTS top_productos (
            producto TEXT PRIMARY KEY, ingreso NUMERIC(16,2) NOT NULL)""")
        for producto, ingreso in top10:
            cur.execute(
                """INSERT INTO top_productos VALUES (%s, %s)
                           ON CONFLICT (producto) DO UPDATE SET ingreso = EXCLUDED.ingreso""",
                (producto, ingreso),
            )
finally:
    con.close()

print(f"Cargados {len(top10)} registros desde {ruta}")
for p, i in top10:
    print(f"  {p}\t{i}")
