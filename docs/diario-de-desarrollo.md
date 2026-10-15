# Diario de desarrollo

Registro paso a paso de la Práctica 1 según la hoja de ruta de `docs/dependencias-y-pasos.md`.

---

### [Paso 0.1: verificar el entorno]
- **Fecha:** 2026-10-08
- **Archivos:** ninguno (paso de verificación)
- **Comandos:**
  - PowerShell: `wsl -l -v`, `docker --version`, `docker compose version`, `docker run --rm hello-world`, `git --version`, `git config --global user.name`, `git config --global user.email`, `netstat -ano | findstr :8000`, `netstat -ano | findstr :8080`, `python --version`
  - WSL (Ubuntu 22.04): `docker --version`, `docker compose version`, `docker run --rm hello-world`, `make --version`, `git --version`, `docker pull python:3.12-slim`, `docker pull postgres:16`, `docker pull redis:7-alpine`, `ssh -T git@github.com`
  - Resultado: WSL2, Docker 29.8.1, Compose v5.5.1, GNU Make 4.3 en WSL y puertos 8000/8080 libres; imágenes base descargadas. Se activó la integración Docker–WSL, que estaba desactivada. Se corrigió el email de Git (dominio `.eu`). SSH a GitHub sin clave todavía (`Permission denied`, esperado): se crea en el Paso 0.2.
- **Justificación:** se cierra la decisión 2: `make` y `docker` se ejecutan en WSL (entorno Linux, como los contenedores). Inicialmente Git iba en Windows con HTTPS; ver la actualización final de esta entrada, que es la decisión vigente.
  El riesgo de finales de línea CRLF en el `Makefile` se mitiga en el Paso 0.2 con `.gitattributes` (LF) y `.editorconfig`.
- **Asistencia de IA:** Claude Code (app de escritorio), modelo Claude Opus 5.5 (`claude-opus-5-5`). Finalidad: explicar qué se comprueba y por qué, dar los comandos y revisar las salidas. Parte del trabajo: Fase 0, verificación del entorno y cierre de la decisión 2.
- **Commit:** sin commit (paso de verificación). El diario se versionará en el Paso 0.2.
- **Actualización (2026-10-08):** se revisa la decisión 2: Git también se ejecuta en WSL, autenticado por SSH, y VS Code se abre en modo WSL. Motivo: un único entorno Linux para Git, `make` y `docker`, sin dos instalaciones de Git sobre la misma carpeta.

### [Paso 0.2: repositorio y ficheros base]
- **Fecha:** 2026-10-08
- **Archivos:** `.gitignore`, `.gitattributes`, `.editorconfig`, `docs/idea-y-alcance.md`, `docs/dependencias-y-pasos.md`, `docs/diario-de-desarrollo.md`
- **Comandos:**
  - Autenticación (WSL): `ssh-keygen -t ed25519 -C "<email>"`, `cat ~/.ssh/id_ed25519.pub` (solo la clave pública, añadida en GitHub → Settings → SSH and GPG keys), `ssh -T git@github.com`
  - Repositorio (WSL): `git init -b main`, `git config core.filemode` (resultado `false`), `git remote add origin git@github.com:Akrahan/Tracker_Randomlocke.git`, `git remote -v`
  - Revisión antes del commit: `git check-ignore -v Practica1.pdf CLAUDE.md`, `git status --short --untracked-files=all`, `git add .`, `git status`
  - Publicación: `git commit -m "..."`, `git push -u origin main`
- **Qué se ha hecho y cómo:**
  - Se creó en GitHub un repositorio público **vacío** (sin README, `.gitignore` ni licencia) y se conectó a la carpeta existente con `git init` + `git remote add`, en lugar de clonar y mover ficheros. Así se trabaja sobre la carpeta de la decisión 1 y se puede revisar todo con `git status` antes del primer commit.
  - `.gitignore`: excluye los `.env` reales (antes de que existan), cachés y entornos de Python, configuración local de editor y herramientas (`.vscode/`, `.claude/`) y material no publicable (`Practica1.pdf`, `CLAUDE.md`).
  - `.gitattributes`: `* text=auto eol=lf` fuerza LF en el repositorio y al clonar, sea cual sea la configuración de cada máquina; las imágenes y los PDF se marcan como binarios.
  - `.editorconfig`: el editor escribe con UTF-8, LF, salto de línea final y sin espacios sobrantes; sangría de 4 espacios (2 en YAML y Markdown) y **tabuladores en el `Makefile`**.
  - Antes del commit se verificó que solo entraban los 6 ficheros previstos y que el PDF y `CLAUDE.md` se ignoraban.
- **Decisiones:**
  - Git, `make` y `docker` se ejecutan en WSL, con VS Code abierto en modo WSL. La autenticación es por **SSH (ed25519)**; la clave privada vive en `~/.ssh` (sistema de ficheros Linux, permisos `600`) y nunca sale de la máquina.
  - `core.filemode=false` en el repositorio, porque NTFS (`/mnt/c`) no conserva permisos de Linux y sin esto aparecerían cambios de permisos que no son reales.
  - `Practica1.pdf` no se publica (material de la universidad, 6 MB). `CLAUDE.md` tampoco: la declaración de uso de IA se hace en el README y en este diario.
  - El README se escribirá completo en el Paso 4.3; no se crea uno mínimo ahora.
  - Mensajes de commit con *Conventional Commits* (`chore:`, `feat:`, `docs:`, `build:`) para que el historial sea legible.
- **Justificación:** `.gitignore`, `.gitattributes` y `.editorconfig` son preventivos: solo protegen lo que entra **después** de crearlos, por eso van antes de cualquier código o secreto.
  Forzar LF y tabuladores evita que el `Makefile` y los scripts fallen en Linux (WSL y contenedores), y versionarlos hace que las reglas viajen con el proyecto a cualquiera que lo clone.
- **Asistencia de IA:** Claude Code (app de escritorio), modelo Claude Opus 5.5 (`claude-opus-5-5`). Finalidad: explicar cada fichero y cada decisión, dar los comandos y el contenido de los ficheros de configuración, y revisar las salidas y los ficheros escritos por el alumno. Parte del trabajo: Fase 0, inicialización del repositorio y configuración base.
- **Commit:** `chore: init repo with gitignore, gitattributes and editorconfig` (`2a547e8`), publicado con `git push -u origin main`

### [Paso 0.3: estructura de carpetas]
- **Fecha:** 2026-10-08 (commit) y 2026-10-09 (publicación, tras la incidencia de abajo)
- **Archivos:** `app/static/.gitkeep`
- **Comandos:** `mkdir -p app/static`, `touch app/static/.gitkeep`, `git status --short --untracked-files=all`, `git add .`, `git commit -m "..."`, `git push`
- **Decisiones:**
  - Git no guarda carpetas vacías, así que se usa un fichero vacío `.gitkeep` para que `app/static/` exista al clonar el repositorio (si no, un Dockerfile o la app que la esperen fallarían en una máquina limpia).
  - Opción A: solo se crea `app/static/` ahora. `db/` se crea en el Paso 2.1 únicamente si se elige la inicialización con scripts de `initdb.d` (decisión 5); si se elige SQL idempotente al arrancar la app, la carpeta no haría falta. Motivo: simplicidad, sin carpetas sin uso.
- **Justificación:** la estructura de `app/` (API, Dockerfile, `requirements.txt` y frontend estático servido por la propia API) refleja la arquitectura acordada de un único contenedor `web` con un solo puerto publicado.
- **Asistencia de IA:** Claude Code (app de escritorio), modelos Claude Opus 5.5 (`claude-opus-5-5`) y Claude Sonnet 5.5 (`claude-sonnet-5-5`). Finalidad: explicar el problema de las carpetas vacías y las dos opciones, y revisar las salidas. Parte del trabajo: Fase 0, estructura de carpetas.
- **Commit:** `chore: add app/static folder structure` (`87bacab` tras el rebase)

### [Incidencia durante el Paso 0.3: push rechazado]
- **Fecha:** 2026-10-09
- **Archivos:** `docs/diario-de-desarrollo.md` (conflicto resuelto a mano)
- **Comandos:** `git push` (error 1: `Could not resolve hostname github.com`; error 2: `! [rejected] main -> main (fetch first)`). Diagnóstico, solo lectura: `git fetch origin`, `git log --oneline --graph --all`, `git diff --stat main origin/main`, `git show origin/main`. Resolución: `git pull --rebase origin main`, edición del conflicto, `git add`, `git rebase --continue`, `git push`.
- **Causa:**
  - Error 1: fallo temporal de DNS en WSL, ajeno al repositorio y a la clave SSH. Se resolvió solo al reintentar.
  - Error 2: el diario se había editado directamente en la web de GitHub (commit `b98dcbc`, "Update diario-de-desarrollo.md"). `origin/main` y la rama local divergían desde `2a547e8`, y Git rechaza el push para no sobrescribir commits que no tiene.
- **Resolución:** se revisó el contenido del commit remoto con `git show origin/main`: solo cambiaba la línea `Commit:` del Paso 0.2 (con un espacio de más tras `chore:`). Esa misma línea se había corregido también en local, por lo que `git pull --rebase` produjo un conflicto en ella. Se conservó la versión local (con el hash y cómo se publicó) y se descartó la de la web. El historial quedó lineal, sin commit de fusión, y el push posterior fue correcto.
- **Justificación:** se eligió `rebase` y no `merge` por ser un repositorio de una sola persona (historial lineal más fácil de leer). No se usó `git push --force`, que habría borrado el commit remoto sin saber qué contenía.
- **Reglas adoptadas:** (1) no editar ficheros desde la web de GitHub; todo se cambia en local y se sube con `push`. (2) No usar `--force` sin revisar antes qué contiene el remoto. (3) Mensajes de commit con `git commit -m "..."` para no abrir un editor.
- **Asistencia de IA:** Claude Code (app de escritorio), modelo Claude Sonnet 5.5 (`claude-sonnet-5-5`). Finalidad: interpretar los errores, proponer un diagnóstico seguro y guiar la resolución del conflicto de rebase. Parte del trabajo: Fase 0, publicación del Paso 0.3.
- **Commit:** `docs: log push rejection incident` (`d954c33` tras el rebase)


### [Paso 1.1: variables de entorno de dev]
- **Fecha:** 2026-10-09
- **Archivos:** `.env.dev.example` (versionado); `.env.dev` (real, ignorado por Git, no versionado)
- **Comandos:** `cp .env.dev.example .env.dev`, `openssl rand -base64 24` (generación de la contraseña), `chmod 600 .env.dev`, `ls -l .env.dev`, `git status --short`, `git check-ignore -v .env.dev`, `grep -n POSTGRES_PASSWORD .env.dev.example`, `git add .env.dev.example`, `git commit`, `git push`
- **Variables definidas (solo nombres):** `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `DB_HOST`, `WEB_PORT`, `CACHE_ENABLED`.
- **Qué se ha hecho y cómo:**
  - La plantilla `.env.dev.example` lleva valores ficticios y documenta qué variables hay que definir. Se copió a `.env.dev`, donde la contraseña es real, aleatoria y exclusiva de este proyecto.
  - `git check-ignore -v .env.dev` confirmó que el real se ignora (regla de `.gitignore` línea 3) y `git ls-files` que no está en el repositorio.
- **Incidencia:** al preparar la plantilla se escribió en ella por error una contraseña real. Se detectó al revisar el fichero **antes** del primer `git add` (estaba sin seguir), se sustituyó por un valor ficticio y se generó una contraseña nueva para `.env.dev`. Nunca llegó al historial. Lección: borrar un secreto en un commit posterior no lo elimina del historial, por eso la revisión se hace antes de `add`.
- **Limitación conocida:** `chmod 600` no tiene efecto porque el repositorio está en `/mnt/c` (NTFS): el fichero sigue como `-rwxrwxrwx`. Se documentará con honestidad en el README (§1.3c del plan). Alternativa pendiente de valorar: mover el repositorio al sistema de ficheros de WSL.
- **Justificación:** el enunciado prohíbe credenciales hardcodeadas. El compose usará interpolación (`${POSTGRES_PASSWORD}`), de modo que el YAML contiene solo nombres de variables. Los `.env` reales se entregarán en el ZIP con credenciales exclusivas del proyecto (decisión 9); alternativa en un entorno real: Docker secrets o un gestor de secretos.
- **Asistencia de IA:** Claude Code (app de escritorio), modelo Claude Sonnet 5.5 (`claude-sonnet-5-5`). Finalidad: explicar la interpolación de variables, proponer la plantilla y revisar la versionada (sin leer `.env.dev`). Parte del trabajo: Fase 1, variables de entorno de dev.
- **Commit:** `chore(env): add dev environment variables template` (`d64672b`)

### [Paso 1.2: solo la base de datos]
- **Fecha:** 2026-10-10
- **Archivos:** `docker-compose.dev.yml`
- **Comandos:** `docker compose --env-file .env.dev -f docker-compose.dev.yml config --quiet` (validación de sintaxis, con y sin `--env-file`), `alias dc='docker compose --env-file .env.dev -f docker-compose.dev.yml'`, `dc up -d db`, `dc ps`, `dc exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT version();"'`, `docker ps --format "table {{.Names}}\t{{.Ports}}"`, `nc -zv localhost 5432`, `dc down`
- **Qué se ha hecho y cómo:**
  - Primer `docker-compose.dev.yml`, construido en tres piezas: (1) `name: randomlocke-dev` y el servicio `db` con la imagen `postgres:16`; (2) `environment` con `${POSTGRES_USER}`, `${POSTGRES_PASSWORD}` y `${POSTGRES_DB}` y el volumen con nombre `pgdata` montado en `/var/lib/postgresql/data`, declarado al final del fichero; (3) `healthcheck` con `pg_isready`.
  - Error corregido durante el paso: el bloque `healthcheck` se escribió fuera del servicio (sin la sangría que lo hace hijo de `db`). Se detecta con `config --quiet` y se arregla subiéndolo a 4 espacios dentro de `db`.
  - Sin `--env-file`, `config` avisa de que las variables no están definidas; Compose solo lee `.env` automáticamente, no `.env.dev`.
