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
