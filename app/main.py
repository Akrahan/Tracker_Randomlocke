import csv
import json
import mimetypes
import os
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Literal

import psycopg
import redis
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from pydantic import BaseModel, ConfigDict, Field
from redis.backoff import NoBackoff
from redis.retry import Retry


DB_HOST = os.environ["DB_HOST"]
DB_USER = os.environ["POSTGRES_USER"]
DB_PASSWORD = os.environ["POSTGRES_PASSWORD"]
DB_NAME = os.environ["POSTGRES_DB"]
CACHE_ENABLED = os.environ.get("CACHE_ENABLED", "false").lower() == "true"
CACHE_HOST = os.environ.get("CACHE_HOST", "cache")
CACHE_PASSWORD = os.environ.get("REDIS_PASSWORD")
ENABLE_DOCS = os.environ.get("ENABLE_DOCS", "false").lower() == "true"

# La imagen slim no conoce .woff2: sin esto, las tipografías se servirían como application/octet-stream.
mimetypes.add_type("font/woff2", ".woff2")

cache = (
    redis.Redis(
        host=CACHE_HOST,
        password=CACHE_PASSWORD,
        socket_connect_timeout=1,
        socket_timeout=1,
        retry=Retry(NoBackoff(), 0),
        decode_responses=True,
    )
    if CACHE_ENABLED
    else None
)

CACHE_VIGILANCIA_S = 3
CACHE_EQUIPO_TTL_S = 30
CACHE_ESPECIES_TTL_S = 3600
cache_estado = "ok" if CACHE_ENABLED else "no aplica"

SCHEMA = Path(__file__).with_name("schema.sql")
SPECIES = Path(__file__).with_name("species.csv")
TYPES = Path(__file__).with_name("types.csv")
SPECIES_TYPES = Path(__file__).with_name("species_types.csv")

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
                cargar_especies(conn)
                cargar_tipos(conn)
            return
        except psycopg.Error:
            if intento == intentos:
                raise
            time.sleep(espera)


def cargar_especies(conn: psycopg.Connection) -> None:
    with SPECIES.open(encoding="utf-8", newline="") as fichero:
        filas = [(int(fila["id"]), fila["name"]) for fila in csv.DictReader(fichero)]
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO species (id, name) VALUES (%s, %s) "
            "ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name",
            filas,
        )


def cargar_tipos(conn: psycopg.Connection) -> None:
    with TYPES.open(encoding="utf-8", newline="") as fichero:
        tipos = [(int(f["id"]), f["identifier"], f["name"]) for f in csv.DictReader(fichero)]
    with SPECIES_TYPES.open(encoding="utf-8", newline="") as fichero:
        relaciones = [(int(f["species_id"]), int(f["type_id"]), int(f["slot"])) for f in csv.DictReader(fichero)]
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO types (id, identifier, name) VALUES (%s, %s, %s) "
            "ON CONFLICT (id) DO UPDATE SET identifier = EXCLUDED.identifier, name = EXCLUDED.name",
            tipos,
        )
        cur.executemany(
            "INSERT INTO species_types (species_id, type_id, slot) VALUES (%s, %s, %s) "
            "ON CONFLICT (species_id, slot) DO UPDATE SET type_id = EXCLUDED.type_id",
            relaciones,
        )


def comprobar_db() -> bool:
    try:
        with conectar() as conn:
            conn.execute("SELECT 1")
        return True
    except psycopg.Error:
        return False


def vigilar_cache() -> None:
    global cache_estado
    while True:
        try:
            cache.ping()
            cache_estado = "ok"
        except redis.RedisError:
            cache_estado = "caida"
        time.sleep(CACHE_VIGILANCIA_S)


def marcar_cache_caida() -> None:
    global cache_estado
    cache_estado = "caida"


def comprobar_cache() -> str:
    return cache_estado


# Columnas de especie para una captura "c": su número de Pokédex (para el dibujo) y sus tipos.
# La especie se escribe como texto en la captura, así que se busca por nombre (sin distinguir mayúsculas);
# si el nombre no está en la lista (forma rara de un randomizer), species_id y types salen null.
COLUMNAS_ESPECIE = (
    "(SELECT s.id FROM species s WHERE lower(s.name) = lower(c.species)) AS species_id, "
    "(SELECT json_agg(json_build_object('identifier', t.identifier, 'name', t.name) ORDER BY st.slot) "
    "FROM species s JOIN species_types st ON st.species_id = s.id JOIN types t ON t.id = st.type_id "
    "WHERE lower(s.name) = lower(c.species)) AS types"
)


def escapar_like(texto: str) -> str:
    return texto.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def existe_run(conn, run_id: int) -> None:
    if conn.execute("SELECT 1 FROM runs WHERE id = %s", (run_id,)).fetchone() is None:
        raise HTTPException(status_code=404, detail="La partida no existe")