- **Verificación (observable):**
  - `dc ps`: `randomlocke-dev-db-1` en estado `healthy`, columna PORTS `5432/tcp` (sin publicar).
  - `psql` dentro del contenedor: `PostgreSQL 16.15`. Es el comando de prueba de conexión que exige el enunciado.
  - `docker ps`: sin mapeo de puertos.
  - `nc -zv localhost 5432`: `Connection refused`, es decir, `db` no es accesible desde fuera.
- **Decisiones:**
  - `environment` con interpolación, no `env_file`: cada servicio recibe solo las variables que necesita (mínimo privilegio).
  - Volumen con nombre y no *bind mount*: en `/mnt/c` (NTFS) Postgres puede fallar por permisos.
  - `$${...}` en el healthcheck para que las variables las resuelva la shell del contenedor y no Compose; `-U` y `-d` en `pg_isready` para evitar errores `role "root" does not exist` en los logs.
  - Valores del healthcheck: `interval 10s`, `timeout 5s`, `retries 5`, `start_period 20s`.
  - No se publica ningún puerto en `db`; se comprueba con `exec` en lugar de conectar desde el host.
  - `config` solo con `--quiet`: sin esa opción imprimiría la contraseña ya resuelta.
- **Justificación:** la base de datos es el servicio imprescindible de la arquitectura y se valida aislada antes de añadir la web. El volumen cubre la persistencia del enunciado, el healthcheck permite que `web` espere a `db` (paso 1.4) y la ausencia de `ports` cumple que solo `web` se publique.
- **Asistencia de IA:** Claude Code (app de escritorio), modelo Claude Sonnet 5.5 (`claude-sonnet-5-5`). Finalidad: explicar los conceptos, dar el compose por piezas, revisar el fichero escrito por el alumno y corregir la sangría del healthcheck. Parte del trabajo: Fase 1, servicio `db` de dev.
- **Commit:** `feat(dev): add PostgreSQL service with persistent volume and healthcheck`

### [Decisión fuera de paso: alineación con el temario]
- **Fecha:** 2026-10-10
- **Archivos:** ninguno (revisión de documentación)
- **Qué se hizo:** se compararon los Temas 3 (Git), 4 (Arquitecturas Cloud) y 5 (Contenedores) de la asignatura con el plan. Solo se pudo leer el texto de los PDF (las páginas que son imágenes del Tema 5 quedaron sin leer) y el Tema 4 solo por palabras clave. El plan sigue el enunciado y cubre las buenas prácticas del Tema 5; no se cambia ninguna decisión cerrada.
- **Decisiones:** para la defensa, el proyecto se describe como un monolito con servicios de apoyo (web + BD + caché), no como microservicios.
- **Asistencia de IA:** Claude Code (app de escritorio), modelo Claude Sonnet 5.5 (`claude-sonnet-5-5`). Finalidad: contrastar el plan con el temario y explicar monolito, microservicios y Trivy. Parte del trabajo: revisión de alineación del proyecto.
- **Commit:** se incluirá con el commit del Paso 1.3.

### [Paso 1.3: imagen de la web con una app mínima]
- **Fecha:** 2026-10-10
- **Archivos:** `app/requirements.txt`, `app/main.py`, `app/.dockerignore`, `app/Dockerfile`
- **Comandos:** `docker run --rm python:3.12-slim pip index versions fastapi` (y `uvicorn`), `docker run --rm -v "$PWD/app":/app python:3.12-slim pip install --dry-run -r /app/requirements.txt`, `docker run --rm -v "$PWD/app":/app python:3.12-slim python -m py_compile /app/main.py`, `docker build -t randomlocke-web:test ./app` (dos veces), `docker run --rm randomlocke-web:test whoami`, `docker run --rm -d -p 8000:8000 --name web-test randomlocke-web:test`, `curl -i http://localhost:8000/`, `docker exec web-test whoami`, `docker stop web-test`
- **Qué se ha hecho y cómo:**
  - `requirements.txt` con `fastapi==0.143.0` y `uvicorn==0.54.0`, versiones consultadas con `pip index versions` dentro de una imagen `python:3.12-slim` y validadas con `pip install --dry-run`, sin instalar nada en el equipo.
  - `main.py`: aplicación FastAPI con un único endpoint `GET /` que devuelve un JSON. Todavía no usa la BD (paso 1.4).
  - `.dockerignore` (en `app/`, que es el contexto de build): excluye cachés de Python, entornos virtuales, `.env` y `.env.*`, metadatos de Git y de VS Code, y el propio `Dockerfile`.
  - `Dockerfile`: base `python:3.12-slim`; `ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1`; `WORKDIR /app`; `requirements.txt` copiado e instalado **antes** que el código (capa de dependencias propia, `--no-cache-dir`); usuario `appuser` (sistema, sin home, sin shell, UID 10001); `COPY . .`; `USER appuser`; `EXPOSE 8000`; `CMD` en forma *exec* con Uvicorn en `0.0.0.0:8000`.
- **Verificación (observable):**
  - Construcción: 5,7 s la primera vez y 0,3 s la segunda, con las tres capas iniciales en `CACHED`.
  - `whoami` devuelve `appuser` con `docker run` y con `docker exec`, es decir, el proceso no corre como root.
  - `curl -i http://localhost:8000/` devuelve `HTTP/1.1 200 OK` y `{"mensaje":"Tracker Randomlocke funcionando"}`.
- **Decisiones:**
  - `slim` y no `alpine` para Python, para evitar problemas de compatibilidad de paquetes; solo se fijan las dependencias directas.
  - El código se copia sin `--chown`: pertenece a `root` y `appuser` solo puede leerlo, de modo que la app no puede modificar su propio código.
  - `CMD` en forma *exec* (Uvicorn recibe las señales de parada) y `--host 0.0.0.0` (con `127.0.0.1` el puerto publicado no llegaría a la app).
  - `HEALTHCHECK` no va en el `Dockerfile`: se define en el compose (paso 1.5). Una sola etapa de build: un *multi-stage* no aporta nada con dependencias sin compilar.
- **Tropiezos:** (1) `requirements.txt` creado por error en `app/static/` (carpeta pública) en vez de `app/`; se detectó porque la verificación no lo encontraba. (2) `Dockerfile` creado como carpeta vacía en lugar de fichero; se detectó con `ls` y se corrigió. (3) Un `curl` lanzado justo tras `docker run -d` no devolvió nada: Uvicorn aún no escuchaba; con una espera de 3 s respondió `200`. (4) La extensión EditorConfig no estaba aplicándose: faltaba el salto de línea final en `main.py`.
- **Justificación:** la web es el único servicio que publicará puerto, así que su imagen debe ser reproducible (versiones fijas), pequeña, sin secretos y sin privilegios. La capa de dependencias aparte hace que reconstruir tras un cambio de código sea casi instantáneo.
- **Asistencia de IA:** Claude Code (app de escritorio), modelo Claude Sonnet 5.5 (`claude-sonnet-5-5`). Finalidad: explicar el Dockerfile por piezas, dar el código en trozos, comprobar los ficheros escritos por el alumno y detectar los errores de ubicación y de tipo. Parte del trabajo: Fase 1, imagen de la web.
- **Commit:** `feat(web): add FastAPI base image with non-root user`

### [Paso 1.4: web en Compose, único puerto publicado y /status real]
- **Fecha:** 2026-10-10
- **Archivos:** `docker-compose.dev.yml` (servicio `web`), `app/requirements.txt` (`psycopg[binary]==3.3.6`), `app/main.py` (variables de entorno, conexión a la BD y endpoint `/status`)
- **Comandos:** `docker run --rm python:3.12-slim pip index versions psycopg`, `docker run --rm -v "$PWD/app":/app python:3.12-slim pip install --dry-run -r /app/requirements.txt`, `dc up -d --build`, `dc ps`, `curl -i http://localhost:8000/status`, `dc stop db`, `dc start db`, `docker run --rm randomlocke-dev-web` y `docker run --rm -e DB_HOST=db -e POSTGRES_USER=x -e POSTGRES_DB=x randomlocke-dev-web` (prueba del *fail fast*). `dc` es el alias `docker compose --env-file .env.dev -f docker-compose.dev.yml`.
- **Qué se ha hecho y cómo:**
  - Servicio `web` en el compose: `build: ./app`, `ports: "${WEB_PORT}:8000"` (el único servicio con `ports`), `environment` con `DB_HOST`, `POSTGRES_USER`, `POSTGRES_PASSWORD` y `POSTGRES_DB`, y `depends_on: db: condition: service_healthy`.
  - `main.py` lee la configuración con `os.environ[...]` y `comprobar_db()` abre una conexión nueva con `psycopg.connect(..., connect_timeout=2)` y ejecuta `SELECT 1`. `/status` devuelve `{"db":"ok"}` con 200, o `{"db":"down"}` con 503.
  - La web llega a la base de datos por el nombre de servicio `db`: Compose crea la red `randomlocke-dev_default` con DNS interno.
- **Verificación (observable):**
  - BD arriba: `200 OK`, `{"db":"ok"}`.
  - Tras `dc stop db`: `503 Service Unavailable`, `{"db":"down"}`; `web` siguió `Up` (sin reiniciarse) mientras la BD estaba parada.
  - Tras `dc start db`: `200 OK`, `{"db":"ok"}`, sin reiniciar la web.
  - `dc ps`: `web` con `0.0.0.0:8000->8000/tcp` y `db` con `5432/tcp` (sin publicar).
  - Al arrancar, Compose mostró `db` en `Healthy` antes de `web` en `Started`: la espera por el healthcheck funciona.
  - Sin variables de entorno, `web` falla de inmediato con `KeyError: 'DB_HOST'`, y con solo la contraseña omitida, con `KeyError: 'POSTGRES_PASSWORD'` (*fail fast*).
- **Decisiones:**
  - `depends_on` con `service_healthy`, no solo orden de arranque: `web` espera a que Postgres acepte conexiones.
  - Conexión nueva por cada comprobación (no *pool*): no hay conexiones caducadas tras reiniciarse la BD, así que `/status` se recupera solo; el `connect_timeout` evita que se cuelgue.
  - BD caída → 503 (decisión 7 del plan); `/status` no devuelve el mensaje de error para no filtrar detalles internos.
  - `psycopg[binary]`: evita compiladores en la imagen `slim`.
  - Variables con `os.environ[...]` (sin valores por defecto): fallo rápido y ninguna credencial en el código.
- **Tropiezos:** comandos pegados mientras otro escribía (`dc dc ps`, `ddc ps`); un `curl` cuyo cuerpo no se veía por la falta de salto de línea final de la respuesta, resuelto con `curl -s -w "\nHTTP %{http_code}\n"`.
- **Justificación:** la web es el único punto de entrada de la arquitectura y la BD es imprescindible, así que `/status` debe reflejar en tiempo real su disponibilidad. La red interna de Compose y el DNS por nombre de servicio evitan publicar el puerto de la BD.
- **Asistencia de IA:** Claude Code (app de escritorio), modelo Claude Sonnet 5.5 (`claude-sonnet-5-5`). Finalidad: explicar el servicio `web` en el compose, `psycopg`, el *fail fast* y la conexión por petición; dar el código en piezas y revisar lo escrito por el alumno. Parte del trabajo: Fase 1, conexión web–BD.
- **Commit:** `feat(dev): connect web to database with real /status endpoint`

