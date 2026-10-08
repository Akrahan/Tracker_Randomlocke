# Dependencias y hoja de ruta de la Práctica 1

> Complementa a `idea-y-alcance.md` (stack, alcance MVP en §3.1 y plan por fechas en §9).
> Este documento **no contiene código de la aplicación**: solo comprobaciones de entorno y el orden de trabajo.
>
> **Entorno de partida:** Windows con VS Code y Docker ya instalados.
> **Fechas clave:** entrega domingo 18 oct · test y exposición lunes 19 oct.

---

## 1. Evaluación del entorno

### 1.1 Qué corre dónde

Principio: **todo lo que ejecuta el servicio vive en contenedores**; en tu máquina solo hacen falta herramientas.

| Componente | Tecnología | Dónde corre | ¿Necesito algo en Windows? |
|---|---|---|---|
| Web/API | Python + FastAPI (servidor Uvicorn) | Contenedor `web` | No. Python local es opcional (solo para autocompletado del editor) |
| Frontend | HTML/CSS/JS sin paso de build | Servido por la propia API | No hace falta Node ni npm |
| Base de datos | PostgreSQL | Contenedor `db` | No. El cliente `psql` viene dentro del contenedor |
| Caché (solo prod) | Redis | Contenedor `cache` | No |
| Orquestación | Docker Compose v2 | Docker Desktop | **Verificar** |
| Automatización | Make | Terminal Linux (WSL) | **Verificar** (no viene en Windows) |
| Control de versiones | Git + GitHub | Local | **Verificar** |

### 1.2 Checklist de verificación (antes de escribir código)

| Qué | Cómo comprobarlo | Resultado esperado |
|---|---|---|
| WSL2 con una distro Linux (p. ej. Ubuntu) | `wsl -l -v` (PowerShell) | La distro aparece con `VERSION 2` |
| Docker Desktop usa WSL2 | Docker Desktop → Settings → General ("Use the WSL 2 based engine") | Activado |
| Integración Docker–WSL | Docker Desktop → Settings → Resources → WSL integration | Activada para tu distro |
| Docker funciona | `docker --version` y `docker run --rm hello-world` | Mensaje de bienvenida |
| Compose v2 | `docker compose version` (con espacio, no `docker-compose`) | Versión 2.x |
| Git | `git --version`; `git config --global user.name` y `user.email` | Versión y datos configurados |
| Acceso a GitHub | Poder hacer `git push` a un repositorio vacío | Push correcto (HTTPS con Credential Manager o SSH) |
| Make | `make --version` dentro de WSL (si falta: `sudo apt install make`) | Versión de GNU Make |
| Puerto libre | PowerShell: `netstat -ano \| findstr :8000` (repetir con el puerto elegido) | Sin resultados |
| Descarga de imágenes | `docker pull` de las imágenes base (ver §1.5) | Descarga correcta; hacerlo ya, por si falla la red |
| Python (opcional) | `python --version` | 3.12 recomendado, para coincidir con la imagen |

### 1.3 Configuraciones locales críticas

**a) Fin de línea (CRLF frente a LF).** Windows usa CRLF y los contenedores Linux, LF. Un `Makefile` o un script con CRLF falla con errores confusos. Configura:
- Un `.gitattributes` que fuerce LF en el repositorio.
- `files.eol` = `\n` en VS Code y un `.editorconfig`.

**b) OneDrive.** Tu carpeta de documentación está dentro de OneDrive (`...\OneDrive\Documentos\RedesAvanzadas\...`). Para un repositorio Git con Docker esto da problemas: sincronización sobre `.git`, ficheros bloqueados y permisos de Linux que no existen en NTFS. Opciones:
- **Solución adoptada:** el repositorio está en `C:\Users\andre\Documents\RedesAvanzadas\Tracker_Randomlocke`, fuera de OneDrive. Sigue siendo NTFS, así que al trabajar desde WSL (en `/mnt/c`) los permisos de Linux como `chmod 600` pueden no aplicarse; si ocurre, se documenta con honestidad en el README.
- **Alternativa más robusta:** el repositorio en el sistema de ficheros de WSL (por ejemplo `~/proyectos/Tracker_Randomlocke`), abierto con la extensión WSL.
- **Si te quedas en OneDrive:** pausar la sincronización mientras trabajas y asumir que `chmod 600` no tendrá efecto real (documentarlo con honestidad en el README).

**c) Permisos mínimos.** El requisito de "permisos mínimos en los ficheros de configuración" (`chmod 600` en los `.env`) solo tiene efecto en un sistema de ficheros Linux, otra razón para preferir WSL.

