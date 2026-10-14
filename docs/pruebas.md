# Pruebas y verificaciones

## 1. Persistencia de datos en dev (paso 2.4)

**Fecha:** 2026-10-11
**Objetivo:** demostrar que los datos de PostgreSQL sobreviven a eliminar el contenedor de la base de datos (requisito del enunciado).

### Antes

Partida creada para la prueba: `id=4`, «Persistencia 20261011-140538», con una captura (Eevee en «Ruta Persistencia»).

```
ID: 2335b1affc07  CREADO: 2026-10-10T21:54:39.124653907Z
local     randomlocke-dev_pgdata
 partidas | eventos
----------+---------
        4 |       7
[{"route":"Ruta Persistencia","species":"Eevee","created_at":"2026-10-11T12:05:52.013866+00:00"}]
```

### Eliminación del contenedor (no del volumen)

```
$ dc rm -s -f db
 ✔ Container randomlocke-dev-db-1 Removed
$ docker ps -a --filter name=db-1
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
$ docker volume ls | grep pgdata
local     randomlocke-dev_pgdata
$ curl -s -w "\nHTTP %{http_code}\n" http://localhost:8000/status
{"db":"down"}
HTTP 503
```

### Después (contenedor recreado con `dc up -d db`)

```
ID: 44e9376fb8b5  CREADO: 2026-10-11T15:15:00.599888049Z
local     randomlocke-dev_pgdata
 partidas | eventos
----------+---------
        4 |       7
[{"route":"Ruta Persistencia","species":"Eevee","created_at":"2026-10-11T12:05:52.013866+00:00"}]
{"db":"ok"}
HTTP 200
```

### Conclusión

| | Antes | Después |
|---|---|---|
| ID del contenedor `db` | `2335b1affc07` | `44e9376fb8b5` (nuevo) |
| Volumen | `randomlocke-dev_pgdata` | `randomlocke-dev_pgdata` (el mismo) |
| Partidas / eventos | 4 / 7 | 4 / 7 |
| Eevee en la partida 4 | sí | sí (misma fecha) |

El contenedor se destruyó y se creó uno distinto, pero los datos son idénticos: viven en el volumen, no en el contenedor. La web pasó a `unhealthy` mientras no hubo BD y volvió a `healthy` sola, sin reiniciarse.

## 2. Entornos levantados, healthchecks y puertos publicados

Fecha: 2026-10-14 11:53

```
$ make ps-dev
docker compose --env-file .env.dev  -f docker-compose.dev.yml ps
NAME                    IMAGE                 COMMAND                  SERVICE   CREATED        STATUS                  PORTS
randomlocke-dev-db-1    postgres:16           "docker-entrypoint.s…"   db        2 days ago     Up 17 hours (healthy)   5432/tcp
randomlocke-dev-web-1   randomlocke-dev-web   "uvicorn main:app --…"   web       17 hours ago   Up 17 hours (healthy)   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp

$ make ps-prod
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
NAME                       IMAGE                  COMMAND                  SERVICE   CREATED        STATUS                  PORTS
randomlocke-prod-cache-1   redis:7-alpine         "docker-entrypoint.s…"   cache     17 hours ago   Up 17 hours (healthy)   6379/tcp
randomlocke-prod-db-1      postgres:16            "docker-entrypoint.s…"   db        24 hours ago   Up 19 hours (healthy)   5432/tcp
randomlocke-prod-web-1     randomlocke-prod-web   "uvicorn main:app --…"   web       17 hours ago   Up 17 hours (healthy)   0.0.0.0:8080->8000/tcp, [::]:8080->8000/tcp
```

Los tres contenedores de prod (y los dos de dev) están `healthy`. Solo `web` publica un puerto (`8080` en prod, `8000` en dev); `db` y `cache` solo exponen su puerto dentro de la red.

### Desde el host no se alcanzan la base de datos ni la caché

```
$ conexión TCP a localhost:5432
  rechazada (BIEN): el puerto 5432 no está publicado
$ conexión TCP a localhost:6379
  rechazada (BIEN): el puerto 6379 no está publicado
```

## 3. /status con un servicio detenido (prod)

