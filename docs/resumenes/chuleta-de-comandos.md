# Chuleta de comandos para la defensa

> Todo se ejecuta **desde WSL** (Ubuntu), en la **raíz del proyecto**: `cd /mnt/c/Users/andre/Documents/RedesAvanzadas/Tracker_Randomlocke`. `make` solo existe en WSL (no en PowerShell ni Git Bash).
> **Prod:** http://localhost:8080 (con caché). **Dev:** http://localhost:8000 (sin caché).
> Para no escribir el comando largo, define este atajo al empezar (se pierde al cerrar la terminal):
> ```bash
> P="docker compose --env-file .env.prod -f docker-compose.prod.yml"
> ```
> (Para dev sería `D="docker compose --env-file .env.dev -f docker-compose.dev.yml"`).

## 1. Los `make` (el atajo oficial)

| Comando | Qué hace | Cuándo usarlo |
|---|---|---|
| `make up-dev` | Construye la imagen y levanta `web` + `db` de **dev** en segundo plano | Arrancar desarrollo |
| `make up-prod` | Construye la imagen y levanta `web` + `db` + `cache` de **prod** | Arrancar producción |
| `make down` | Para y elimina los contenedores y redes de **dev y prod**. **Conserva los datos** (volúmenes) | «Apaga todo» |
| `make down-dev` / `make down-prod` | Igual, pero solo de un entorno | Apagar solo uno |
| `make ps-dev` / `make ps-prod` | Lista los contenedores del entorno, su estado (`healthy`) y los puertos | Comprobar que está todo bien |
| `make logs-dev` / `make logs-prod` | Sigue los logs en directo (últimas 50 líneas). Se sale con `Ctrl+C` | Ver qué pasa |
| `make build-dev` / `make build-prod` | Solo construye la imagen, sin levantar | Raramente |
| `make clean-dev` / `make clean-prod` | **Borra contenedores, redes Y DATOS** (`down -v`). Avisa antes | Empezar de cero de verdad. **Peligroso** |

**Targets de prod para tumbar y levantar servicios sueltos** (paran/arrancan el contenedor **sin eliminarlo** ni tocar los datos):

| Comando | Qué hace |
|---|---|
| `make stop-cache` / `make start-cache` | Para / arranca Redis |
| `make stop-db` / `make start-db` | Para / arranca PostgreSQL |
| `make stop-web` / `make start-web` | Para / arranca la web |
| `make psql-prod` | Comando de prueba de conexión a la BD: `SELECT 1` y lista las tablas |

`make -n <objetivo>` enseña el comando que ejecutaría **sin ejecutarlo** (ensayo en seco).

## 2. Guiones típicos de la defensa

### «Levanta la web de cero»
**Desde el proyecto ya clonado** (los `.env` ya existen):
```bash
make up-prod          # levanta prod
make ps-prod          # espera ~20 s: db, cache y web en "healthy"
curl -s localhost:8080/status    # {"estado":"ok","db":"ok","cache":"ok"}
```
**Desde cero absoluto, borrando también los datos:**
```bash
make clean-prod       # borra contenedores, redes y volumen
make up-prod
```
**Desde un clon nuevo (sin `.env`):** `git clone <url> carpeta && cd carpeta`, crear `.env.prod` a partir de `.env.prod.example` (cambiando las contraseñas), y `make up-prod`.

### «Tumba la caché»
```bash
make stop-cache       # para Redis
sleep 12; curl -s localhost:8080/status
```
Resultado: `{"estado":"degraded","db":"ok","cache":"caida"}` (HTTP 200). La web **sigue funcionando** leyendo de PostgreSQL; en la interfaz, círculo rojo de la caché y «Origen: base de datos · caché caída».
```bash
make start-cache      # vuelve; en ~10-25 s el estado vuelve a ok
```

### «Tumba la base de datos»
```bash
make stop-db
sleep 12; curl -s -w ' [HTTP %{http_code}]\n' localhost:8080/status
```
Resultado: `{"estado":"down","db":"down",...}` con **503**. La interfaz marca «BD caída» y avisa al intentar cargar datos.
```bash
make start-db         # ~30 s: se recupera sola, sin reiniciar la web
```

### «Tumba la web»
```bash
make stop-web         # la página deja de responder; db y cache siguen vivos
make start-web        # vuelve en ~15 s
```

### «Demuestra la persistencia»
```bash
$P exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tA -c "SELECT count(*) FROM runs;"'   # cuenta partidas
docker inspect -f '{{.Id}}' randomlocke-prod-db-1 | cut -c1-12                                    # ID del contenedor
$P rm -s -f db        # ELIMINA el contenedor (no el volumen)
$P up -d db           # lo recrea (esperar a "healthy")
docker inspect -f '{{.Id}}' randomlocke-prod-db-1 | cut -c1-12                                    # ID distinto
$P exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tA -c "SELECT count(*) FROM runs;"'   # mismo número
```
Contenedor nuevo, mismos datos: viven en el volumen `randomlocke-prod_pgdata`. **Lo que rompería esto:** `make clean-prod` (`down -v`).

### «Demuestra la caché (MISS → HIT → invalidación)»
```bash
ID=5     # el id de una partida; mira http://localhost:8080/runs
leer() { curl -si localhost:8080/runs/$ID/team | tr -d '\r' | grep -i -E '^x-cache|^x-latency'; }
leer     # X-Cache: MISS  (va a PostgreSQL y guarda en Redis, TTL 30 s)
leer     # X-Cache: HIT   (sale de Redis, más rápido)
curl -s -X POST localhost:8080/runs/$ID/events -H 'Content-Type: application/json' \
  -d '{"event_type":"captura","route":"Ruta 20","species":"Mew"}'    # registrar un evento invalida la caché
leer     # X-Cache: MISS otra vez (datos nuevos)
```
Ver lo que hay **dentro de Redis**:
```bash
$P exec cache sh -c 'REDISCLI_AUTH=$REDIS_PASSWORD redis-cli KEYS "*"'        # claves: team:5 ...
$P exec cache sh -c 'REDISCLI_AUTH=$REDIS_PASSWORD redis-cli TTL team:5'      # segundos que le quedan
$P exec cache sh -c 'REDISCLI_AUTH=$REDIS_PASSWORD redis-cli GET team:5'      # el JSON guardado
```

