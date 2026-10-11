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
