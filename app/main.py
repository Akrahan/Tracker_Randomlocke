import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

import psycopg
from fastapi import FastAPI, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from psycopg.rows import dict_row
from pydantic import BaseModel, ConfigDict, Field


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
        row_factory=dict_row,
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


def existe_run(conn, run_id: int) -> None:
    if conn.execute("SELECT 1 FROM runs WHERE id = %s", (run_id,)).fetchone() is None:
        raise HTTPException(status_code=404, detail="La partida no existe")


@asynccontextmanager
async def lifespan(app: FastAPI):
    inicializar_db()
    yield


app = FastAPI(title="Tracker Randomlocke", lifespan=lifespan)


@app.get("/status")
def status(response: Response):
    db_ok = comprobar_db()
    if not db_ok:
        response.status_code = 503
    return {"db": "ok" if db_ok else "down"}


class RunNueva(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)


@app.post("/runs", status_code=201)
def crear_run(run: RunNueva):
    with conectar() as conn:
        return conn.execute(
            "INSERT INTO runs (name) VALUES (%s) RETURNING id, name, created_at",
            (run.name,),
        ).fetchone()


class EventoNuevo(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    event_type: Literal["captura", "fallo", "muerte"]
    route: str = Field(min_length=1, max_length=100)
    species: str = Field(min_length=1, max_length=100)


@app.post("/runs/{run_id}/events", status_code=201)
def registrar_evento(run_id: int, evento: EventoNuevo):
    with conectar() as conn:
        existe_run(conn, run_id)

        previos = {
            fila["event_type"]
            for fila in conn.execute(
                "SELECT event_type FROM encounters WHERE run_id = %s AND route = %s",
                (run_id, evento.route),
            )
        }

        if evento.event_type in ("captura", "fallo") and previos & {"captura", "fallo"}:
            raise HTTPException(status_code=409, detail="Esa ruta ya tiene un resultado de primer encuentro")
        if evento.event_type == "muerte" and "captura" not in previos:
            raise HTTPException(status_code=409, detail="No hay ninguna captura en esa ruta")
        if evento.event_type == "muerte" and "muerte" in previos:
            raise HTTPException(status_code=409, detail="El Pokémon de esa ruta ya murió")

        try:
            return conn.execute(
                "INSERT INTO encounters (run_id, event_type, route, species) "
                "VALUES (%s, %s, %s, %s) "
                "RETURNING id, run_id, event_type, route, species, created_at",
                (run_id, evento.event_type, evento.route, evento.species),
            ).fetchone()
        except psycopg.errors.UniqueViolation:
            raise HTTPException(status_code=409, detail="Evento duplicado")


@app.get("/runs")
def listar_runs():
    with conectar() as conn:
        return conn.execute(
            "SELECT id, name, created_at FROM runs ORDER BY id DESC"
        ).fetchall()


@app.get("/runs/{run_id}/encounters")
def listar_eventos(run_id: int):
    with conectar() as conn:
        existe_run(conn, run_id)
        return conn.execute(
            "SELECT id, event_type, route, species, created_at "
            "FROM encounters WHERE run_id = %s ORDER BY id",
            (run_id,),
        ).fetchall()


@app.get("/runs/{run_id}/team")
def equipo_activo(run_id: int):
    with conectar() as conn:
        existe_run(conn, run_id)
        return conn.execute(
            "SELECT c.route, c.species, c.created_at "
            "FROM encounters c "
            "WHERE c.run_id = %s AND c.event_type = 'captura' "
            "AND NOT EXISTS (SELECT 1 FROM encounters m "
            "WHERE m.run_id = c.run_id AND m.route = c.route AND m.event_type = 'muerte') "
            "ORDER BY c.created_at",
            (run_id,),
        ).fetchall()


@app.get("/runs/{run_id}/graveyard")
def cementerio(run_id: int):
    with conectar() as conn:
        existe_run(conn, run_id)
        return conn.execute(
            "SELECT c.route, c.species, m.created_at AS muerto_en "
            "FROM encounters c "
            "JOIN encounters m ON m.run_id = c.run_id AND m.route = c.route "
            "AND m.event_type = 'muerte' "
            "WHERE c.run_id = %s AND c.event_type = 'captura' "
            "ORDER BY m.created_at",
            (run_id,),
        ).fetchall()


app.mount("/", StaticFiles(directory=Path(__file__).with_name("static"), html=True), name="static")