### [Paso 1.5: healthcheck de la web]
- **Fecha:** 2026-10-10
- **Archivos:** `docker-compose.dev.yml` (bloque `healthcheck` del servicio `web`)
- **Comandos:** `dc config --quiet`, `dc up -d --build`, `dc ps`, `dc stop db`, `dc ps`, `dc start db`, `dc ps`. `dc` es el alias `docker compose --env-file .env.dev -f docker-compose.dev.yml`.
- **Qué se ha hecho y cómo:**
  - Healthcheck de `web` en el compose: `["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/status', timeout=3)"]`, con `interval 10s`, `timeout 5s`, `retries 3` y `start_period 10s`.
  - `urlopen` lanza una excepción ante un error HTTP (como 503) o un tiempo agotado, y el comando termina con código distinto de 0, que Docker cuenta como fallo.
- **Verificación (observable):**
  - Con todo en marcha: `db` `Up 2 hours (healthy)` y `web` `Up 20 seconds (healthy)`.
  - Tras `dc stop db`: `web` pasó a `Up About a minute (unhealthy)`, porque `/status` devuelve 503.
  - Tras `dc start db`: `db` `healthy` y `web` volvió a `Up About a minute (healthy)` **sin reiniciarse** (el contador de actividad no se reinició).
- **Decisiones:**
  - Python (`urllib`) en lugar de instalar `curl`: la imagen `slim` no lo trae y así no se añaden paquetes ni superficie de ataque, ni se modifica el `Dockerfile`.
  - Healthcheck definido en el compose (como el de `db`) y no en el `Dockerfile`, con `CMD` y no `CMD-SHELL` porque no hay variables que expandir.
  - `localhost:8000` dentro del healthcheck (se ejecuta dentro de `web`, donde la app escucha siempre en 8000), distinto del `db` que usa `main.py` para llegar a otro contenedor.
  - Semántica (decisión 7): BD caída → `/status` 503 → `web` `unhealthy`; una futura caída solo de la caché dará 200 con `degraded` y `web` seguirá `healthy`.
  - Compose no reinicia contenedores `unhealthy`: el estado es informativo y lo usan los `depends_on` y los orquestadores.
- **Tropiezos:** al copiar la instrucción se perdió el bloque de código; se aclaró con el fichero completo y la regla de la sangría (`healthcheck:` es hermano de `depends_on`, no hijo).
- **Justificación:** el enunciado exige healthcheck en todos los contenedores y que su estado se refleje en la aplicación; `web` deriva su salud de `/status`, que consulta la BD de forma real, de modo que el estado de salud del contenedor refleja el de sus dependencias.
- **Asistencia de IA:** Claude Code (app de escritorio), modelo Claude Sonnet 5.5 (`claude-sonnet-5-5`). Finalidad: comparar las opciones de healthcheck, dar el bloque y revisar el compose del alumno. Parte del trabajo: Fase 1, healthcheck de la web.
- **Commit:** `feat(web): add healthcheck to web container`

### [Paso 1.6: Makefile mínimo]
- **Fecha:** 2026-10-10
- **Archivos:** `Makefile` (en la raíz del proyecto)
- **Comandos:** `cat -A Makefile` (comprobar tabuladores), `make -n up-dev` y `make -n down ps logs` (ensayo en seco), `make down`, `docker volume ls | grep pgdata`, `make up-dev`, `make ps`, `curl -s -w "\nHTTP %{http_code}\n" http://localhost:8000/status`
- **Qué se ha hecho y cómo:**
  - Variable `COMPOSE_DEV = docker compose --env-file .env.dev -f docker-compose.dev.yml` con el comando base escrito una sola vez, y los targets `build`, `up-dev` (`up -d --build`), `down`, `ps` y `logs` (`logs -f --tail=50`), todos declarados en `.PHONY`. Sustituye al `alias dc`, que se perdía al cerrar la terminal.
  - El nombre de proyecto lo fija `name: randomlocke-dev` dentro del compose, así que no se repite con `-p`.
- **Verificación (observable), desde cero:**
  - `make down` y después `docker volume ls | grep pgdata`: sigue existiendo `randomlocke-dev_pgdata` (decisión 8: `down` conserva los datos).
  - `make up-dev` y `make ps`: `db` `Up (healthy)` (`5432/tcp`, sin publicar) y `web` `Up (healthy)` (`0.0.0.0:8000->8000/tcp`).
  - `curl` a `/status`: `{"db":"ok"}` con `HTTP 200`.
- **Decisiones:**
  - `make down` no borra volúmenes; el borrado de datos irá en `make clean` (paso 3.4).
  - El `Makefile` va en la raíz y no en `app/`: orquesta todo el proyecto y sus rutas (`-f docker-compose.dev.yml`, `--env-file .env.dev`) son relativas a la raíz. `Dockerfile`, `main.py` y `requirements.txt` sí van en `app/`, porque forman parte de la imagen de `web`.
- **Tropiezos:** (1) el `Makefile` quedó en algún momento sin la receta de `up-dev` (el target existía pero sin comando) y `make -n up-dev` dijo `Nothing to be done for 'up-dev'`; se detectó con `cat -A` y `make -n` y se añadió la línea con tabulador. (2) Duda inicial sobre su ubicación (raíz, no `app/`).
- **Justificación:** el enunciado exige automatizar construir, levantar y detener el entorno. Un único sitio con el comando evita olvidar el `--env-file` o mezclar entornos, y hace el despliegue reproducible con `make up-dev`.
- **Asistencia de IA:** Claude Code (app de escritorio), modelo Claude Sonnet 5.5 (`claude-sonnet-5-5`). Finalidad: explicar `make`, `.PHONY` y el tabulador, dar el Makefile por piezas, revisarlo con `cat -A` y `make -n` y detectar la receta ausente. Parte del trabajo: Fase 1, automatización de dev.
- **Commit:** `build: add Makefile with build, up-dev, down, ps and logs targets`

> **Puerta A (esqueleto andante) cumplida:** dev levanta con un solo comando (`make up-dev`), solo `web` publica puerto, `/status` refleja la BD en tiempo real y todos los contenedores quedan `healthy`. Etiqueta sugerida: `v0.1-esqueleto`.

### [Paso 2.1: esquema e inicialización automática]
- **Fecha:** 2026-10-11
- **Archivos:** `app/schema.sql` (nuevo), `app/main.py` (inicialización al arrancar), `Makefile` (target `clean`, adelantado desde el paso 3.4)
- **Comandos:** `make -n clean`, `cat -A Makefile`, `docker compose ... exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < app/schema.sql` (dos veces) y `\dt`, `make clean`, `make up-dev`, `make down`, `make ps`, `curl -s -w "\nHTTP %{http_code}\n" http://localhost:8000/status`, `docker compose ... logs web`; prueba final de recreación (ejecutada por la IA a petición del alumno): `DROP TABLE encounters, runs;`, `\dt`, `docker compose ... restart web`, `\dt`.
- **Qué se ha hecho y cómo:**
  - **Decisión 5 cerrada: opción B**, SQL idempotente al arrancar la app. La alternativa `initdb.d` solo se ejecuta con el volumen vacío y obligaría a borrar los datos para cambiar el esquema.
  - `app/schema.sql`: `runs` (`id` identity, `name`, `created_at`) y `encounters` (`id` identity, `run_id` con clave foránea a `runs`, `event_type` con `CHECK` en `captura`/`fallo`/`muerte`, `route`, `species`, `created_at`, `details JSONB`) con `CREATE TABLE IF NOT EXISTS`, más `idx_encounters_run_id`.
  - `main.py`: `conectar()` centraliza la conexión; `inicializar_db()` lee `schema.sql` y lo ejecuta con hasta 10 intentos separados por 2 s; el `lifespan` de FastAPI lo llama al arrancar. `comprobar_db()` reutiliza `conectar()`.
  - `Makefile`: `make clean` ejecuta `down -v` (borra también el volumen) tras imprimir un aviso; `.PHONY` actualizado. Sin confirmación interactiva: `make` usa `dash`, que no soporta `read -p`.
- **Modelo de datos (acordado):** *append-only*; el equipo activo no se guarda, se deriva (capturas sin muerte posterior). La **ruta** vincula captura y muerte (en un Nuzlocke solo hay una captura por ruta); la API validará en el paso 2.2 que no haya una segunda captura en la misma ruta ni una muerte en una ruta sin captura. `species` es el nombre de la especie (no el tipo): los tipos, si algún día se necesitan, irían en `details`.
- **Verificación (observable):**
  - Aplicar `schema.sql` dos veces con `psql`: la segunda da `NOTICE: relation ... already exists, skipping` (idempotente). `\dt` lista `runs` y `encounters`.
  - `make down` y `make up-dev` con el volumen lleno: `web` arranca sin errores y `/status` devuelve `{"db":"ok"}` con 200.
  - **Prueba de recreación:** `DROP TABLE encounters, runs;` deja `Did not find any relations`; tras `restart web` (sin tocar `db`, `Up 6 minutes`) vuelven a existir `encounters` y `runs`, creadas por la propia aplicación.
- **Decisiones:**
  - Restricciones en la base de datos (`NOT NULL`, `CHECK`, clave foránea) como segunda línea de defensa: la API valida, pero la BD tampoco admite datos inválidos.
  - `TEXT` con `CHECK` y no `ENUM`: añadir un tipo de evento es más fácil. `GENERATED ALWAYS AS IDENTITY` en lugar de `SERIAL`.
  - Reintentos al arrancar, además del `depends_on: service_healthy`, para el caso de que `web` se reinicie con la BD caída.
  - `make clean` adelantado: la verificación del plan necesita probar desde cero.
- **Tropiezos:** (1) el `Makefile` pegado en el chat tenía el target `clean`, pero no estaba guardado en disco (`No rule to make target 'clean'`); se detectó con `make -n clean`. (2) No se podía asegurar que las tablas las hubiera creado la app y no el `schema.sql` aplicado a mano antes, por lo que se añadió la prueba de borrar las tablas y reiniciar `web`.
- **Justificación:** el enunciado exige que la BD se inicialice automáticamente o al arrancar la aplicación. Hacerlo desde la web, de forma idempotente, mantiene el esquema sincronizado con el código sin perder datos y funciona igual con volúmenes nuevos o ya llenos.
- **Asistencia de IA:** Claude Code (app de escritorio), modelo Claude Sonnet 5.5 (`claude-sonnet-5-5`). Finalidad: explicar la decisión 5 y el modelo de datos, dar el SQL y el código en piezas, y ejecutar a petición del alumno la prueba de borrado y recreación de tablas en la BD de desarrollo (vacía). Parte del trabajo: Fase 2, esquema e inicialización.
- **Commit:** `feat(db): add runs/encounters schema with idempotent init on startup`

### [Paso 2.2: endpoints del MVP]
- **Fecha:** 2026-10-11
- **Archivos:** `app/main.py` (endpoints), `app/schema.sql` (índice `uq_encounters_primer_encuentro`)
- **Comandos:** `make up-dev` / `docker compose ... up -d --build`, `curl -s -w "\nHTTP %{http_code}\n" -X POST http://localhost:8000/runs ...`, `curl ... POST /runs/1/events ...` (varios casos), `curl -s http://localhost:8000/runs/1/team`, `curl -s http://localhost:8000/runs/1/graveyard`, `psql ... "\d encounters"` y `SELECT ... FROM encounters`. Varias pruebas las ejecutó la IA a petición del alumno, siempre sobre la BD de desarrollo.
- **Qué se ha hecho y cómo:**
  - `POST /runs` (201, `RETURNING`), con modelo Pydantic `RunNueva` (`min_length=1`, `max_length=100`, espacios recortados).
  - `POST /runs/{id}/events` con `EventoNuevo` (`event_type` ∈ {`captura`, `fallo`, `muerte`} con `Literal`): `404` si la partida no existe, `409` ante un segundo resultado de primer encuentro en la ruta, una muerte sin captura previa o una segunda muerte, y `409` también si salta el índice único (`UniqueViolation`).
  - `GET /runs/{id}/team` (capturas sin muerte en su ruta, con `NOT EXISTS`) y `GET /runs/{id}/graveyard` (capturas con muerte en su ruta, con *self join*; la especie sale de la captura).
  - `conectar()` con `row_factory=dict_row`; `existe_run()` compartida por los tres endpoints.
  - Todas las consultas están parametrizadas (`%s`).