def leer_con_cache(clave: str, ttl_s: int, consultar):
    estado = "OFF"

    if cache is not None:
        if cache_estado != "ok":
            estado = "DEGRADED"
        else:
            try:
                crudo = cache.get(clave)
                if crudo is not None:
                    return json.loads(crudo), "HIT", cache.ttl(clave)
                estado = "MISS"
            except redis.RedisError:
                marcar_cache_caida()
                estado = "DEGRADED"

    datos = consultar()

    ttl = None
    if estado == "MISS":
        try:
            cache.set(clave, json.dumps(datos), ex=ttl_s)
            ttl = ttl_s
        except redis.RedisError:
            marcar_cache_caida()
            estado = "DEGRADED"

    return datos, estado, ttl


def poner_cabeceras_cache(response: Response, estado: str, ttl, inicio: float) -> None:
    response.headers["X-Cache"] = estado
    if ttl is not None and ttl >= 0:
        response.headers["X-Cache-TTL"] = str(ttl)
    response.headers["X-Latency-Ms"] = f"{(time.perf_counter() - inicio) * 1000:.1f}"


def leer_equipo(run_id: int):
    def consultar():
        with conectar() as conn:
            existe_run(conn, run_id)
            return jsonable_encoder(
                conn.execute(
                    "SELECT c.route, c.species, c.details->>'nickname' AS nickname, c.created_at, "
                    + COLUMNAS_ESPECIE + " "
                    "FROM encounters c "
                    "WHERE c.run_id = %s AND c.event_type = 'captura' "
                    "AND NOT EXISTS (SELECT 1 FROM encounters m "
                    "WHERE m.run_id = c.run_id AND m.route = c.route AND m.event_type = 'muerte') "
                    "ORDER BY c.created_at",
                    (run_id,),
                ).fetchall()
            )

    return leer_con_cache(f"team:{run_id}", CACHE_EQUIPO_TTL_S, consultar)


def leer_especies(prefijo: str, limit: int):
    def consultar():
        with conectar() as conn:
            filas = conn.execute(
                "SELECT name FROM species WHERE lower(name) LIKE %s ORDER BY name LIMIT %s",
                (escapar_like(prefijo) + "%", limit),
            ).fetchall()
        return [fila["name"] for fila in filas]

    return leer_con_cache(f"species:{prefijo}:{limit}", CACHE_ESPECIES_TTL_S, consultar)


def invalidar_equipo(run_id: int) -> None:
    if cache is None:
        return
    try:
        cache.delete(f"team:{run_id}")
    except redis.RedisError:
        marcar_cache_caida()


@asynccontextmanager
async def lifespan(app: FastAPI):
    inicializar_db()
    if cache is not None:
        threading.Thread(target=vigilar_cache, daemon=True).start()
    yield


app = FastAPI(
    title="Tracker Randomlocke",
    lifespan=lifespan,
    docs_url="/docs" if ENABLE_DOCS else None,
    redoc_url="/redoc" if ENABLE_DOCS else None,
    openapi_url="/openapi.json" if ENABLE_DOCS else None,
)


@app.get("/status")
def status(response: Response):
    db_ok = comprobar_db()
    cache_estado = comprobar_cache()
    if not db_ok:
        response.status_code = 503
        estado = "down"
    elif cache_estado == "caida":
        estado = "degraded"
    else:
        estado = "ok"
    return {"estado": estado, "db": "ok" if db_ok else "down", "cache": cache_estado}


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
    nickname: str | None = Field(default=None, max_length=20)


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

        detalles = None
        if evento.event_type == "captura" and evento.nickname:
            detalles = Jsonb({"nickname": evento.nickname})

        try:
            fila = conn.execute(
                "INSERT INTO encounters (run_id, event_type, route, species, details) "
                "VALUES (%s, %s, %s, %s, %s) "
                "RETURNING id, run_id, event_type, route, species, created_at",
                (run_id, evento.event_type, evento.route, evento.species, detalles),
            ).fetchone()
        except psycopg.errors.UniqueViolation:
            raise HTTPException(status_code=409, detail="Evento duplicado")

    invalidar_equipo(run_id)
    return fila


VIVO = (
    "NOT EXISTS (SELECT 1 FROM encounters m WHERE m.run_id = c.run_id "
    "AND m.route = c.route AND m.event_type = 'muerte')"
)


@app.get("/runs")
def listar_runs():
    # Una sola consulta con todo lo que necesita la portada: contadores y el equipo de cada partida.
    with conectar() as conn:
        return conn.execute(
            "SELECT r.id, r.name, r.created_at, "
            "(SELECT count(*) FROM encounters c WHERE c.run_id = r.id "
            "AND c.event_type = 'captura' AND " + VIVO + ") AS alive, "
            "(SELECT count(*) FROM encounters c WHERE c.run_id = r.id AND c.event_type = 'muerte') AS dead, "
            "COALESCE((SELECT json_agg(json_build_object("
            "'species_id', (SELECT s.id FROM species s WHERE lower(s.name) = lower(c.species)), "
            "'species', c.species, 'alive', " + VIVO + ") ORDER BY p.position) "
            "FROM party p JOIN encounters c ON c.run_id = p.run_id AND c.route = p.route "
            "AND c.event_type = 'captura' WHERE p.run_id = r.id), '[]'::json) AS party "
            "FROM runs r ORDER BY r.id DESC"
        ).fetchall()


