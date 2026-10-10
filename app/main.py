import os

import psycopg
from fastapi import FastAPI, Response

app = FastAPI(title="Tracker Randomlocke")

DB_HOST = os.environ["DB_HOST"]
DB_USER = os.environ["POSTGRES_USER"]
DB_PASSWORD = os.environ["POSTGRES_PASSWORD"]
DB_NAME = os.environ["POSTGRES_DB"]


def comprobar_db() -> bool:
    try:
        with psycopg.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME,
            connect_timeout=2,
        ) as conn:
            conn.execute("SELECT 1")
        return True
    except psycopg.Error:
        return False


@app.get("/")
def raiz():
    return {"mensaje": "Tracker Randomlocke funcionando"}


@app.get("/status")
def status(response: Response):
    db_ok = comprobar_db()
    if not db_ok:
        response.status_code = 503
    return {"db": "ok" if db_ok else "down"}
