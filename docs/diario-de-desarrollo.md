# Diario de desarrollo

Registro paso a paso de la Práctica 1 según la hoja de ruta de `docs/dependencias-y-pasos.md`.

---

### [Paso 0.1: verificar el entorno]
- **Fecha:** 2026-10-08
- **Archivos:** ninguno (paso de verificación)
- **Comandos:**
  - PowerShell: `wsl -l -v`, `docker --version`, `docker compose version`, `docker run --rm hello-world`, `git --version`, `git config --global user.name`, `git config --global user.email`, `netstat -ano | findstr :8000`, `netstat -ano | findstr :8080`, `python --version`
  - WSL (Ubuntu 22.04): `docker --version`, `docker compose version`, `docker run --rm hello-world`, `make --version`, `git --version`, `docker pull python:3.12-slim`, `docker pull postgres:16`, `docker pull redis:7-alpine`, `ssh -T git@github.com`
  - Resultado: WSL2, Docker 29.8.1, Compose v5.5.1, GNU Make 4.3 en WSL y puertos 8000/8080 libres; imágenes base descargadas. Se activó la integración Docker–WSL, que estaba desactivada. SSH a GitHub sin clave: se usará HTTPS.
- **Justificación:** se cierra la decisión 2: `make` y `docker` se ejecutan en WSL (entorno Linux, como los contenedores) y Git en Windows, con HTTPS y Git Credential Manager.
  El riesgo de finales de línea CRLF en el `Makefile` se mitigará en el Paso 0.2 con `.gitattributes` (LF) y `core.autocrlf`.
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

### [Incidencia durante el Paso 0.3: push rechazado]
- **Fecha:** 2026-10-09
- **Archivos:** ninguno modificado por la incidencia
- **Comandos:** `git push` (error 1: `Could not resolve hostname github.com`; error 2: `! [rejected] main -> main (fetch first)`). Diagnóstico previsto, solo lectura: `git fetch origin`, `git log --oneline --graph --all`, `git diff --stat main origin/main`.
- **Justificación:** el primer error fue un fallo de DNS en WSL (ajeno al repositorio y a la clave SSH). El segundo indica que `origin/main` contiene commits que no están en local; Git lo impide para no sobrescribir trabajo ajeno. Regla adoptada: no usar `git push --force` sin saber antes qué contiene el remoto.
- **Resolución:** _pendiente de completar tras revisar el contenido del commit remoto._
- **Asistencia de IA:** Claude Code (app de escritorio), modelo Claude Sonnet 5.5 (`claude-sonnet-5-5`). Finalidad: interpretar los errores y proponer un diagnóstico seguro. Parte del trabajo: Fase 0, publicación del Paso 0.3.
- **Commit:** ninguno por esta incidencia.