- **Verificación (observable):**
  - Inyección SQL: crear una partida con el nombre `x'; DROP TABLE runs; --` devuelve `201` y se guarda como texto; `runs` sigue existiendo. Nombre vacío → `422`.
  - Reglas: captura en Ruta 1 → `201`; segunda captura → `409`; fallo en Ruta 2 → `201`; muerte en Ruta 2 sin captura → `409`; tipo `huida` → `422`; partida 999 → `404`.
  - Índice único: un `INSERT` directo de un segundo primer encuentro en Ruta 1 falla con `duplicate key value violates unique constraint "uq_encounters_primer_encuentro"`.
  - **Prueba del plan:** antes de la muerte, el equipo contiene Charmander (Ruta 1) y el cementerio está vacío. Tras registrar la muerte en Ruta 1 (`201`), el equipo pasa a `[]` y el cementerio contiene Charmander con `muerto_en`. Una segunda muerte en Ruta 1 → `409` («El Pokémon de esa ruta ya murió»).
- **Decisiones:**
  - Consultas parametrizadas: prevención de inyección SQL; los datos nunca se concatenan al SQL.
  - Validación en dos capas: Pydantic en la API (mensajes claros y barata) y restricciones en la BD (`NOT NULL`, `CHECK`, clave foránea, índice único) como segunda línea.
  - Los eventos no se modifican (*append-only*): una muerte es un `INSERT`, y el equipo y el cementerio se derivan.
  - La ruta vincula captura y muerte; la especie del cementerio sale de la captura para que cada Pokémon tenga un solo nombre.
  - Solo el primer encuentro tiene índice único; «una sola muerte por ruta» se comprueba únicamente en la API, para no atar el esquema a una regla que podría ser configurable (opción de la Fase 4).
  - Códigos HTTP: 201 creado, 404 inexistente, 409 conflicto con las reglas, 422 entrada inválida.
- **Tropiezos:** (1) `Literal` sin importar en `main.py` (habría provocado `NameError` al arrancar); detectado en la revisión antes de reconstruir. (2) Importación de FastAPI duplicada. (3) Los endpoints de la pieza 3 no estaban guardados en disco cuando se pidió la revisión. (4) El `id` 3 de `encounters` no existe: lo consumió el `INSERT` directo que rechazó el índice único; las secuencias *identity* no reutilizan números aunque la inserción falle.
- **Limitación conocida:** `"Ruta 1"` y `"ruta 1"` son rutas distintas; normalizar mayúsculas sería una mejora.
- **Justificación:** convierte la web en una aplicación útil sin romper el modelo *append-only* acordado, aplica las reglas del Nuzlocke con mensajes claros y deja la integridad garantizada por la base de datos aunque la API falle.
- **Asistencia de IA:** Claude Code (app de escritorio), modelo Claude Sonnet 5.5 (`claude-sonnet-5-5`). Finalidad: explicar las consultas parametrizadas, la validación y las consultas derivadas; dar el código en piezas; revisar el código del alumno; hacer un pequeño refactor de `existe_run` y el índice de `schema.sql` a petición suya; y ejecutar varias pruebas HTTP y SQL en la BD de desarrollo. Parte del trabajo: Fase 2, API del MVP.
- **Commit:** `feat(api): add runs, events, active team and graveyard endpoints`

### [Paso 2.3: interfaz estática]
- **Fecha:** 2026-10-11
- **Archivos:** `app/static/index.html`, `app/static/style.css`, `app/static/app.js` (nuevos); `app/main.py` (montaje de `static/`, `GET /runs` y `GET /runs/{id}/encounters`, eliminado el `GET /` que devolvía un JSON)
- **Comandos:** `touch app/static/style.css app/static/app.js`, `docker compose ... up -d --build`, `curl` a `/`, `/style.css`, `/app.js` y a la API, `docker compose ... stop db` y `start db`. La verificación en el navegador (panel integrado) la ejecutó la IA a petición del alumno, sobre la BD de desarrollo.
- **Qué se ha hecho y cómo:**
  - **La API sirve la interfaz:** `app.mount("/", StaticFiles(directory=..., html=True))` **al final** de `main.py` (los montajes se evalúan por orden y uno en `/` captura todo). Se eliminó el antiguo `GET /`, que tapaba `index.html`. Mismo origen, por lo que no hace falta CORS, y un solo contenedor y un solo puerto publicado.
  - **API ampliada:** `GET /runs` (lista de partidas) y `GET /runs/{id}/encounters` (todos los eventos, para las capturas por ruta).
  - **Interfaz:** HTML, CSS y JavaScript sin frameworks. Cabecera con el **indicador de estado** (círculo verde/rojo/gris y texto), selector y formulario de partida, formulario de eventos y tres bloques: **Pokémon vivos**, **Capturas por ruta** y **Cementerio**. Secciones dependientes de una partida con `hidden`; `<script>` al final del `body`; una sola columna para el móvil.
  - **Estado en vivo:** *polling* con `fetch("/status", { cache: "no-store" })` cada 3 s; distingue «BD caída» (la web responde `503` con JSON) de «Sin conexión con la web» (`catch`).
  - **Datos y formularios:** `pedir()` envuelve `fetch` y convierte los errores de la API en mensajes legibles; los `5xx` muestran «El servidor no puede acceder a la base de datos ahora mismo»; los datos del usuario se escriben siempre con `textContent` o `new Option`, nunca con `innerHTML`.
- **Verificación (observable, en el navegador):**
  - Carga: las dos partidas en el desplegable, con el nombre `x'; DROP TABLE runs; --` mostrado como texto. Consola sin errores.
  - Partida 1: *Ruta 1 captura (muerto) Charmander*, *Ruta 2 fallo Rattata*, vivos vacío y cementerio con Charmander.
  - Registrar: captura en Ruta 3 (Squirtle) → aparece en vivos y tabla; captura repetida → «Esa ruta ya tiene un resultado de primer encuentro»; muerte en Ruta 9 → «No hay ninguna captura en esa ruta»; muerte en Ruta 3 → pasa al cementerio; segunda muerte → «El Pokémon de esa ruta ya murió».
  - **XSS:** una partida llamada `<b>hola</b><img src=x onerror="window.__xss=1">` y un evento con especie `<img src=x onerror="window.__xss=2">` se muestran literales: `window.__xss` sigue en `0` y no se creó ningún `<img>` ni `<b>`.
  - **Estado en vivo (requisito del enunciado):** con `docker compose stop db`, el círculo pasa a rojo («BD caída») sin recargar la página (tipo de navegación `navigate`); con `start db` vuelve a verde.
  - Con la BD parada, la interfaz muestra «El servidor no puede acceder a la base de datos ahora mismo. Inténtalo de nuevo.».
- **Decisiones:**
  - **Interfaz servida por la propia API:** una sola web, un solo puerto, sin CORS (la política del mismo origen bloquearía las peticiones si estuviera en otro puerto).
  - **Sección «Pokémon vivos» y no «Equipo»:** la consulta devuelve el equipo y la PC; el límite de 6 es una regla de honor que la aplicación no comprueba.
  - ***Polling* cada 3 s** y no WebSockets ni Server-Sent Events: más simple y suficiente para un indicador de estado.
  - `textContent` y no `innerHTML` por seguridad (XSS); mensajes de error de la API mostrados al usuario.
- **Hallazgo:** con la BD parada, la API tarda ~3,1 s en responder (`connect_timeout=2` más el reintento del DNS), `GET /status` da `503` y un `POST` da `500` con texto plano; la interfaz mostraba «Solicitud no válida» (engañoso), corregido con la rama `status >= 500` de `pedir()`. El indicador tarda unos segundos en cambiar (respuesta más intervalo), compatible con el `timeout: 5s` del healthcheck.
- **Mejora aplicada tras la verificación (recuperación automática):** al principio, al volver la BD, el indicador pasaba a verde pero la página no recargaba los datos ni borraba el mensaje de error hasta que se refrescaba. Se añadió `dbAnterior` (recuerda el estado de la comprobación anterior) y, cuando `/status` pasa de «caída» a «conectada» (`dbOk && dbAnterior === false`), `recuperar()` borra el mensaje y vuelve a cargar las partidas conservando la elegida. También cuenta como «caída» que la propia web no responda. Comprobado en el navegador sin recargar la página (el tipo de navegación sigue siendo `navigate`): (a) con una partida abierta y un mensaje de error por la BD caída, al arrancar la BD el mensaje desaparece y los datos se recargan; (b) cargando la página con la BD ya caída (desplegable vacío y mensaje rojo), al arrancar la BD el desplegable se rellena solo.
- **Tropiezos:** (1) carpeta vacía `app;C` creada por error en la raíz (un trozo de ruta de Windows pegado como nombre), inofensiva. (2) El editor mantuvo una copia antigua de `main.py` con el punto sin guardar y el aviso «el contenido del archivo es más reciente»; se resolvió cerrando la pestaña sin guardar y reabriéndola. (3) Una afirmación errónea mía sobre las líneas en blanco del fichero, corregida. (4) El mensaje de error vivía dentro de una sección oculta y se movió bajo `<main>`.
- **Justificación:** el enunciado exige que la aplicación muestre el estado de la BD y de la caché y que refleje dinámicamente cuándo un servicio deja de estar disponible; una interfaz servida por la propia web, con *polling* del endpoint `/status`, lo cumple con un único contenedor y un único puerto publicado.
- **Asistencia de IA:** Claude Code (app de escritorio), modelo Claude Sonnet 5.5 (`claude-sonnet-5-5`). Finalidad: explicar `StaticFiles`, el mismo origen y CORS, el *polling* y XSS; dar el código en piezas; aplicar a petición del alumno los cambios de `main.py` y `index.html`; y ejecutar la verificación en el navegador integrado. Parte del trabajo: Fase 2, interfaz estática.
- **Commit:** `feat(ui): add static interface with live status, vivos, routes and graveyard`

### [Paso 2.4: prueba de persistencia en dev]
- **Fecha:** 2026-10-11
- **Archivos:** `docs/pruebas.md` (nuevo, escrito por el alumno con las salidas reales)
- **Comandos:** `alias dc='docker compose --env-file .env.dev -f docker-compose.dev.yml'`; `curl -X POST /runs` y `POST /runs/{id}/events` (datos marcados); `docker inspect -f 'ID: {{printf "%.12s" .Id}}  CREADO: {{.Created}}' randomlocke-dev-db-1`; `docker volume ls | grep pgdata`; `dc exec db ... psql ... "SELECT (SELECT count(*) FROM runs) AS partidas, (SELECT count(*) FROM encounters) AS eventos;"`; `curl /runs/{id}/team`; **`dc rm -s -f db`** (elimina solo el contenedor); `docker ps -a --filter name=db-1`; `curl /status`; `dc up -d db`. La prueba la ejecutó el alumno; la IA revisó cada salida y repitió los `GET` de lectura para contrastarla.
- **Qué se ha hecho y cómo:** se creó una partida marcada (`id=4`, «Persistencia 20261011-140538») con una captura (Eevee en «Ruta Persistencia») y se anotó el estado de la BD; se eliminó el **contenedor** `db` sin tocar el volumen; se comprobó que el volumen seguía y que la web notaba la caída; se recreó el contenedor y se comparó el estado.
- **Verificación (observable):**
  - ID del contenedor `db`: `2335b1affc07` (creado `2026-10-10T21:54:39Z`) → **`44e9376fb8b5`** (creado `2026-10-11T15:15:00Z`): es un contenedor nuevo.
  - Volumen: `randomlocke-dev_pgdata` antes, durante y después.
  - Filas: **4 partidas y 7 eventos** antes y después.
  - API: Eevee en la partida 4 con la misma fecha (`2026-10-11T12:05:52Z`).
  - Con el contenedor eliminado: `/status` → `503` `{"db":"down"}`; tras recrearlo: `200` `{"db":"ok"}`. `web` pasó a `unhealthy` y volvió a `healthy` sin reiniciarse.
- **Decisiones:**
  - Se elimina el contenedor con `docker compose rm -s -f db` (conserva red y volumen) y no con `down -v` ni `make clean`, que borrarían el volumen.
  - Los datos de prueba llevan una marca con la fecha para que la comprobación sea inequívoca.
  - La evidencia queda en `docs/pruebas.md` para el README (apartado de pruebas y verificaciones).
