import os, time
from contextlib import contextmanager

import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="DataMart - Top 10 productos por ingreso")


def conectar():
    for _ in range(10):
        try:
            return psycopg2.connect(
                host="db",  # nombre del servicio en docker compose
                dbname=os.environ["POSTGRES_DB"],
                user=os.environ["POSTGRES_USER"],
                password=os.environ["POSTGRES_PASSWORD"],
            )
        except psycopg2.OperationalError:
            time.sleep(2)
    raise RuntimeError("No hay conexion a la base de datos")


@contextmanager
def cursor():
    con = conectar()
    try:
        with con, con.cursor() as cur:  # commit/rollback automatico
            yield cur
    finally:
        con.close()


@app.on_event("startup")
def inicio():
    with cursor() as cur:
        cur.execute("""CREATE TABLE IF NOT EXISTS top_productos (
            producto TEXT PRIMARY KEY, ingreso NUMERIC(16,2) NOT NULL)""")


class Resultado(BaseModel):
    producto: str
    ingreso: float


class Ingreso(BaseModel):
    ingreso: float


def _fila(producto, ingreso):
    return {"producto": producto, "ingreso": float(ingreso)}


@app.get("/")
def salud():
    return {"estado": "ok"}


@app.get("/resultados")
def listar():
    with cursor() as cur:
        cur.execute("SELECT producto, ingreso FROM top_productos ORDER BY ingreso DESC")
        return [_fila(*f) for f in cur.fetchall()]


@app.get("/top")
def top():
    with cursor() as cur:
        cur.execute(
            "SELECT producto, ingreso FROM top_productos ORDER BY ingreso DESC LIMIT 10"
        )
        return [_fila(*f) for f in cur.fetchall()]


@app.get("/resultados/{clave}")
def uno(clave: str):
    with cursor() as cur:
        cur.execute(
            "SELECT producto, ingreso FROM top_productos WHERE producto = %s", (clave,)
        )
        fila = cur.fetchone()
    if not fila:
        raise HTTPException(404, "No encontrado")
    return _fila(*fila)


@app.post("/resultados", status_code=201)
def agregar(r: Resultado):
    with cursor() as cur:
        cur.execute(
            """INSERT INTO top_productos VALUES (%s, %s)
                       ON CONFLICT (producto) DO UPDATE SET ingreso = EXCLUDED.ingreso""",
            (r.producto, r.ingreso),
        )
    return {"guardado": r.producto}


@app.put("/resultados/{clave}")
def actualizar(clave: str, d: Ingreso):
    with cursor() as cur:
        cur.execute(
            "UPDATE top_productos SET ingreso = %s WHERE producto = %s",
            (d.ingreso, clave),
        )
        if cur.rowcount == 0:
            raise HTTPException(404, "No encontrado")
    return {"actualizado": clave}


@app.delete("/resultados/{clave}")
def borrar(clave: str):
    with cursor() as cur:
        cur.execute("DELETE FROM top_productos WHERE producto = %s", (clave,))
        if cur.rowcount == 0:
            raise HTTPException(404, "No encontrado")
    return {"eliminado": clave}