```
$ curl /status  (todo operativo)
{"estado":"ok","db":"ok","cache":"ok"}  [HTTP 200]

$ docker compose stop cache   (se espera 12 s)
{"estado":"degraded","db":"ok","cache":"caida"}  [HTTP 200]

$ docker compose start cache  (se espera 25 s)
{"estado":"ok","db":"ok","cache":"ok"}  [HTTP 200]

$ docker compose stop db      (se espera 15 s)
{"estado":"down","db":"down","cache":"ok"}  [HTTP 503]

$ docker compose start db     (se espera 30 s)
{"estado":"ok","db":"ok","cache":"ok"}  [HTTP 200]

$ make ps-prod
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
NAME                       IMAGE                  COMMAND                  SERVICE   CREATED        STATUS                        PORTS
randomlocke-prod-cache-1   redis:7-alpine         "docker-entrypoint.s…"   cache     17 hours ago   Up About a minute (healthy)   6379/tcp
randomlocke-prod-db-1      postgres:16            "docker-entrypoint.s…"   db        24 hours ago   Up 30 seconds (healthy)       5432/tcp
randomlocke-prod-web-1     randomlocke-prod-web   "uvicorn main:app --…"   web       17 hours ago   Up 17 hours (healthy)         0.0.0.0:8080->8000/tcp, [::]:8080->8000/tcp
```

Caché parada: `200` con `degraded` (la web sigue `healthy` y lee de PostgreSQL). BD parada: `503` con `down`. Al volver cada servicio, `/status` vuelve a `ok` sin reiniciar la web. En la interfaz el cambio se ve sin recargar la página (círculos de BD y de caché).

## 4. Comando de prueba de conexión a la base de datos (prod)

```
$ docker compose exec db psql -c "SELECT 1 AS conexion_ok" -c "\dt"
 conexion_ok 
-------------
           1
(1 row)

           List of relations
 Schema |    Name    | Type  |  Owner  
--------+------------+-------+---------
 public | encounters | table | tracker
 public | runs       | table | tracker
(2 rows)

```

## 5. Persistencia de datos en prod: eliminar el contenedor de la BD y recrearlo

Se crea una partida marcada, se anota el ID del contenedor, el volumen y el número de filas, se elimina **solo el contenedor** (`rm -s -f db`, no `down -v`) y se recrea.

```
$ curl -X POST /runs  (crear partida marcada)
{"id":4,"name":"Persistencia prod 20261014-115539",}

--- ANTES ---
ID del contenedor db: dc80222da005
Volumen:              randomlocke-prod_pgdata
Filas:                4 partidas, 12 eventos

$ docker compose rm -s -f db   (elimina el contenedor, NO el volumen)
 Container randomlocke-prod-db-1 Removing 
 Container randomlocke-prod-db-1 Removed 

$ docker volume ls | grep pgdata
local     randomlocke-prod_pgdata

$ docker compose up -d db
 Container randomlocke-prod-db-1 Started 

--- DESPUES ---
ID del contenedor db: c4abb313400c
Volumen:              randomlocke-prod_pgdata
Filas:                4 partidas, 12 eventos
Eevee sigue en la partida marcada:
[{"route":"Ruta 1","species":"Eevee",}]
```

El contenedor es **otro** (ID distinto), el volumen es el mismo y los datos están intactos: viven en el volumen, no en el contenedor.

## 6. Caché en prod: MISS, HIT, invalidación y TTL

Partida nueva para la prueba. Cabecera `X-Cache`: HIT o MISS; `X-Cache-TTL`: segundos restantes; `X-Latency-Ms`: latencia de la lectura.

```
Partida de prueba: 5

$ POST captura Ruta 1 Pidgey
{"id":13,"run_id":5,"event_type":"captura","route":"Ruta 1","species":"Pidgey",}  [HTTP 201]

$ GET /runs/5/team  (primera lectura)
x-cache: MISS
x-cache-ttl: 30
x-latency-ms: 16.8
[Pidgey (Ruta 1)]

$ GET /runs/5/team  (segunda lectura)
x-cache: HIT
x-cache-ttl: 30
x-latency-ms: 0.9
[Pidgey (Ruta 1)]

$ POST captura Ruta 2 Rattata  (registrar un evento invalida la caché)
{"id":14,"run_id":5,"event_type":"captura","route":"Ruta 2","species":"Rattata",}  [HTTP 201]

$ GET (tras registrar)
x-cache: MISS
x-cache-ttl: 30
x-latency-ms: 13.3
[Pidgey (Ruta 1),Rattata (Ruta 2)]

$ GET (otra vez)
x-cache: HIT
x-cache-ttl: 30
x-latency-ms: 0.8
[Pidgey (Ruta 1),Rattata (Ruta 2)]

$ POST captura Ruta 2 otra vez  (rechazado: no debe invalidar)
{"detail":"Esa ruta ya tiene un resultado de primer encuentro"}  [HTTP 409]

$ GET (sigue HIT)
x-cache: HIT
x-cache-ttl: 30
x-latency-ms: 0.8
[Pidgey (Ruta 1),Rattata (Ruta 2)]

$ INSERT directo en la BD, sin pasar por la API (Ruta 3, Ditto)
INSERT 0 1

$ GET inmediato: dato viejo, la caché no sabe nada del cambio
x-cache: HIT
x-cache-ttl: 29
x-latency-ms: 0.7
[Pidgey (Ruta 1),Rattata (Ruta 2)]

$ sleep 32  (el TTL de 30 s caduca)
$ GET: caduca el TTL y aparece el dato nuevo
x-cache: MISS
x-cache-ttl: 30
x-latency-ms: 14.1
[Pidgey (Ruta 1),Rattata (Ruta 2),Ditto (Ruta 3)]
```