- **Tropiezos:** (1) `docs/pruebas.md` no existía cuando el alumno dio el paso por hecho; se creó después. (2) Un `curl .../team` lanzado a los segundos de recrear `db` salió vacío (la BD estaba en `health: starting` y `web` aún `unhealthy`); repetido con la BD `healthy` devolvió a Eevee.
- **Justificación:** es el requisito central del enunciado («insertando información, eliminando el contenedor y volviéndolo a iniciar, verificando que los datos se mantienen») y la razón de usar un volumen con nombre: el contenedor es desechable y los datos viven en el volumen.
- **Asistencia de IA:** Claude Code (app de escritorio), modelo Claude Sonnet 5.5 (`claude-sonnet-5-5`). Finalidad: diseñar la prueba por pasos con evidencia comprobable, explicar la diferencia entre eliminar el contenedor y el volumen, y revisar las salidas. Parte del trabajo: Fase 2, persistencia en dev.
- **Commit:** `docs: add persistence test evidence for dev`

> **Fase 2 (MVP en dev) cerrada.** Resumen en `docs/resumenes/fase-2.md`.

### [Paso 3.1: .env.prod y docker-compose.prod.yml]
- **Fecha:** 2026-10-11
- **Archivos:** `.env.prod.example` (versionado); `.env.prod` (real, ignorado por Git, no versionado); `docker-compose.prod.yml`
- **Comandos:** `cp .env.prod.example .env.prod`, `openssl rand -base64 24` (dos contraseñas distintas entre sí y de las de dev), `chmod 600 .env.prod`, `grep -n "PASSWORD" .env.prod.example` (comprobar que la plantilla solo tiene valores ficticios), `git check-ignore -v .env.prod`, `docker compose --env-file .env.prod -f docker-compose.prod.yml config --quiet`, `... up -d db`, `... up -d cache`, `... up -d --build`, `... ps`, `... exec cache sh -c 'REDISCLI_AUTH=$REDIS_PASSWORD redis-cli ping'`, `... exec cache redis-cli ping`, `... exec cache ... redis-cli config get save`, `... exec db ... psql ... "\dt"`, `docker ps --format "table {{.Names}}\t{{.Ports}}"`, `curl http://localhost:8080/status`.
- **Variables de prod (solo nombres):** `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` (`tracker_prod`), `DB_HOST`, `WEB_PORT` (8080), `CACHE_ENABLED` (`true`), `CACHE_HOST` (`cache`), `REDIS_PASSWORD`.
- **Qué se ha hecho y cómo:**
  - Plantilla `.env.prod.example` con valores ficticios y `.env.prod` real con contraseñas aleatorias propias. Se comprobó antes de versionar que la plantilla solo contenía los valores ficticios (la incidencia del paso 1.1 no se repitió) y que `.gitignore` (línea 4) ignora `.env.prod`.
  - `docker-compose.prod.yml` con `name: randomlocke-prod` y tres servicios: `db` (PostgreSQL 16 con volumen y healthcheck, como en dev), `cache` (`redis:7-alpine`) y `web` (`build: ./app`, con `WEB_PORT`, las variables de la caché y `depends_on` con `service_healthy` sobre `db` y `cache`). Los tres con `restart: unless-stopped`.
  - Redis arranca con `sh -c 'exec redis-server --requirepass "$$REDIS_PASSWORD" --save "" --appendonly no'`: contraseña por variable de entorno (el YAML no contiene valores), proceso principal con `exec` y **sin persistencia** (es una caché reconstruible). Su healthcheck usa `REDISCLI_AUTH` y `grep -q PONG`, no `redis-cli -a`.
- **Verificación (observable):**
  - `config --quiet` sin salida. Los tres servicios `healthy`; solo `web` publica puerto (`0.0.0.0:8080->8000/tcp`); `db` (`5432/tcp`) y `cache` (`6379/tcp`) no.
  - Redis: con contraseña, `PONG`; sin ella, `(error) NOAUTH Authentication required.`; `config get save` devuelve una cadena vacía.
  - `curl http://localhost:8080/status` → `{"db":"ok"}` con 200; `GET /` sirve la interfaz.
  - La web creó el esquema en la BD de prod, que estaba vacía (`\dt` muestra `runs` y `encounters`): la decisión 5-B también funciona en prod.
  - **Convivencia de los dos entornos:** `docker ps` muestra a la vez `randomlocke-dev-*` (puerto 8000) y `randomlocke-prod-*` (puerto 8080), con bases de datos independientes: `/runs` en prod devuelve `[]` mientras que en dev devuelve las partidas de prueba.
- **Decisiones:**
  - Dos ficheros de Compose independientes (decisión 6), aun con algo de duplicación: cada entorno se entiende sin abrir el otro.
  - `name`, puerto, nombre de la BD y contraseñas propios en prod: no se pisan contenedores, red ni volúmenes (`randomlocke-prod_pgdata`), y las credenciales de un entorno no comprometen las del otro.
  - `restart: unless-stopped` solo en prod. No reinicia contenedores `unhealthy`, solo los que terminan.
  - Redis con contraseña aunque no publique puerto (defensa en profundidad: cualquier otro contenedor de la red podría usarlo) y sin persistencia.
  - `build: ./app` en ambos entornos: Compose crea una imagen por proyecto (`randomlocke-dev-web`, `randomlocke-prod-web`).
- **Tropiezos:** (1) el bloque `web` no se había guardado en disco; `up -d --build` no mostró ningún paso de construcción y `curl` dio `HTTP 000` (nada escuchando en el puerto). Se detectó con `grep -n -E "^  [a-z]+:"` sobre el fichero y se resolvió guardando. (2) Dev estaba parado cuando se dijo que los dos entornos aparecerían juntos; la convivencia se comprobó después, arrancando dev.
- **Limitación conocida:** hasta el paso 3.3 la aplicación todavía no usa Redis; las variables de la caché llegan a `web` pero no tienen efecto.
- **Justificación:** el entorno de producción añade el servicio de caché del enunciado (solo en prod) con las mismas medidas de seguridad que el resto: credenciales por variable de entorno, solo `web` expuesto y healthchecks en todos los contenedores.
- **Asistencia de IA:** Claude Code (app de escritorio), modelo Claude Sonnet 5.5 (`claude-sonnet-5-5`). Finalidad: explicar las diferencias entre dev y prod, la política de reinicio y la configuración segura de Redis; dar el compose por piezas, y revisar los ficheros del alumno y su verificación. Parte del trabajo: Fase 3, entorno de producción.
- **Commit:** `feat(prod): add production compose with Redis and its own variables`

### [Paso 3.2: aislamiento de red]
- **Fecha:** 2026-10-13
- **Archivos:** `docker-compose.prod.yml` (claves `networks:` de `db`, `cache` y `web`, y bloque `networks:` final)
- **Comandos:** `grep -n -E "^networks:|^  frontend:|^  backend:|internal:|^      - (frontend|backend)$|^    networks:" docker-compose.prod.yml`, `docker compose --env-file .env.prod -f docker-compose.prod.yml config --quiet`, `... down`, `... up -d`, `... ps`, `docker network ls | grep randomlocke-prod`, `docker network inspect randomlocke-prod_backend -f '{{.Internal}}'`, `docker network inspect <red> -f '{{range .Containers}}{{.Name}} {{end}}'`, `... exec cache sh -c 'wget -q -T 3 -O- http://example.com ...'`, `... exec web python -c "import urllib.request; urllib.request.urlopen('http://example.com', timeout=3)"`, `curl http://localhost:8080/status`, `... exec web python -c "import socket; socket.create_connection(('cache', 6379), timeout=3)"`.
- **Qué se ha hecho y cómo:** se definieron dos redes: `frontend` (normal) y `backend` (`internal: true`). `db` y `cache` solo están en `backend`; `web` está en las dos y actúa de puente. Se bajó prod con `down` (conserva volúmenes) y se recreó con `up -d`: Compose creó `randomlocke-prod_backend` y `randomlocke-prod_frontend`.
- **Verificación (observable):**
  - `docker network inspect randomlocke-prod_backend -f '{{.Internal}}'` → `true`. `backend` contiene `web`, `cache` y `db`; `frontend`, solo `web`.
  - Desde `cache`: `wget: bad address 'example.com'` → «sin salida a internet». Desde `web`: «web SI sale a internet».
  - `/status` → `{"db":"ok"}` con 200 y `web` abre una conexión a `cache:6379` («web alcanza cache»).
  - Los tres contenedores `healthy`; solo `web` publica puerto (`0.0.0.0:8080->8000/tcp`).
  - **Efecto de `restart: unless-stopped` tras apagar el ordenador:** al volver, los contenedores de prod seguían `Up (healthy)` mientras los de dev estaban `Exited (255)`.
- **Decisiones:**
  - Una red `internal: true` no permite publicar puertos ni salir al exterior; por eso `web` está en dos redes (publica por `frontend` y habla con `db` y `cache` por `backend`).
  - Endurecimiento solo en prod. En dev (solo `web` y `db`) se mantiene la red por defecto, que ya cumple «una red interna donde se comunican»; replicarlo allí es opcional.
  - `db` y `cache` sin salida a internet: aplicar el mínimo privilegio a la red. Un `docker pull` no se ve afectado, porque lo hace el demonio de Docker en el host y no el contenedor.
- **Detalle:** `randomlocke-prod_default` (la red antigua) quedó huérfana, porque `down` solo borra las redes definidas en el fichero actual. Está vacía y es inofensiva; se puede quitar con `docker network rm randomlocke-prod_default`.
- **Limitación conocida:** `web` está en las dos redes, así que es la pieza más delicada: comprometerla da acceso a `db`, `cache` e internet. Mitigaciones ya aplicadas: usuario sin root, código de solo lectura y credenciales solo por variables de entorno. Endurecimientos posibles fuera de alcance: `read_only: true` y `cap_drop` en `web`.
- **Justificación:** el enunciado exige que solo la aplicación web pueda exponerse y que los demás servicios sean accesibles únicamente desde la red interna; las dos redes lo garantizan estructuralmente, además de no publicar sus puertos.
- **Asistencia de IA:** Claude Code (app de escritorio), modelo Claude Sonnet 5.5 (`claude-sonnet-5-5`). Finalidad: explicar las redes `internal`, proponer la topología de dos redes y revisar las pruebas de aislamiento del alumno. Parte del trabajo: Fase 3, aislamiento de red.
- **Commit:** `feat(prod): isolate db and cache in an internal network`

