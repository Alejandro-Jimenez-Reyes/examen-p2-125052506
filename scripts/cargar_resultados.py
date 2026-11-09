import os, sys
import psycopg2

ruta = sys.argv[1] if len(sys.argv) > 1 else "/salida/top10.tsv"
con = psycopg2.connect(
    host="db",
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
)
with con, con.cursor() as cur:
    cur.execute("""CREATE TABLE IF NOT EXISTS top_productos (
        producto TEXT PRIMARY KEY, ingreso NUMERIC(16,2) NOT NULL)""")
    with open(ruta) as f:
        for linea in f:
            producto, ingreso = linea.strip().split("\t")
            cur.execute(
                """INSERT INTO top_productos VALUES (%s, %s)
                           ON CONFLICT (producto) DO UPDATE SET ingreso = EXCLUDED.ingreso""",
                (producto, float(ingreso)),
            )
print("Resultados cargados")