**d) Recursos de Docker Desktop.** Con los valores por defecto basta para este stack.

### 1.4 Extensiones de VS Code

Los identificadores pueden cambiar: búscalas por nombre al instalarlas.

| Extensión | Identificador | Para qué | Prioridad |
|---|---|---|---|
| WSL | `ms-vscode-remote.remote-wsl` | Trabajar dentro de WSL | Imprescindible si usas WSL |
| Docker | `ms-azuretools.vscode-docker` | Ver contenedores, logs, validar Dockerfile y compose | Imprescindible |
| Python + Pylance | `ms-python.python`, `ms-python.vscode-pylance` | Autocompletado y análisis del código | Recomendada |
| YAML | `redhat.vscode-yaml` | Validar los ficheros de Compose | Recomendada |
| Makefile Tools | `ms-vscode.makefile-tools` | Resaltado y ejecución de targets | Recomendada |
| EditorConfig | `editorconfig.editorconfig` | Respetar LF y estilo | Recomendada |
| Markdown Preview Mermaid Support | `bierner.markdown-mermaid` | Previsualizar el diagrama del README | Recomendada |
| Hadolint | `exiasr.hadolint` | Lint de Dockerfile (requiere el binario o Docker) | Opcional |
| DotENV | `mikestead.dotenv` | Resaltado de `.env` | Opcional |

Ajustes recomendados de VS Code: fin de línea `\n`, insertar salto de línea final y recortar espacios al final de línea.

### 1.5 Dependencias de la aplicación

Se instalan **dentro de la imagen**, no en tu PC. Fija las versiones con `==` en `requirements.txt`.

| Paquete | Para qué | Entorno |
|---|---|---|
| `fastapi` | Framework de la API | dev y prod |
| `uvicorn` | Servidor ASGI | dev y prod |
| `psycopg` (v3, con extra binario) | Acceso a PostgreSQL | dev y prod |
| `redis` (redis-py) | Cliente de Redis | Instalado en ambos, usado solo en prod |
| `pytest` + `httpx` | Pruebas de humo | Opcional |

Instalar `redis` también en dev permite **una única imagen** para ambos entornos (menos mantenimiento); la alternativa es una imagen por entorno.

Imágenes base propuestas (fija siempre una versión, nunca `latest`; confirma las etiquetas en Docker Hub):

| Servicio | Propuesta |
|---|---|
| Web | `python:3.12-slim` |
| Base de datos | `postgres:16` (versión mayor fija) |
| Caché | `redis:7-alpine` |

### 1.6 Decisiones abiertas

| # | Decisión | Propuesta | Cerrar antes de |
|---|---|---|---|
| 1 | Ubicación del repositorio | **Cerrada:** `C:\Users\andre\Documents\RedesAvanzadas\Tracker_Randomlocke` (fuera de OneDrive) | Paso 0.2 |
| 2 | Cómo ejecutar Make en Windows | WSL como terminal integrada de VS Code (pendiente de comprobar con `wsl -l -v`) | Paso 0.1 |
| 3 | Framework | FastAPI (validación tipada y documentación interactiva en `/docs`) | Paso 1.3 |
| 4 | Puertos publicados | dev 8000, prod 8080 | Paso 1.1 |
| 5 | Inicialización de la BD | Scripts de `initdb.d` o SQL idempotente al arrancar la app (ver Paso 2.1) | Paso 2.1 |
| 6 | Dos ficheros de Compose | Dos ficheros independientes, como pide el enunciado | Paso 3.1 |
| 7 | Semántica de `/status` | BD caída → 503; caché caída → 200 con `degraded` | Paso 1.5 |
| 8 | Alcance de `make down` | Para y elimina contenedores y red, **conserva volúmenes**; `make clean` borra también los datos | Paso 1.6 |
| 9 | Qué `.env` se versionan | **Cerrada:** en GitHub solo las plantillas `.env.*.example` (los reales, ignorados); el ZIP del campus digital incluye los `.env` reales con credenciales exclusivas de este proyecto | Paso 1.1 |

---

## 2. Hoja de ruta secuencial

**Reglas:** un paso a la vez; cada paso termina con una **verificación observable** y un **commit**. Si la verificación falla, no se avanza. Se aprovecha cada paso para anotar material para el README (ver §3).

### Estructura objetivo (se construye gradualmente)