### [Incidencia durante el Paso 3.3: la caché parada tumbaba la web]
- **Fecha:** 2026-10-13
- **Archivos:** `app/main.py` (cliente de Redis, `vigilar_cache()`, `cache_estado`, `comprobar_cache()`, `lifespan`), `app/requirements.txt` (`redis==8.1.0`), `docker-compose.dev.yml` (`CACHE_ENABLED` en `web`); `docker-compose.prod.yml` sin cambios netos (se probó alargar el healthcheck y se revirtió).
- **Comandos:** `docker compose --env-file .env.prod -f docker-compose.prod.yml stop cache`, `curl http://localhost:8080/status` (repetido), `docker compose ... ps`, `docker inspect -f '{{range .State.Health.Log}}...' randomlocke-prod-web-1`, medición dentro de `web` (`socket.getaddrinfo('cache', 6379)` y `cache.ping()`), medición de `redis-py` con y sin reintentos en una red interna temporal, `... up -d --build`, `... stop db`, `... start db`.
- **El problema:** con la caché parada, `web` pasaba a `unhealthy` y `/status` tardaba más de 30 s (a veces sin respuesta). Contradecía la decisión 7: una caché caída debe dar `200` con `degraded` y no tumbar la web.
- **Diagnóstico (medido):** (1) `redis-py` **reintenta por defecto** con esperas crecientes: con la política por defecto, un fallo costaba 4,25 s frente a 0,00 s sin reintentos (en una red interna con un nombre inexistente). (2) **Los `timeout` del cliente no cubren la resolución DNS**, y en Docker Desktop resolver el nombre de un contenedor parado tarda **3-8 s** (medido dentro de `web`: 3,15 s, 7,14 s y 8,01 s). Un `ping` completo costaba ~3,2 s y el primer `/status` tras la caída hasta 8 s. El healthcheck de `web` (`timeout=3`) lo contaba como fallo.
- **Primer intento (descartado):** un temporizador que dejaba de insistir 15 s tras un fallo. `/status` pasó a 8 s la primera vez y 12 ms las siguientes y `web` quedó `healthy`, pero el registro del healthcheck mostraba que **uno de cada dos chequeos fallaba** (`exit=1`, a los ~6 s): la primera petición de cada ventana pagaba la espera y a veces era la del healthcheck. Solo se salvaba porque nunca fallaban tres seguidos (`retries: 3`).
- **Solución adoptada:** (a) `retry=Retry(NoBackoff(), 0)`: sin reintentos. (b) **Un hilo vigilante** lanzado en el `lifespan`: `vigilar_cache()` hace `ping` cada 3 s y guarda `"ok"` o `"caida"` en `cache_estado`; `comprobar_cache()` solo lee esa variable, de modo que ninguna petición de usuario espera nunca a Redis. Estado inicial optimista (`ok`) hasta el primer `ping`; `marcar_cache_caida()` lo marca al instante si una operación real falla. El healthcheck vuelve a sus valores originales (`timeout=3`, `timeout: 5s`).
- **Verificación (observable) tras el arreglo:** con la caché parada, `/status` → `{"estado":"degraded","db":"ok","cache":"caida"}` con `200` en ~12 ms de forma sostenida; `web` `healthy` con 5 chequeos consecutivos `exit=0` y `FailingStreak` 0; al arrancar la caché, `/status` vuelve a `ok` en ~7 s. Contraste: con la BD parada, `{"estado":"down","db":"down","cache":"ok"}` con `503`; al volver, `ok` y `200`.
- **Observación:** con la BD parada, `/status` tardó 8,0 s (el mismo DNS lento): cuando un contenedor desaparece de la red, todo lo que dependa de su nombre se vuelve lento unos segundos. Es coherente con el comportamiento esperado (BD caída → `unhealthy`).
- **Decisiones:** una comprobación de salud de un servicio opcional no puede estar en el camino de las peticiones: se mueve a un hilo en segundo plano que escribe en una variable. El estado inicial es optimista. No se usa un *circuit breaker* de temporizador: limita la espera pero alguien la paga.
- **Explicación con analogía (para repasar):** el camarero (`web`) comprobaba la libreta (Redis) antes de cada cliente; con la libreta perdida, la comprobación tardaba muchísimo; ahora un ayudante (el hilo) mira la libreta cada 3 s y apunta en una pizarra (`cache_estado`), y el camarero solo lee la pizarra. Detalle completo en `docs/conceptos-para-estudiar.md`.
- **Asistencia de IA:** Claude Code (app de escritorio), modelo Claude Sonnet 5.5 (`claude-sonnet-5-5`). Finalidad: diagnosticar el fallo con mediciones, proponer y descartar una solución intermedia, implementar la solución del hilo vigilante y explicarlo con una analogía. Parte del trabajo: Fase 3, caché (pieza 1).
- **Commit:** incluido en el commit del paso 3.3.

### [Paso 3.3: caché cache-aside con Redis]
- **Fecha:** 2026-10-13
- **Archivos:** `app/main.py` (cliente Redis, `leer_equipo`, `invalidar_equipo`, `/status`, cabeceras `X-Cache`, `X-Cache-TTL` y `X-Latency-Ms`), `app/requirements.txt` (`redis==8.1.0`), `docker-compose.dev.yml` (`CACHE_ENABLED`), `app/static/index.html`, `app/static/app.js`, `app/static/style.css` (origen, latencia, TTL e indicador de la caché).
- **Comandos:** `docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build web`, `... stop cache` / `... start cache`, `curl -si http://localhost:8080/runs/<id>/team` (lectura de cabeceras), `psql` dentro de `db` con un `INSERT` directo (prueba del TTL), `... exec db sh -c "psql ..."`, y comprobaciones en el navegador (prod en 8080 y dev en 8000).
- **Qué se ha hecho y cómo:** (1) conexión a Redis y `/status` con el estado de la caché (hilo vigilante, ver la incidencia anterior); (2) lectura del equipo activo con *cache-aside*: clave `team:<run_id>`, valor JSON, TTL de 30 s; (3) invalidación con `DEL` **después del COMMIT** (fuera del `with conectar()`); (4) degradación a PostgreSQL si Redis cae; (5) la interfaz muestra «Origen: caché | base de datos · ms · caduca en s» y un segundo indicador de caché (`conectada`, `caída`, `no aplica`).
- **Verificación (observable):**
  - MISS (13,2 ms) → HIT (0,7 ms) con el TTL bajando (30 → 22).
  - Registrar una captura invalida: la lectura siguiente es MISS con los datos nuevos. Un registro rechazado (`409`) **no** invalida (sigue HIT). Una muerte hace que el Pokémon desaparezca del equipo.
  - Con la caché parada: registrar un evento da `201` y la lectura sale `DEGRADED`; al volver, MISS y luego HIT.
  - **TTL como red de seguridad:** un `INSERT` directo en la BD (sin API) no invalida: lectura inmediata HIT (TTL 29) **sin** el dato nuevo; tras `sleep 32`, MISS **con** el dato.
  - Interfaz en prod: origen base de datos → caché → base de datos tras registrar; con la caché parada, «Origen: base de datos · caché caída» y círculo rojo `Caché: caída` sin recargar. En dev: «no aplica» (gris) y `X-Cache: OFF`.
- **Decisiones:** invalidar tras el COMMIT (si fuera antes, una lectura intermedia podría volver a cachear el dato viejo; el TTL es solo la red de seguridad); se invalida con cualquier evento por simplicidad; `pedirConCabeceras` devuelve cuerpo y cabeceras en lugar de una variable global (`Promise.all` la dejaría apuntando a otra petición); el beneficio de la caché a esta escala es sobre todo pedagógico.
- **Tropiezos:** la caché parada tumbaba la web (ver la incidencia anterior); un primer borrador del cambio de interfaz con variable global estaba mal planteado y se corrigió; en la prueba del TTL con comandos manuales la entrada caducó entre pasos (30 s es poco para teclear), por lo que se repitió en un solo bloque.
- **Justificación:** el enunciado exige demostrar una caché en prod. *Cache-aside* con invalidación tras el commit, degradación a PostgreSQL y estado visible en la UI cumplen el diseño de §6 de `idea-y-alcance.md` y la decisión 7.
- **Asistencia de IA:** Claude Code (app de escritorio), modelo Claude Sonnet 5.5 (`claude-sonnet-5-5`). Finalidad: explicar *cache-aside* y la invalidación, revisar el código del alumno, aplicar y verificar la pieza 5 (interfaz) a petición suya y ejecutar las pruebas de verificación. Parte del trabajo: Fase 3, caché.
- **Commit:** `feat(cache): add cache-aside for active team with invalidation after commit`

### [Paso 3.4: Makefile completo y verificación en limpio]
- **Fecha:** 2026-10-13
- **Archivos:** `Makefile` (variables `COMPOSE_DEV` y `COMPOSE_PROD`, doce targets por entorno y `down`), `docs/conceptos-para-estudiar.md`, `docs/diario-de-desarrollo.md`, `docs/resumenes/fase-3.md`.
- **Comandos:** `make -n up-prod`, `make -n down-dev`, `make -n clean-prod`, `make -n down` (ensayo en seco), `make ps-dev`, `make ps-prod`; verificación en limpio: `git clone` en `RedesAvanzadas/prueba-limpia`, `cp .env.prod.example .env.prod` + `sed` (contraseñas aleatorias y `WEB_PORT=8081`), `COMPOSE_PROJECT_NAME=prueba-limpia make up-prod`, `... make ps-prod`, `curl /status`, `POST /runs`, dos `GET /runs/1/team`, `COMPOSE_PROJECT_NAME=prueba-limpia make clean-prod` y `rm -rf prueba-limpia`.
- **Qué se ha hecho y cómo:** el Makefile pasa a tener targets por entorno (`build`, `up`, `down`, `ps`, `logs`, `clean`, cada uno con sufijo `-dev` o `-prod`) y `make down`, que baja los dos entornos conservando los datos. `clean` no tiene versión conjunta: `clean-dev` y `clean-prod` avisan, cada uno con su mensaje, antes de `down -v`. Después se clonó el repositorio desde GitHub en una carpeta nueva, sin ningún `.env` real, y se levantó prod desde las plantillas.
- **Verificación (observable):**
  - Clon sin `.env` reales: `make clean-prod` falló con «couldn't find env file» (prueba de que no viaja ningún secreto en el repo); tras crear `.env.prod` desde la plantilla, `make up-prod` creó imagen, redes `frontend` y `backend`, volumen y los tres contenedores.
  - `db`, `cache` y `web` en `healthy`; solo `web` publica puerto (`0.0.0.0:8081->8000`); `/status` → `{"estado":"ok","db":"ok","cache":"ok"}`; crear partida y leer el equipo dos veces → `MISS` y `HIT`.
  - Limpieza solo del proyecto de prueba, y el prod real (`randomlocke-prod`, puerto 8080) siguió `healthy` durante toda la prueba.
- **Decisiones:** nombres de target por entorno para no confundir dev con prod; `make down` baja ambos (conserva volúmenes, decisión 8) pero `clean` nunca se junta, porque borra datos; la verificación se aisló con `COMPOSE_PROJECT_NAME=prueba-limpia` y el puerto 8081, para no reutilizar el volumen del prod real ni parar sus contenedores.
- **Limitación honesta:** las capas de la imagen salieron `CACHED` (el Docker ya las tenía), así que no fue un *build* sin caché de Docker; sí fue un despliegue desde cero en cuanto a repositorio, `.env`, redes y volumen.
- **Tropiezo:** se ejecutó el paso de limpieza antes de crear el `.env.prod` y falló sin consecuencias (no existía el fichero y, además, el nombre de proyecto lo aislaba del prod real).
- **Justificación:** el enunciado pide automatizar con Make (`up-dev`, `up-prod`, `down`) y poder reproducir el despliegue desde una instalación limpia; los targets por entorno y la verificación en limpio lo demuestran.
- **Asistencia de IA:** Claude Code (app de escritorio), modelo Claude Sonnet 5.5 (`claude-sonnet-5-5`). Finalidad: proponer la convención de targets, escribir el Makefile a petición del alumno, diseñar la verificación en limpio con aislamiento de proyecto y revisar sus resultados. Parte del trabajo: Fase 3, automatización y verificación.
- **Commit:** `build: add per-environment make targets and down for both` (el Makefile) y `docs: close phase 3 with step 3.4 diary, concepts and summary`.

### [Paso 4.1: revisión de seguridad]
- **Fecha:** 2026-10-13
- **Archivos:** `docker-compose.prod.yml` (`user: redis` en `cache`, `ENABLE_DOCS` en `web`), `docker-compose.dev.yml` (`ENABLE_DOCS` en `web`), `app/main.py` (`ENABLE_DOCS` y `docs_url`, `redoc_url`, `openapi_url` condicionales), `.env.dev.example`, `.env.prod.example` y los `.env` reales (solo se añadió el nombre `ENABLE_DOCS` con su valor).
- **Comandos:** `git ls-files | grep -i -E "\.env|claude\.md|\.pdf|..."`, `git log --all --diff-filter=A --name-only`, `git check-ignore -v`, `git ls-files -z | xargs -0 grep -i -E "password|secret|token|api[_-]?key"`, `docker compose ... ps`, `docker ps --filter name=randomlocke-prod --format ...`, `docker top <contenedor>`, `docker exec <contenedor> grep -E "^(Uid|Gid):" /proc/1/status`, `curl -s -o /dev/null -w '%{http_code}' localhost:<puerto>/docs` (y `/redoc`, `/openapi.json`), `docker compose ... config --quiet`, `docker compose ... up -d --build`, `ls -l .env.dev .env.prod`.
- **Revisión (resultado):**
  - Solo las plantillas `.env.*.example` están versionadas, ahora y en todo el historial; `.env.dev`, `.env.prod`, `CLAUDE.md` y `Practica1.pdf` están ignorados.
  - Sin credenciales en código ni YAML: solo `${VAR}`, `os.environ` y los valores ficticios `cambia_esto` de las plantillas.
  - Solo `web` publica puerto (`8080` en prod); `db` y `cache` no.
  - Procesos: `web` uid 10001 (sin root), `db` uid 999 (`postgres`); **`cache` corría como `root`**.
  - **`/docs`, `/redoc` y `/openapi.json` respondían `200` en prod.**
  - Permisos de los `.env`: `-rw-r--r--` (644).
- **Correcciones aplicadas:**
  - **Redis sin root:** `user: redis` en el servicio `cache`. La imagen oficial solo baja de privilegios si arranca `redis-server` directamente; nuestro `command: ["sh","-c","exec redis-server ..."]` (para leer la contraseña de la variable) se lo saltaba. Verificado: `docker inspect` → `redis`, proceso uid 999, contenedor `healthy`, `/status` `ok` y `MISS` → `HIT`.
  - **Documentación interactiva desactivada en prod:** variable `ENABLE_DOCS` (por defecto `false`: seguro por defecto), `true` en dev y `false` en prod. Verificado: prod → `/docs`, `/redoc` y `/openapi.json` dan `404`; dev → `200`.