### «Demuestra que solo `web` publica puerto»
```bash
make ps-prod                                  # solo web muestra 0.0.0.0:8080->8000; db y cache solo 5432/tcp y 6379/tcp (internos)
timeout 3 bash -c 'echo > /dev/tcp/127.0.0.1/5432' || echo "5432 no accesible desde fuera"
timeout 3 bash -c 'echo > /dev/tcp/127.0.0.1/6379' || echo "6379 no accesible desde fuera"
docker network inspect randomlocke-prod_backend -f '{{.Internal}}'   # true (red interna)
```

### «Demuestra que no corre como root / que no hay credenciales»
```bash
docker top randomlocke-prod-web-1 | head -3     # UID 10001
docker top randomlocke-prod-cache-1 | head -3   # UID 999 (redis)
git ls-files | grep -i "\.env"                  # solo .env.dev.example y .env.prod.example
curl -s -o /dev/null -w '%{http_code}\n' localhost:8080/docs    # 404 en prod
curl -s -o /dev/null -w '%{http_code}\n' localhost:8000/docs    # 200 en dev
```

## 3. Comandos sueltos útiles (los que se usan por debajo)

| Comando | Qué hace |
|---|---|
| `docker ps` | Contenedores en marcha (con puertos y estado) |
| `docker ps -a` | También los parados |
| `$P ps` | Contenedores de **prod** (igual que `make ps-prod`) |
| `$P logs web --tail 30` | Últimas 30 líneas del log de `web` (cambia `web` por `db` o `cache`) |
| `$P exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "\dt"'` | Entra a PostgreSQL y lista las tablas (**comando de prueba de conexión**) |
| `$P stop <servicio>` / `$P start <servicio>` | Para / arranca un servicio sin borrarlo |
| `$P restart web` | Reinicia solo la web |
| `$P rm -s -f db` | Elimina el contenedor `db` (**conserva** el volumen) |
| `$P up -d --build web` | Reconstruye la imagen de `web` y la recrea (tras cambiar código) |
| `$P config --quiet` | Valida el YAML **sin imprimir** variables (no uses `config` a secas: muestra contraseñas) |
| `docker volume ls` | Volúmenes (donde están los datos) |
| `docker network ls` | Redes |
| `docker inspect -f '{{.State.Health.Status}}' randomlocke-prod-web-1` | Estado de salud de un contenedor |
| `curl -s localhost:8080/status` | Estado real de BD y caché (HTTP 200 o 503) |

## 4. Precauciones

- `make down` **no** borra datos. `make clean-*` **sí**. Si dudas, usa `down`.
- Tras `start cache` / `start db`, espera ~25-30 s: la recuperación no es instantánea (DNS de Docker Desktop y vigilancia cada 3 s).
- Con la BD parada más de ~30 s, Docker marca `web` como `unhealthy` (3 comprobaciones seguidas fallidas); se recupera sola al volver la BD.
- Si algo se queda raro: `make ps-prod` y `$P logs <servicio> --tail 30`.
- No muestres nunca `.env.dev` ni `.env.prod` en pantalla durante la exposición.

## 5. Autocompletado de especies (paso 3.5)

```bash
# sugerencias de la API (prod): 1.ª vez MISS, 2.ª HIT
curl -si "localhost:8080/species?q=zub" | tr -d '\r' | grep -i -E '^x-cache:|^\['
# cuántas especies hay en la tabla (debe ser 1025)
$P exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tA -c "SELECT count(*) FROM species;"'
# claves de la caché de especies y su TTL
$P exec cache sh -c 'REDISCLI_AUTH=$REDIS_PASSWORD redis-cli --scan --pattern "species:*"'
$P exec cache sh -c 'REDISCLI_AUTH=$REDIS_PASSWORD redis-cli TTL species:zub:10'
```
En la interfaz: escribe `zub` en «Especie» y aparece `Zubat`. **Tras `make clean-prod` y `make up-prod` la lista se recarga sola** (1025 especies) porque `web` la carga al arrancar. Con la caché parada (`make stop-cache`) las sugerencias siguen funcionando, leídas de PostgreSQL (`X-Cache: DEGRADED`).

**Demostrar que la caché reduce consultas a la BD** (contador de transacciones antes y después de 100 peticiones iguales; en prod sube muy poco, en dev sube ~200):
```bash
tx() { $P exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tA -c "SELECT xact_commit FROM pg_stat_database WHERE datname = current_database();"'; }
A=$(tx); for i in $(seq 1 100); do curl -s -o /dev/null "localhost:8080/species?q=pik"; done; B=$(tx); echo "transacciones: $((B-A))"
```
(Para dev usa `D` en vez de `P` y el puerto 8000.)

## 6. Datos de demostración (script local, no está en el repositorio)

```bash
bash scripts/seed-demo.sh prod     # carga 6 partidas de ejemplo en prod (puerto 8080); "dev" para el 8000
```
Es idempotente (omite las partidas que ya existen) y usa la API. Para empezar de cero con datos de demo: `make clean-prod`, `make up-prod`, esperar a `healthy` y ejecutar el script. Si dev está parado tras reiniciar el PC: `make up-dev`.
