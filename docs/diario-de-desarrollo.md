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

### [Decisión fuera de paso: alineación con el temario y rama en la Fase 2]
- **Fecha:** 2026-10-10
- **Archivos:** ninguno (revisión de documentación)
- **Qué se hizo:** se compararon los Temas 3 (Git), 4 (Arquitecturas Cloud) y 5 (Contenedores) de la asignatura con el plan. Solo se pudo leer el texto de los PDF (las páginas que son imágenes del Tema 5 quedaron sin leer) y el Tema 4 solo por palabras clave. El plan sigue el enunciado y cubre las buenas prácticas del Tema 5; no se cambia ninguna decisión cerrada.
- **Decisiones:** (1) la funcionalidad opcional de la Fase 2, si se llega, se hará en una **rama** y se fusionará en `main`, para practicar el concepto de Git del Tema 3 que aún no se ha usado. (2) Trivy queda como mejora opcional de la Fase 4, pendiente de decidir. (3) Para la defensa, el proyecto se describe como un monolito con servicios de apoyo (web + BD + caché), no como microservicios.
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
- **Modelo de datos (acordado):** *append-only*; el equipo activo no se guarda, se deriva (capturas sin muerte posterior). La **ruta** vincula captura y muerte (en un Nuzlocke solo hay una captura por ruta); la API validará en el paso 2.2 que no haya una segunda captura en la misma ruta ni una muerte en una ruta sin captura. `species` es el nombre de la especie (no el tipo): los tipos, si se implementa la funcionalidad opcional de cobertura, irán en `details`.
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

### [Decisión fuera de paso: reglas configurables por partida, anotadas como opción de la Fase 4]
- **Fecha:** 2026-10-11
- **Archivos:** ninguno (decisión de alcance)
- **Qué se propuso:** que al crear una partida el jugador pueda elegir las reglas de esa run (prohibir objetos curativos, cláusula de especies, vidas por Pokémon, etc.), porque cada comunidad juega el Nuzlocke a su manera.
- **Decisión:** se **anota como opción** para la funcionalidad opcional de la Fase 2 del documento de diseño (Fase 4 de la hoja de ruta, 14-15 oct), a decidir si el MVP se cierra a tiempo. Generaliza la opción «validador de reglas de la run» y se haría en una **rama** (practicar el concepto del Tema 3). El MVP sigue con las reglas fijas del plan. No cambia ninguna decisión cerrada.
- **Diseño previsto:** columna `rules JSONB` en `runs`, añadida con `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` en `schema.sql` (ejemplo práctico de la decisión 5 B). Reglas *comprobables* (primer encuentro, cláusula de especies) con `409`; reglas *de honor* (objetos curativos, nivel máximo) solo informativas; «vidas por Pokémon» queda fuera por cambiar el modelo (distinguir debilitado de muerto).
- **Ajuste inmediato en el MVP:** el paso 2.2 no crea el índice único `uq_encounters_muerte`; la regla «una sola muerte por ruta» se comprueba solo en la API, para no atar el esquema a una regla que podría ser configurable. Se mantiene `uq_encounters_primer_encuentro`.
- **Asistencia de IA:** Claude Code (app de escritorio), modelo Claude Sonnet 5.5 (`claude-sonnet-5-5`). Finalidad: clasificar las reglas según se puedan comprobar y valorar el impacto en el modelo y el calendario. Parte del trabajo: alcance de la Fase 2 opcional.
- **Commit:** se incluirá con el commit del paso 2.2.

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

### [Idea opcional anotada: distinguir equipo y PC]
- **Fecha:** 2026-10-11
- **Archivos:** ninguno (decisión de alcance)
- **Qué se planteó:** el jugador solo lleva 6 Pokémon en el equipo y guarda el resto en la PC; la pregunta era si los de la PC cuentan como «activos».
- **Decisión:** en el MVP, «equipo activo» significa «Pokémon vivos» (equipo y PC), porque la aplicación solo ve eventos `captura`, `fallo` y `muerte`; el límite de 6 es una regla de honor que no se comprueba. Para no inducir a error, la sección de la interfaz (paso 2.3) se llamará **«Pokémon vivos»**. El endpoint `/team` no cambia.
- **Idea opcional anotada** (junto a las reglas configurables por partida, Fase 4, solo si se cierra el MVP a tiempo): distinguir equipo y PC con dos eventos nuevos (`a_caja` y `a_equipo`), derivando el estado del último movimiento (modelo *append-only*), con una migración del `CHECK` de `event_type` (`DROP CONSTRAINT` y volver a crearlo) y cambios en las consultas. Coste alto para poco valor en el MVP.
- **Asistencia de IA:** Claude Code (app de escritorio), modelo Claude Sonnet 5.5 (`claude-sonnet-5-5`). Finalidad: aclarar qué devuelve la consulta del equipo y valorar el coste de modelar equipo y PC. Parte del trabajo: alcance del modelo de datos.
- **Commit:** se incluirá con el siguiente commit.