- **Limitación aceptada y documentada:** los `.env` quedan en 644. WSL monta `C:\` (`drvfs`) sin la opción `metadata`, así que `chmod 600` no tiene efecto sobre NTFS. En un servidor Linux se aplicaría `chmod 600 .env.*`; se explicará con honestidad en el README. Alternativa más robusta descartada por el momento del proyecto: trabajar desde el sistema de ficheros de WSL.
- **Decisiones:** seguro por defecto (sin la variable, no hay documentación); `ENABLE_DOCS` como variable y no «desactivar si hay caché», para no acoplar dos cosas distintas; `db` ya baja de privilegios por la imagen oficial.
- **Justificación:** el enunciado pide credenciales fuera del código, puertos mínimos y permisos mínimos; la revisión lo comprueba con evidencia y reduce la superficie de ataque de prod (menos privilegios en Redis, API no autodocumentada).
- **Asistencia de IA:** Claude Code (app de escritorio), modelo Claude Sonnet 5.5 (`claude-sonnet-5-5`). Finalidad: diseñar y ejecutar la revisión, detectar Redis como root y la documentación expuesta, aplicar y verificar los arreglos a petición del alumno. Parte del trabajo: Fase 4, seguridad.
- **Commit:** `chore(security): run redis as non-root and disable api docs in prod`

### [Paso 4.2: pruebas y evidencias]
- **Fecha:** 2026-10-14
- **Archivos:** `docs/pruebas.md` (secciones 2 a 10 nuevas; la 1, persistencia en dev, ya existía).
- **Comandos:** `make ps-dev`, `make ps-prod`, `make down`, `make up-dev`, `make up-prod` (ejecutados con `wsl -e make`), `curl localhost:8080/status` (y `:8000`), conexión TCP a `localhost:5432` y `:6379`, `docker compose stop|start cache|db`, `docker compose exec db psql -c "SELECT 1" -c "\dt"`, `docker compose rm -s -f db` y `up -d db`, `docker inspect`, `docker volume ls`, `curl -X POST /runs` y `/runs/<id>/events`, `curl -si /runs/<id>/team` (cabeceras `X-Cache`, `X-Cache-TTL`, `X-Latency-Ms`), `INSERT` directo con `psql`.
- **Qué se ha hecho y cómo:** se ejecutó de forma ordenada toda la lista de verificaciones de §11 de `idea-y-alcance.md` y se guardó la salida real en `docs/pruebas.md`, con una tabla final que enlaza cada requisito con su sección. Las pruebas las ejecutó la IA a petición del alumno (que había elegido hacerlas él y cambió de opinión); las salidas son reales y no contienen credenciales.
- **Verificación (observable):**
  - Los cinco contenedores `healthy`; solo `web` publica puerto; desde el host 5432 y 6379 rechazan la conexión.
  - `/status`: caché parada → `200 degraded`; BD parada → `503 down`; ambos se recuperan solos.
  - Persistencia en prod: el contenedor de la BD cambia (`dc80222da005` → `c4abb313400c`), el volumen es el mismo y las filas también (4 partidas y 12 eventos antes y después).
  - Caché: `MISS` (16,8 ms) → `HIT` (0,9 ms); registrar invalida; un `409` no invalida; un `INSERT` directo no invalida y el dato viejo se sirve hasta que caduca el TTL; con Redis parado, `201` y `X-Cache: DEGRADED`.
  - `make down` conserva el volumen: tras `up-dev` y `up-prod`, 5 partidas y 16 eventos.
- **Pendiente del alumno:** capturas de pantalla de la interfaz (todo operativo, caché parada y BD parada) para el README, p. ej. en `docs/img/`.
- **Justificación:** el enunciado exige entregar resultados de pruebas y verificaciones en el README; reunirlos con la salida real permite defenderlos y reutilizarlos tal cual.
- **Asistencia de IA:** Claude Code (app de escritorio), modelo Claude Sonnet 5.5 (`claude-sonnet-5-5`). Finalidad: ejecutar las pruebas de verificación, recoger las salidas y redactar `docs/pruebas.md`. Parte del trabajo: Fase 4, pruebas y evidencias.
- **Commit:** `docs: add verification results for prod, cache and make targets`


### [Decisión fuera de paso: se incorpora a la práctica el Paso 3.5, autocompletado de especies con caché (pendiente de implementar)]
- **Fecha:** 2026-10-14
- **Archivos:** ninguno todavía (solo planificación). Se tocarán `app/main.py`, `app/schema.sql`, `app/static/*` y se añadirá un fichero de datos en `app/`.
- **Motivo de la decisión:** dar un uso más claro a la caché. Hoy se cachea el equipo activo (pocas filas; beneficio pequeño y reconocido). Una lista de especies de referencia es el caso clásico: **solo lectura**, ~1000 filas y **una consulta por cada tecla** que se escribe. Encaja con el enunciado («almacenar datos temporalmente y reducir consultas a la base de datos») y usa a la vez los tres servicios: la lista vive en **PostgreSQL**, la sirve la **API** y **Redis** la cachea. Además evita escribir nombres inventados y hace la interfaz más cómoda.
- **Alcance respecto al plan original:** amplía el MVP con una funcionalidad pequeña que no estaba en `idea-y-alcance.md`. Respeta el riesgo R4 («no depender de APIs externas; usar datos locales»): la lista se descarga **una sola vez** y se guarda en el repositorio, solo texto (§1.6: ningún sprite oficial). Se desarrolla en una **rama** (`feat/autocompletado`) y se fusiona en `main` solo si funciona.
- **Diseño:**
  - **Datos:** fichero fuente en `app/` con los nombres de especie (descargado una vez de una fuente pública como PokéAPI; fuente concreta e idioma por decidir al implementarlo).
  - **BD:** tabla `species` creada de forma idempotente en `schema.sql` y cargada al arrancar desde el fichero con `INSERT ... ON CONFLICT DO NOTHING`, igual que el esquema; sobrevive a `make clean-*` porque se recarga sola.
  - **API:** `GET /species?q=zub`: búsqueda por prefijo, sin distinguir mayúsculas, con límite de resultados, consulta parametrizada y escape de `%` y `_`. En prod, *cache-aside* con clave `species:<prefijo>` y un **TTL largo** (p. ej. 1 h) **sin invalidación**, porque los datos no cambian durante la ejecución. Devuelve las cabeceras `X-Cache` y `X-Latency-Ms`. En dev (sin caché) consulta directamente la BD (`X-Cache: OFF`). Si Redis cae, degrada a PostgreSQL como el equipo activo.
  - **Interfaz:** campo «Especie» con `<input list>` y `<datalist>` relleno con las sugerencias (con un pequeño retardo para no lanzar una petición por tecla; opciones creadas con `new Option`, nunca `innerHTML`).
- **Decisiones que se cerrarán al implementar:** idioma de los nombres (español o inglés) y si solo **sugiere** (propuesta por defecto: los *randomizers* pueden producir formas que la lista no recoja) o **valida**.
- **Plan por piezas (una por turno, con verificación):**
  1. Datos: descargar la lista, limpiarla y guardarla en `app/` (solo nombres).
  2. Esquema y carga: tabla `species` en `schema.sql` y carga al arrancar.
  3. Endpoint `GET /species` sin caché (dev), con pruebas de prefijo, mayúsculas, límite, caracteres especiales y entrada vacía.
  4. Caché del endpoint en prod (*cache-aside*, TTL largo, degradación).
  5. Interfaz con `<datalist>` y retardo.
  6. Verificación completa y documentación.
- **Verificación esperada:** dev: sugerencias correctas y `X-Cache: OFF`; prod: primera búsqueda de un prefijo `MISS` y las siguientes `HIT` (ms); con la caché parada, `DEGRADED` y las sugerencias siguen funcionando; tras `make clean-prod` y `make up-prod` la tabla se recarga sola; el XSS sigue sin ejecutarse en las sugerencias.
- **Documentación que habrá que actualizar al terminar:** entrada del diario del Paso 3.5, cuaderno de conceptos (entrada «Autocompletado de especies con caché», ya marcada como pendiente), nueva sección de `docs/pruebas.md`, `docs/resumenes/fase-3.md` (ampliación de la sección de la caché), `docs/resumenes/chuleta-de-comandos.md` y el README.
- **Plazo y criterio de abandono:** las funcionalidades se congelan el 15 de octubre por la noche. Si el 15 a las 20:00 no está verificada en prod, se descarta con la rama sin tocar `main` y esta entrada pasa a ideas futuras. La práctica ya está completa sin ella.
- **Orden de trabajo acordado:** datos de demostración (seed), **autocompletado**, capturas (para que salgan las sugerencias), README, entrega.
- **Asistencia de IA:** Claude Code (app de escritorio), modelo Claude Sonnet 5.5 (`claude-sonnet-5-5`). Finalidad: evaluar la idea frente a la caché y al alcance, diseñar la solución y planificarla. Parte del trabajo: Fase 3, ampliación de la caché.

### [Paso 3.5, piezas 1 a 3: datos, tabla `species` y endpoint `GET /species`]
- **Fecha:** 2026-10-14
- **Archivos:** `app/species.csv` (nuevo), `app/schema.sql` (tabla `species` e índice), `app/main.py` (`import csv`, `SPECIES`, `cargar_especies`, `escapar_like`, endpoint `buscar_especies`). Rama `feat/autocompletado`.
- **Comandos:** `git switch -c feat/autocompletado`; `{ echo "id,name"; curl -sL <pokemon_species_names.csv de PokéAPI> | awk -F, '$2==7 {print $1","$3}'; } > app/species.csv`; `wc -l`, `head`, `sed -n`, `tail`; `make up-dev`; `docker compose ... exec -T db psql ... SELECT count(*) FROM species`; `restart web`; `EXPLAIN` con `SET enable_seqscan = off`; `curl -G --data-urlencode "q=..." localhost:8000/species`; `git push -u origin feat/autocompletado`.
- **Qué se ha hecho y cómo:**
  - **Pieza 1 (datos):** se descargó una sola vez el fichero de nombres de especie de PokéAPI y se filtró el idioma español (`local_language_id = 7`, comprobado en `languages.csv`) a `app/species.csv` con dos columnas `id,name` (1025 especies; solo texto, sin imágenes).
  - **Pieza 2 (tabla y carga):** tabla `species (id INTEGER PRIMARY KEY, name TEXT NOT NULL)` con índice `ON species (lower(name) text_pattern_ops)` para búsquedas por prefijo; `cargar_especies(conn)` lee el CSV y hace `INSERT ... ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name` con `executemany`, dentro del bucle de reintentos de `inicializar_db` y en la misma transacción que el esquema.
  - **Pieza 3 (endpoint):** `GET /species?q=<prefijo>&limit=<n>` devuelve una lista de nombres. Valida con `Query` (`q` de 1 a 50 caracteres, `limit` de 1 a 20, 10 por defecto), recorta espacios y pasa a minúsculas, escapa `\`, `%` y `_` con `escapar_like`, y consulta con parámetros `%s`, `ORDER BY name` y `LIMIT`.
- **Verificación (observable, dev):**
  - Tabla: `count(*)` = 1025; `lower(name) LIKE 'zub%'` → `41 | Zubat`; tras `restart web` sigue en 1025 (carga idempotente).
  - Índice: `EXPLAIN` con `seqscan` desactivado → `Index Scan using idx_species_nombre`, con `Index Cond: (lower(name) ~>=~ 'zub') AND (lower(name) ~<~ 'zuc')`.
  - Endpoint: `zub`, `ZUB` y `"  zub  "` → `["Zubat"]`; `flab` → `["Flabébé"]`; `pi` → 10 resultados alfabéticos; `pi` con `limit=3` → 3; `mew` → `["Mew","Mewtwo"]`.
  - Entrada hostil: `%`, `_`, `\`, `xyz` y `x'; DROP TABLE species; --` → `[]` con 200 y la tabla sigue con 1025 filas; solo espacios → `[]`.
  - Validación: sin `q`, `q` vacía, `q` de 60 caracteres, `limit=99` y `limit=0` → `422`.
  - Prod aún devuelve `404` en `/species` (no reconstruida; se actualiza con la pieza 4).
- **Decisiones:** idioma **español**; el autocompletado **solo sugiere** (no valida) porque en un Randomlocke pueden aparecer formas que la lista no recoja; clave `id` de la Pokédex para que la carga sea un *upsert*; respuesta como lista de textos (lo más simple para el `<datalist>`); sin caché todavía (pieza 4). `text_pattern_ops` porque la ordenación de la BD no es «C» y sin él el `LIKE 'zub%'` no podría usar el índice.
- **Pendiente:** pieza 4 (caché del endpoint), pieza 5 (interfaz), pieza 6 (verificación en dev y prod, y documentación final) y fusionar en `main`. Plazo: 15 de octubre a las 20:00.
- **Asistencia de IA:** Claude Code (app de escritorio), modelo Claude Sonnet 5.5 (`claude-sonnet-5-5`). Finalidad: investigar el formato de la fuente de datos, diseñar la tabla, el índice y el endpoint, aplicar los cambios de la pieza 3 a petición del alumno y ejecutar las pruebas. Parte del trabajo: Fase 3, ampliación de la caché.
- **Commit:** `feat(species): add local list of species names in Spanish`, `feat(species): create species table and load names on startup` y `feat(species): add GET /species prefix search endpoint`.

### [Paso 3.5, pieza 4: caché del endpoint `/species`]
- **Fecha:** 2026-10-14
- **Archivos:** `app/main.py`.
- **Comandos:** `docker compose ... up -d --build web` (prod y dev); `curl -si -G localhost:8080/species --data-urlencode "q=..."` (cabeceras `X-Cache`, `X-Cache-TTL`, `X-Latency-Ms`); `redis-cli --scan --pattern "species:*"` y `TTL` dentro del contenedor `cache`; `docker compose stop cache` / `start cache`; peticiones de regresión al equipo activo.
- **Qué se ha hecho y cómo:** la lógica *cache-aside* de `leer_equipo` se extrajo a una función genérica `leer_con_cache(clave, ttl_s, consultar)`, usada ahora por `leer_equipo` (clave `team:<id>`, TTL 30 s, se invalida al registrar un evento) y por la nueva `leer_especies` (clave `species:<prefijo>:<límite>`, TTL 3600 s, sin invalidación). Las cabeceras se ponen con `poner_cabeceras_cache`. Se renombró `CACHE_TTL_S` a `CACHE_EQUIPO_TTL_S` y se añadió `CACHE_ESPECIES_TTL_S`. Mismo comportamiento de estados: `HIT`, `MISS`, `OFF` (dev) y `DEGRADED` (Redis caído).
- **Verificación (observable):** prod: `zub` `MISS` (21,5 ms) → `HIT` (1,6 ms) con TTL 3600; `ZUB` y `"  zub  "` comparten clave (`HIT`); `limit=3` tiene clave propia; claves `species:zub:10`, `species:zub:3`, `species:pi:10` y `species:%:10` en Redis. Registrar un evento no invalida las especies. Con la caché parada, `DEGRADED` y las sugerencias siguen funcionando; al volver, `MISS` y luego `HIT`. Dev: `X-Cache: OFF`. Regresión del equipo (`MISS`→`HIT`, invalidación al registrar, `409` sin invalidar, `404` sin crear clave) sin cambios.
- **Decisiones:** (1) la clave incluye **todo lo que cambia la respuesta** (prefijo y límite); (2) el prefijo se normaliza (minúsculas y sin espacios) antes de formar la clave, para que `ZUB` y `zub` compartan entrada; (3) TTL largo y sin invalidación, porque los datos son de referencia y no cambian mientras la app corre; (4) una función genérica en lugar de duplicar la lógica, por simplicidad y para que ambas lecturas se comporten igual.
- **Limitación conocida:** cada prefijo distinto crea una clave (también los resultados vacíos, p. ej. `%`) durante una hora; a esta escala es irrelevante, y en un entorno real se acotaría la memoria de Redis (`maxmemory` con política `allkeys-lru`).
- **Asistencia de IA:** Claude Code (app de escritorio), modelo Claude Sonnet 5.5 (`claude-sonnet-5-5`). Finalidad: aplicar a petición del alumno la caché del endpoint y la refactorización, y verificar el comportamiento en prod y dev. Parte del trabajo: Fase 3, ampliación de la caché.
- **Commit:** `feat(species): cache species search in redis with a generic cache-aside helper`

### [Paso 3.5, pieza 5: interfaz con sugerencias al escribir]
- **Fecha:** 2026-10-14
- **Archivos:** `app/static/index.html` (`list="lista-especies"`, `autocomplete="off"` y `<datalist id="lista-especies">` en el campo «Especie»), `app/static/app.js` (`cargarSugerencias`, escucha del evento `input` con retardo).
- **Comandos:** `docker compose ... up -d --build web` (prod y dev; `app/static` va dentro de la imagen); pruebas en el navegador con `javascript_exec`: escribir en el campo, contar `performance.getEntriesByType('resource')`, leer las opciones del `<datalist>`.
- **Qué se ha hecho y cómo:** al escribir en «Especie» se espera 200 ms sin teclear (*debounce*: se cancela el temporizador anterior con `clearTimeout`), se pide `/species?q=<texto>` (con `encodeURIComponent`) y se sustituyen las opciones del `<datalist>` con `new Option(nombre)`. Un contador (`peticionSugerencias`) descarta respuestas antiguas que llegan tarde. Si la petición falla, no se muestra ningún error: las sugerencias son opcionales. Con el campo vacío se limpia la lista.
- **Verificación (observable):** `zubat` tecleado rápido → 1 petición (sin *debounce* serían 5); `pi` → 1 petición y 10 sugerencias; `mew` tecleado despacio → 3 peticiones (`m`, `me`, `mew`); texto con `<img onerror=...>` → ninguna sugerencia y **no se ejecuta nada**; campo vacío → lista vacía; dev: `flab` → `Flabébé` y registrar la captura desde el formulario funciona.
- **Decisiones:** `<datalist>` nativo del navegador en vez de una librería (sin dependencias, accesible); `new Option` y nunca `innerHTML` (XSS, como en el resto de la interfaz); *debounce* de 200 ms para no lanzar una petición por tecla y proteger la BD y la caché; descartar respuestas viejas con un contador para que una respuesta tardía no pise a una más reciente; `autocomplete="off"` para que el navegador no mezcle su historial con nuestras sugerencias; solo sugiere (no valida): se puede registrar cualquier texto.
- **Pendiente:** pieza 6 (verificación completa, recarga de la lista tras `make clean-prod`, resumen del paso) y fusión en `main`.
- **Asistencia de IA:** Claude Code (app de escritorio), modelo Claude Sonnet 5.5 (`claude-sonnet-5-5`). Finalidad: aplicar a petición del alumno los cambios de la interfaz y comprobarlos en el navegador. Parte del trabajo: Fase 3, ampliación de la caché.
- **Commit:** `feat(ui): add species autocomplete with datalist and debounce`

### [Paso 3.5: autocompletado de especies con caché]
- **Fecha:** 2026-10-14
- **Archivos:** `app/species.csv` (nuevo), `app/schema.sql`, `app/main.py`, `app/static/index.html`, `app/static/app.js`. Desarrollado en la rama `feat/autocompletado` y fusionado en `main`.
- **Comandos:** `git switch -c feat/autocompletado`, `git push -u origin feat/autocompletado`, `make up-dev`, `docker compose ... up -d --build web`, `make clean-prod` y `make up-prod` (verificación final), `git switch main`, `git merge feat/autocompletado`, `git push`, `git branch -d feat/autocompletado`, `git push origin --delete feat/autocompletado`; detalle de cada pieza en las entradas anteriores del paso.
- **Qué se ha hecho y cómo:** una lista de ~1000 especies de referencia (nombres en español de PokéAPI, descargados una vez y guardados como `id,name`) se carga al arrancar en la tabla `species` (índice `text_pattern_ops` sobre `lower(name)`, carga con `ON CONFLICT DO UPDATE`); `GET /species?q=&limit=` busca por prefijo; en prod Redis cachea cada búsqueda (`species:<prefijo>:<límite>`, TTL 1 h, sin invalidación) con degradación a PostgreSQL; la interfaz sugiere nombres con un `<datalist>` y un *debounce* de 200 ms. La lógica *cache-aside* se refactorizó en `leer_con_cache`, compartida con el equipo activo.
- **Verificación (observable):** tras `make clean-prod` + `make up-prod` la tabla se recarga sola (`0 partidas, 0 eventos, 1025 especies`); `/species?q=zub` es `MISS` y luego `HIT` en prod y `OFF` en dev; con la caché parada, `DEGRADED` y las sugerencias siguen; el equipo activo no cambió de comportamiento tras el refactor; en el navegador, sobre la base vacía: crear partida, sugerencias para `zub`, `pi` y `flab` y registrar una captura funcionan; `zubat` tecleado deprisa lanza 1 petición (5 sin *debounce*). Evidencias completas en `docs/pruebas.md` §11.
- **Decisiones:** nombres en español; solo sugiere (no valida); lista en la BD cacheada en Redis frente a un fichero estático o una consulta directa a PokéAPI (usa los tres servicios, se actualiza desde un único sitio y no depende de internet); TTL largo sin invalidación porque son datos de referencia; la clave incluye el límite; `leer_con_cache` genérica. Desarrollo en rama con fusión *fast-forward* (Tema 3).
- **Limitación conocida:** cada prefijo distinto crea una clave durante una hora (también los vacíos); a esta escala no importa y en un entorno real se acotaría la memoria de Redis.
- **Justificación:** da un uso claro a la caché (muchas lecturas repetidas de un dato de referencia) y evita nombres mal escritos, integrando la BD, la API, Redis y la interfaz sin romper las decisiones cerradas (datos locales, caché opcional con degradación).
- **Asistencia de IA:** Claude Code (app de escritorio), modelo Claude Sonnet 5.5 (`claude-sonnet-5-5`). Finalidad: investigar la fuente de datos, diseñar y aplicar la tabla, el endpoint, la caché y la interfaz, y ejecutar las verificaciones. Parte del trabajo: Fase 3, ampliación de la caché.
- **Commit:** `feat(species): ...` y `feat(ui): add species autocomplete with datalist and debounce` (6 commits en la rama, fusionados en `main`).

### [Datos de demostración: script local `scripts/seed-demo.sh` (no versionado)]
- **Fecha:** 2026-10-15
- **Archivos:** `scripts/seed-demo.sh` (nuevo, **ignorado por Git**: está en `.gitignore`); `.gitignore`.
- **Comandos:** `bash scripts/seed-demo.sh dev` (y `prod`), `bash -n scripts/seed-demo.sh`, `docker compose ... up -d` (dev estaba parado tras reiniciar el equipo), consultas `curl` a `/runs`, `/runs/<id>/team`, `/graveyard` y `/encounters` para comprobar el resultado.
- **Qué se ha hecho y cómo:** un script de `bash` crea seis partidas de ejemplo (Kanto, Johto, Hoenn, Sinnoh, Teselia y Kalos) con 67 eventos (capturas, fallos y muertes) llamando a la **propia API** con `curl`, de modo que los datos pasan por las mismas validaciones que cualquier usuario (el primer encuentro por ruta, una muerte solo si hay captura, etc.). Los nombres de especie son los de la lista local de `app/species.csv` (se comprobó que todos existen). Es **idempotente**: si una partida con ese nombre ya existe, se omite. Comprueba antes que `/status` responde y devuelve un código de salida distinto de cero si algo falla. Parámetro `prod` (8080, por defecto) o `dev` (8000), o `BASE_URL`.
- **Verificación (observable, dev):** 1.ª ejecución: 6 partidas, 67 eventos, 0 errores; 2.ª ejecución: las seis se omiten (0 creadas); resultado por partida (vivos / cementerio): Kanto 7/4, Johto 3/0, Hoenn 1/7, Sinnoh 7/2, Teselia 6/0, Kalos 1/5; con la web inalcanzable (`BASE_URL=http://localhost:9`) avisa y sale con código 1.
- **Decisiones:** el script **no se versiona** (decisión del alumno): son datos de demostración y no parte de la práctica, así que tampoco hay un `make seed` en el Makefile (un target que llamara a un fichero ausente fallaría en un clon). Se usa la API y no SQL directo para pasar por las validaciones y no depender del esquema.
- **Asistencia de IA:** Claude Code (app de escritorio), modelo Claude Sonnet 5.5 (`claude-sonnet-5-5`). Finalidad: escribir el script de datos de demostración y probarlo en dev. Parte del trabajo: preparación de la demostración.
- **Commit:** solo `.gitignore` (`chore: ignore local demo seed script`); el script no se sube.
