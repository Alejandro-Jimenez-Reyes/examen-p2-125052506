import os, time
import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="DataMart Top 10")

def conectar():
    for _ in range(10):
        try:
            return psycopg2.connect(
                host="db",
                dbname=os.environ["POSTGRES_DB"],
                user=os.environ["POSTGRES_USER"],
                password=os.environ["POSTGRES_PASSWORD"],
            )
        except psycopg2.OperationalError:
            time.sleep(2)
    raise RuntimeError("No hay conexion a la base de datos")

def asegurar_tabla():
    con = conectar()
    with con, con.cursor() as cur:
        cur.execute("""CREATE TABLE IF NOT EXISTS top_productos (
            producto TEXT PRIMARY KEY, ingreso NUMERIC(16,2) NOT NULL)""")
    con.close()

@app.on_event("startup")
def inicio():
    asegurar_tabla()

class Producto(BaseModel):
    producto: str
    ingreso: float

@app.get("/")
def salud():
    return {"estado": "ok"}

@app.get("/top")
def top():
    con = conectar()
    with con, con.cursor() as cur:
        cur.execute("SELECT producto, ingreso FROM top_productos ORDER BY ingreso DESC LIMIT 10")
        filas = cur.fetchall()
    con.close()
    return [{"producto": p, "ingreso": float(i)} for p, i in filas]

@app.get("/producto/{codigo}")
def uno(codigo: str):
    con = conectar()
    with con, con.cursor() as cur:
        cur.execute("SELECT producto, ingreso FROM top_productos WHERE producto = %s", (codigo,))
        fila = cur.fetchone()
    con.close()
    if not fila:
        raise HTTPException(404, "No encontrado")
    return {"producto": fila[0], "ingreso": float(fila[1])}

@app.post("/producto")
def agregar(p: Producto):
    con = conectar()
    with con, con.cursor() as cur:
        cur.execute("""INSERT INTO top_productos VALUES (%s, %s)
                       ON CONFLICT (producto) DO UPDATE SET ingreso = EXCLUDED.ingreso""",
                    (p.producto, p.ingreso))
    con.close()
    return {"guardado": p.producto}