```
Tracker_Randomlocke/
├── app/                      # API y frontend estático
│   ├── static/               # HTML, CSS y JS
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .dockerignore
├── db/                       # scripts SQL (si se usa initdb)
├── docs/                     # documentación de diseño y pruebas
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── .env.dev.example          # plantilla versionada
├── .env.prod.example
├── .env.dev / .env.prod      # reales, NO versionados
├── .gitignore  .gitattributes  .editorconfig
├── Makefile
└── README.md
```

---

### Fase 0: entorno y repositorio (hoy, 8 oct)

- [x] **Paso 0.1: verificar el entorno.**
  Ejecutar el checklist de §1.2 y cerrar las decisiones 1 y 2.
  *Se comprueba:* todas las filas en verde. Sin commit.

- [ ] **Paso 0.2: repositorio y ficheros base.**
  Crear el repositorio público en GitHub y clonarlo en la ubicación elegida. Añadir `.gitignore` (que ignore `.env.dev`, `.env.prod`, entornos virtuales y cachés de Python), `.gitattributes`, `.editorconfig` y un `README.md` mínimo. Copiar a `docs/` los dos documentos de diseño.
  *Se comprueba:* `git push` correcto y repositorio visible en GitHub.
  *Concepto:* se ignoran los `.env` **antes** de crearlos, porque un secreto subido una vez queda en el historial aunque se borre después.
  *Commit:* `chore: inicializa el repositorio con ficheros base y documentación de diseño`

- [ ] **Paso 0.3: estructura de carpetas.**
  Crear la estructura objetivo (con `.gitkeep` donde haga falta).
  *Commit:* `chore: crea la estructura de carpetas del proyecto`

> **Pregunta de control:** ¿por qué añadimos los `.env` al `.gitignore` antes de crear ninguno?

---

### Fase 1: esqueleto andante en dev (8-9 oct)

Objetivo: `web` + `db` funcionando en dev, con `/status` que consulta la BD de verdad.

- [ ] **Paso 1.1: variables de entorno de dev.**
  Crear `.env.dev.example` con los **nombres** de las variables y valores ficticios (usuario, contraseña y nombre de la BD, host de la BD, puerto publicado de la web, interruptor de la caché desactivado). Copiarlo a `.env.dev` con valores propios y restringir permisos.
  *Se comprueba:* `git status` no lista `.env.dev` y `git check-ignore -v .env.dev` confirma que se ignora.
  *Concepto:* interpolación de variables en Compose y por qué los secretos no van en el YAML. Alternativas: Docker secrets o gestores de secretos (excesivo aquí, pero conviene saber explicarlo).
  *Commit:* `chore(env): añade la plantilla de variables de entorno para dev`

- [ ] **Paso 1.2: solo la base de datos.**
  Primer `docker-compose.dev.yml` con únicamente el servicio `db`: imagen con versión fija, variables desde el `.env`, **volumen con nombre**, healthcheck y **sin puertos publicados**.
  *Se comprueba:*
  - `docker compose ps` muestra `db` en estado `healthy`.
  - Se ejecuta una consulta de prueba con `psql` dentro del contenedor (este es el "comando de prueba" que exige el enunciado).
  - `docker ps` no muestra ningún mapeo de puertos para `db`.

  *Concepto:* volumen con nombre frente a *bind mount*; parámetros del healthcheck (intervalo, timeout, reintentos, periodo de gracia); por qué la BD no publica puerto.
  *Commit:* `feat(dev): servicio PostgreSQL con volumen persistente y healthcheck`

- [ ] **Paso 1.3: imagen de la web con una app mínima.**
  Dockerfile (base `slim` con versión fija, dependencias en una capa propia, **usuario no root**), `requirements.txt` con versiones fijas, `.dockerignore` y un único endpoint de prueba.
  *Se comprueba:* la imagen se construye, la app responde y el proceso no corre como root.
  *Concepto:* capas y caché de build; `slim` frente a `alpine`; por qué no root.
  *Commit:* `feat(web): imagen base de la API con usuario no root`

- [ ] **Paso 1.4: web en Compose, único puerto publicado y `/status` real.**
  Añadir el servicio `web` a Compose: espera a que `db` esté `healthy`, **es el único con `ports`**, se conecta a `db` por el nombre del servicio. `/status` ejecuta una consulta real a la BD.
  *Se comprueba:*
  - `http://localhost:<puerto>/status` muestra la BD como disponible.
  - Con `docker compose stop db`, el estado cambia a "caída" **sin reiniciar la web**, y se recupera al volver a levantar `db`.

  *Concepto:* resolución DNS por nombre de servicio en la red de Compose; orden de arranque no equivale a "listo para usar"; la app debe tolerar que la BD no esté disponible y reconectar.
  *Commit:* `feat(dev): web conectada a la BD con endpoint /status real`

