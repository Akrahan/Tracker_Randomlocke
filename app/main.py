import os
import time
from contextlib import asynccontextmanager
from pathlib import Path

import psycopg
from fastapi import FastAPI, Response

DB_HOST = os.environ["DB_HOST"]
DB_USER = os.environ["POSTGRES_USER"]
DB_PASSWORD = os.environ["POSTGRES_PASSWORD"]
DB_NAME = os.environ["POSTGRES_DB"]

SCHEMA = Path(__file__).with_name("schema.sql")


def conectar() -> psycopg.Connection:
    return psycopg.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME,
        connect_timeout=2,
    )


def inicializar_db(intentos: int = 10, espera: int = 2) -> None:
    esquema = SCHEMA.read_text(encoding="utf-8")
    for intento in range(1, intentos + 1):
        try:
            with conectar() as conn:
                conn.execute(esquema)
            return
        except psycopg.Error:
            if intento == intentos:
                raise
            time.sleep(espera)


def comprobar_db() -> bool:
    try:
        with conectar() as conn:
            conn.execute("SELECT 1")
        return True
    except psycopg.Error:
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    inicializar_db()
    yield


app = FastAPI(title="Tracker Randomlocke", lifespan=lifespan)


@app.get("/")
def raiz():
    return {"mensaje": "Tracker Randomlocke funcionando"}


@app.get("/status")
def status(response: Response):
    db_ok = comprobar_db()
    if not db_ok:
        response.status_code = 503
    return {"db": "ok" if db_ok else "down"}