- La primera lectura es `MISS` (consulta a PostgreSQL y guarda en Redis con TTL de 30 s) y la segunda `HIT` (más rápida, con el TTL bajando).
- Registrar un evento confirmado invalida la caché: la lectura siguiente es `MISS` con los datos nuevos. Un registro rechazado (`409`) **no** invalida.
- Un cambio hecho directamente en la BD no invalida: se sigue sirviendo el dato viejo hasta que el TTL caduca. Es la red de seguridad del TTL.

### Caché parada: la aplicación sigue funcionando

```
$ docker compose stop cache  (se espera 12 s)
$ POST captura Ruta 4 Zubat con la caché parada
{"id":16,"run_id":5,"event_type":"captura","route":"Ruta 4","species":"Zubat",}  [HTTP 201]

$ GET con la caché parada
x-cache: DEGRADED
x-latency-ms: 13.9
[Pidgey (Ruta 1),Rattata (Ruta 2),Ditto (Ruta 3),Zubat (Ruta 4)]

$ docker compose start cache  (se espera 25 s)
$ GET con la caché de vuelta
x-cache: MISS
x-cache-ttl: 30
x-latency-ms: 15.5
[Pidgey (Ruta 1),Rattata (Ruta 2),Ditto (Ruta 3),Zubat (Ruta 4)]
$ GET otra vez
x-cache: HIT
x-cache-ttl: 30
x-latency-ms: 0.8
[Pidgey (Ruta 1),Rattata (Ruta 2),Ditto (Ruta 3),Zubat (Ruta 4)]
```

Con Redis parado, registrar un evento sigue dando `201` y leer da `X-Cache: DEGRADED` (lee de PostgreSQL, más lento pero funcional). Al volver Redis, vuelve el ciclo `MISS` → `HIT`.

## 7. `make down` limpia el entorno y conserva los datos

```
Filas en prod antes: 5 partidas, 16 eventos

$ make down
docker compose --env-file .env.dev  -f docker-compose.dev.yml down
 Container randomlocke-dev-web-1 Stopping 
 Container randomlocke-dev-web-1 Stopped 
 Container randomlocke-dev-web-1 Removing 
 Container randomlocke-dev-web-1 Removed 
 Container randomlocke-dev-db-1 Stopping 
 Container randomlocke-dev-db-1 Stopped 
 Container randomlocke-dev-db-1 Removing 
 Container randomlocke-dev-db-1 Removed 
 Network randomlocke-dev_default Removing 
 Network randomlocke-dev_default Removed 
docker compose --env-file .env.prod -f docker-compose.prod.yml down
 Container randomlocke-prod-web-1 Stopping 
 Container randomlocke-prod-web-1 Stopped 
 Container randomlocke-prod-web-1 Removing 
 Container randomlocke-prod-web-1 Removed 
 Container randomlocke-prod-db-1 Stopping 
 Container randomlocke-prod-cache-1 Stopping 
 Container randomlocke-prod-cache-1 Stopped 
 Container randomlocke-prod-cache-1 Removing 
 Container randomlocke-prod-cache-1 Removed 
 Container randomlocke-prod-db-1 Stopped 
 Container randomlocke-prod-db-1 Removing 
 Container randomlocke-prod-db-1 Removed 
 Network randomlocke-prod_backend Removing 
 Network randomlocke-prod_frontend Removing 
 Network randomlocke-prod_backend Removed 
 Network randomlocke-prod_frontend Removed 

$ docker ps -a --filter name=randomlocke
NAMES     STATUS

$ docker volume ls | grep pgdata
local     randomlocke-dev_pgdata
local     randomlocke-prod_pgdata

$ docker network ls | grep randomlocke
(ninguna red de randomlocke: eliminadas)

$ make up-dev && make up-prod

$ make ps-prod
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
NAME                       IMAGE                  COMMAND                  SERVICE   CREATED          STATUS                    PORTS
randomlocke-prod-cache-1   redis:7-alpine         "docker-entrypoint.s…"   cache     24 seconds ago   Up 24 seconds (healthy)   6379/tcp
randomlocke-prod-db-1      postgres:16            "docker-entrypoint.s…"   db        24 seconds ago   Up 23 seconds (healthy)   5432/tcp
randomlocke-prod-web-1     randomlocke-prod-web   "uvicorn main:app --…"   web       24 seconds ago   Up 18 seconds (healthy)   0.0.0.0:8080->8000/tcp, [::]:8080->8000/tcp

Filas en prod después: 5 partidas, 16 eventos

$ curl /status (prod)
{"estado":"ok","db":"ok","cache":"ok"}  [HTTP 200]
$ curl /status (dev)
{"estado":"ok","db":"ok","cache":"no aplica"}  [HTTP 200]
```