- [ ] **Paso 1.5: healthcheck de la web.**
  Definir el healthcheck del contenedor `web` según la decisión 7. La imagen `slim` no trae `curl`: decidir si se instala o se usa Python para la comprobación.
  *Se comprueba:* `docker compose ps` muestra `web` y `db` en `healthy`, y el comportamiento al parar `db` coincide con la decisión.
  *Commit:* `feat(web): healthcheck del contenedor web`

- [ ] **Paso 1.6: Makefile mínimo.**
  Targets `build`, `up-dev`, `down`, `ps` y `logs`. `down` conserva los volúmenes (decisión 8).
  *Se comprueba:* desde cero, `make down && make up-dev` termina con todo en `healthy`.
  *Concepto:* `.PHONY`, `--env-file`, `-f` y nombre de proyecto (`-p`) para que dev y prod no se pisen.
  *Commit:* `build: Makefile con build, up-dev y down`

> **Puerta A: esqueleto andante.** Criterios: dev levanta con un comando, solo `web` publica puerto, `/status` refleja la BD en tiempo real, todos los contenedores `healthy`.
> Etiqueta sugerida: `v0.1-esqueleto`.

> **Pregunta de control:** si `depends_on` solo ordenara el arranque, ¿qué pasaría con la web si Postgres tarda 10 segundos en aceptar conexiones?

---

### Fase 2: MVP en dev (10-11 oct)

- [ ] **Paso 2.1: esquema e inicialización automática.**
  Tablas `runs` y `encounters` (modelo *append-only*, con `details JSONB` reservada para la Fase 2). Decidir la inicialización (decisión 5):
  - Scripts de `initdb.d`: simples, pero solo se ejecutan con el volumen vacío.
  - SQL idempotente al arrancar la app: sobrevive a volúmenes ya existentes.

  *Se comprueba:* tras un `make clean` seguido de `make up-dev`, las tablas existen (`\dt` en `psql`).
  *Commit:* `feat(db): esquema runs/encounters e inicialización automática`

- [ ] **Paso 2.2: endpoints del MVP.**
  Crear una run, registrar un evento (captura, fallo, muerte), consultar el equipo activo (derivado) y el cementerio, con validación de entrada.
  *Se comprueba:* peticiones de prueba (`curl` o `/docs`); tras registrar una muerte, el Pokémon sale del equipo y aparece en el cementerio.
  *Concepto:* consultas parametrizadas (prevención de inyección SQL); por qué los eventos no se modifican.
  *Commit:* `feat(api): endpoints de runs, eventos, equipo activo y cementerio`

- [ ] **Paso 2.3: interfaz estática.**
  Página servida por la propia API (mismo origen, sin CORS) con equipo activo, capturas por ruta, cementerio y un indicador de estado que consulta `/status` periódicamente.
  *Se comprueba:* al parar la BD, el indicador cambia sin recargar la página.
  *Commit:* `feat(ui): interfaz estática con equipo, capturas, cementerio y estado`

- [ ] **Paso 2.4: prueba de persistencia en dev.**
  Insertar datos, **eliminar el contenedor de la BD** (no el volumen), volver a levantarlo y comprobar que los datos siguen. Guardar la salida en `docs/pruebas.md`.
  *Concepto:* diferencia entre eliminar el contenedor y eliminar el volumen; por eso `make down` no borra datos.
  *Commit:* `docs: evidencia de la prueba de persistencia en dev`

---

### Fase 3: producción (12 oct, festivo)

- [ ] **Paso 3.1: `.env.prod` y `docker-compose.prod.yml`.**
  Fichero independiente (decisión 6) con `web`, `db` y `cache` (Redis). Redis con contraseña por variable de entorno, **sin puertos publicados** y con healthcheck. Interruptor de caché activado.
  *Se comprueba:* tres contenedores `healthy` y solo el puerto de `web` publicado.
  *Concepto:* dos ficheros independientes frente a base más override (y por qué el enunciado pide dos).
  *Commit:* `feat(prod): compose de producción con Redis y variables propias`

- [ ] **Paso 3.2: aislamiento de red (endurecimiento).**
  Valorar dos redes: una normal para `web` y otra interna (`internal: true`) para `db` y `cache`, con `web` conectada a ambas. Una red interna no permite publicar puertos, de ahí el diseño.
  *Se comprueba:* desde el host no se alcanzan `db` ni `cache`; `web` sí llega a ambas.
  *Commit:* `feat(prod): red interna para db y cache`