@app.get("/runs/{run_id}/encounters")
def listar_eventos(run_id: int):
    with conectar() as conn:
        existe_run(conn, run_id)
        return conn.execute(
            "SELECT id, event_type, route, species, details->>'nickname' AS nickname, created_at "
            "FROM encounters WHERE run_id = %s ORDER BY id",
            (run_id,),
        ).fetchall()


@app.get("/runs/{run_id}/team")
def equipo_activo(run_id: int, response: Response):
    inicio = time.perf_counter()
    datos, estado, ttl = leer_equipo(run_id)
    poner_cabeceras_cache(response, estado, ttl, inicio)
    return datos


def leer_party(conn, run_id: int):
    return conn.execute(
        "SELECT p.position, c.route, c.species, c.details->>'nickname' AS nickname, "
        "NOT EXISTS (SELECT 1 FROM encounters m WHERE m.run_id = c.run_id "
        "AND m.route = c.route AND m.event_type = 'muerte') AS alive, "
        + COLUMNAS_ESPECIE + " "
        "FROM party p "
        "JOIN encounters c ON c.run_id = p.run_id AND c.route = p.route AND c.event_type = 'captura' "
        "WHERE p.run_id = %s ORDER BY p.position",
        (run_id,),
    ).fetchall()


class EquipoNuevo(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    routes: list[Annotated[str, Field(min_length=1, max_length=100)]] = Field(max_length=6)


@app.get("/runs/{run_id}/party")
def equipo(run_id: int):
    with conectar() as conn:
        existe_run(conn, run_id)
        return leer_party(conn, run_id)


@app.put("/runs/{run_id}/party")
def cambiar_equipo(run_id: int, equipo: EquipoNuevo):
    if len(set(equipo.routes)) != len(equipo.routes):
        raise HTTPException(status_code=409, detail="Un Pokémon no puede estar dos veces en el equipo")

    with conectar() as conn:
        existe_run(conn, run_id)

        capturas = {
            fila["route"]: fila["vivo"]
            for fila in conn.execute(
                "SELECT c.route, NOT EXISTS (SELECT 1 FROM encounters m WHERE m.run_id = c.run_id "
                "AND m.route = c.route AND m.event_type = 'muerte') AS vivo "
                "FROM encounters c WHERE c.run_id = %s AND c.event_type = 'captura'",
                (run_id,),
            )
        }
        actuales = {fila["route"] for fila in conn.execute("SELECT route FROM party WHERE run_id = %s", (run_id,))}

        for ruta in equipo.routes:
            if ruta not in capturas:
                raise HTTPException(status_code=409, detail=f"No hay ninguna captura en «{ruta}»")
            if not capturas[ruta] and ruta not in actuales:
                raise HTTPException(status_code=409, detail=f"El Pokémon de «{ruta}» está muerto")

        conn.execute("DELETE FROM party WHERE run_id = %s", (run_id,))
        for posicion, ruta in enumerate(equipo.routes, start=1):
            conn.execute(
                "INSERT INTO party (run_id, route, position) VALUES (%s, %s, %s)",
                (run_id, ruta, posicion),
            )
        return leer_party(conn, run_id)


@app.get("/runs/{run_id}/graveyard")
def cementerio(run_id: int):
    with conectar() as conn:
        existe_run(conn, run_id)
        return conn.execute(
            "SELECT c.route, c.species, c.details->>'nickname' AS nickname, m.created_at AS muerto_en, "
            + COLUMNAS_ESPECIE + " "
            "FROM encounters c "
            "JOIN encounters m ON m.run_id = c.run_id AND m.route = c.route "
            "AND m.event_type = 'muerte' "
            "WHERE c.run_id = %s AND c.event_type = 'captura' "
            "ORDER BY m.created_at",
            (run_id,),
        ).fetchall()


@app.get("/species")
def buscar_especies(
    response: Response,
    q: str = Query(min_length=1, max_length=50),
    limit: int = Query(10, ge=1, le=20),
):
    inicio = time.perf_counter()
    prefijo = q.strip().lower()
    if not prefijo:
        return []
    datos, estado, ttl = leer_especies(prefijo, limit)
    poner_cabeceras_cache(response, estado, ttl, inicio)
    return datos


@app.middleware("http")
async def no_cachear_interfaz(request, call_next):
    # El HTML, el JS y el CSS cambian con cada versión: el navegador debe comprobar siempre si hay uno nuevo
    # (si no ha cambiado, el servidor responde 304 y no se descarga de nuevo). Sin esto, el navegador podía
    # mezclar un index.html nuevo con un app.js antiguo guardado en caché y la página dejaba de funcionar.
    respuesta = await call_next(request)
    ruta = request.url.path
    if ruta == "/" or ruta.endswith((".html", ".js", ".css")):
        respuesta.headers["Cache-Control"] = "no-cache"
    return respuesta


app.mount("/", StaticFiles(directory=Path(__file__).with_name("static"), html=True), name="static")