`make down` elimina contenedores y redes pero **conserva los volúmenes**: tras volver a levantar, las partidas y los eventos siguen. El único comando que borra los datos es `make clean-dev` / `make clean-prod` (`down -v`), que avisa antes.

## 8. Despliegue desde cero en un clon limpio (paso 3.4)

Se clonó el repositorio desde GitHub en una carpeta nueva (`RedesAvanzadas/prueba-limpia`), **sin ningún `.env` real** (el primer intento de `make clean-prod` falló con `couldn't find env file`, prueba de que no viaja ningún secreto en el repositorio). Se creó `.env.prod` desde la plantilla con contraseñas aleatorias y `WEB_PORT=8081`, y se levantó con un nombre de proyecto propio para no tocar el prod real:

```
$ COMPOSE_PROJECT_NAME=prueba-limpia make up-prod
 ✔ Image prueba-limpia-web         Built
 ✔ Network prueba-limpia_backend   Created
 ✔ Network prueba-limpia_frontend  Created
 ✔ Volume prueba-limpia_pgdata     Created
 ✔ Container prueba-limpia-db-1    Healthy
 ✔ Container prueba-limpia-cache-1 Healthy
 ✔ Container prueba-limpia-web-1   Started

$ COMPOSE_PROJECT_NAME=prueba-limpia make ps-prod
prueba-limpia-cache-1   redis:7-alpine      Up 30 seconds (healthy)   6379/tcp
prueba-limpia-db-1      postgres:16         Up 30 seconds (healthy)   5432/tcp
prueba-limpia-web-1     prueba-limpia-web   Up 24 seconds (healthy)   0.0.0.0:8081->8000/tcp

$ curl localhost:8081/status
{"estado":"ok","db":"ok","cache":"ok"}

$ crear partida y leer el equipo dos veces
x-cache: MISS
x-cache: HIT
```

Limitación honesta: las capas de la imagen salieron `CACHED` (el Docker ya las tenía), así que no fue un *build* sin caché de Docker; sí fue un despliegue desde cero en cuanto a repositorio, `.env`, redes y volumen.

## 9. Revisión de seguridad (paso 4.1)

| Comprobación | Resultado |
|---|---|
| Ficheros `.env` versionados (ahora y en todo el historial) | Solo `.env.dev.example` y `.env.prod.example` |
| `.env.dev`, `.env.prod`, `CLAUDE.md`, `Practica1.pdf` | Ignorados por Git (`git check-ignore -v`) |
| Credenciales en código o YAML (`grep` de `password`, `secret`, `token`, `api_key` en los ficheros versionados) | Solo referencias `${VAR}` y `os.environ`, y los valores ficticios `cambia_esto` de las plantillas |
| Puertos publicados en prod | Solo `web` (`0.0.0.0:8080->8000`); `db` y `cache` no |
| Usuario de los procesos (`docker top`) | `web` uid 10001, `db` uid 999 (`postgres`), `cache` uid 999 (`redis`, tras añadir `user: redis`) |
| `/docs`, `/redoc`, `/openapi.json` | Prod: `404` (`ENABLE_DOCS=false`); dev: `200` |
| Permisos de los `.env` | `-rw-r--r--` (644): `chmod 600` no tiene efecto en NTFS montado en WSL (`drvfs` sin `metadata`). En un servidor Linux se aplicaría `chmod 600 .env.*`; compensado porque los `.env` están ignorados por Git y no se reutilizan en otros proyectos |

## 10. Resumen de cumplimiento de la lista de verificaciones

| Verificación (`idea-y-alcance.md` §11) | Dónde |
|---|---|
| `make up-dev` y `make up-prod` levantan el entorno desde cero | §8 y §7 |
| `docker compose ps` muestra todos los contenedores `healthy` | §2 |
| Solo el puerto de `web` está publicado | §2 |
| `/status` con todo operativo y con un servicio detenido, y reflejo en la UI | §3 |
| Comando de prueba de conexión a la BD | §4 |
| Persistencia: insertar, eliminar el contenedor, volver a levantar | §1 (dev) y §5 (prod) |
| Caché: MISS → HIT e invalidación tras registrar un evento | §6 |
| `make down` limpia el entorno | §7 |