- [ ] **Paso 3.3: caché *cache-aside*.**
  Lectura del equipo activo con Redis, TTL, invalidación **después del commit**, degradación a Postgres si Redis falla, y `/status` con el estado de la caché. La UI muestra origen (`cache` o `db`), latencia y TTL restante.
  *Se comprueba:*
  - Primera lectura MISS y segunda HIT.
  - Registrar un evento provoca un nuevo MISS.
  - Con `docker compose stop cache`, el estado pasa a `degraded` y la app sigue funcionando.

  *Concepto:* por qué se invalida tras el commit; qué aporta el TTL; límites honestos del beneficio a esta escala.
  *Commit:* `feat(cache): cache-aside del equipo activo con invalidación`

- [ ] **Paso 3.4: Makefile completo y verificación en limpio.**
  Añadir `up-prod` y `clean`. Clonar el repositorio en una carpeta nueva, crear los `.env` a partir de las plantillas y levantar prod.
  *Se comprueba:* funciona sin ningún estado previo en la máquina.
  *Commit:* `build: targets up-prod y clean; verificación en limpio`

> **Puerta B (13 oct, noche): MVP completo.** Dev y prod, healthchecks, Makefile, persistencia probada y borrador del README. Si no se cumple, la Fase 2 del proyecto se cancela.
> Etiqueta sugerida: `v0.2-mvp`.

> **Pregunta de control:** ¿qué ocurre si se invalida la caché *antes* del commit y entra una lectura en medio?

---

### Fase 4: cierre (14-17 oct)

Entre el 14 y el 15 de octubre cabe como máximo **una** funcionalidad opcional de la Fase 2 de `idea-y-alcance.md`, con límite de tiempo. El 15 por la noche se congelan las funcionalidades.

- [ ] **Paso 4.1: revisión de seguridad.**
  Comprobar: ningún `.env` real versionado (`git ls-files`), ninguna credencial en código ni YAML (búsqueda de contraseñas), solo `web` con puerto publicado, procesos sin root, permisos de los `.env`. Valorar desactivar la documentación interactiva en prod.
  *Commit:* `chore(security): revisión de seguridad y permisos`

- [ ] **Paso 4.2: pruebas y evidencias.**
  Ejecutar la lista de verificaciones de §11 de `idea-y-alcance.md` y guardar salidas y capturas en `docs/pruebas.md`.
  *Commit:* `docs: resultados de pruebas y verificaciones`

- [ ] **Paso 4.3: README final.**
  Montarlo a partir del mapa de §12 de `idea-y-alcance.md`: guía de instalación, entornos, diagrama, pruebas, healthchecks, uso del Makefile y declaración de uso de IA.
  *Commit:* `docs: README final`

- [ ] **Paso 4.4: entrega y ensayo.**
  Comprobar que el repositorio es público (desde una ventana de incógnito) y que **no contiene** ningún `.env` real. Preparar el ZIP desde la carpeta de trabajo **incluyendo** `.env.dev` y `.env.prod` (con credenciales exclusivas de este proyecto, no reutilizadas en ningún otro sitio) además de las plantillas. Ensayar la defensa.
  Etiqueta sugerida: `v1.0-entrega`.

**Preguntas típicas de la defensa para ensayar:**
1. ¿Por qué solo `web` publica un puerto y qué ocurre si publicas el de la BD?
2. ¿Qué diferencia hay entre `depends_on` y un healthcheck?
3. ¿Cómo se demuestra la persistencia y qué la rompería (`down -v`)?
4. ¿Por qué se invalida la caché después del commit y qué papel tiene el TTL?
5. ¿Qué pasa con la app si Redis cae? ¿Y si cae Postgres?
6. ¿Cómo evitas credenciales en el repositorio y qué harías en un entorno real (secretos)?

---

## 3. Qué ir guardando para el README

| Fase | Material a conservar |
|---|---|
| 0 | Decisiones 1 y 2 y su justificación; estructura de carpetas |
| 1 | Salida de `docker compose ps` con `healthy`; consulta de prueba con `psql`; captura de `/status` con la BD arriba y abajo; explicación de cada healthcheck |
| 2 | Evidencia de persistencia (antes y después de eliminar el contenedor); capturas de la interfaz |
| 3 | `docker compose ps` de prod; demostración MISS/HIT e invalidación; `/status` con la caché caída; diagrama de red |
| 4 | Resultados de la revisión de seguridad; checklist de pruebas completo; **diario de uso de IA** (fecha, herramienta y versión, finalidad y parte del trabajo) |
