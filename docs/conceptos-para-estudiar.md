# Conceptos para estudiar

Guía de estudio para entender y defender la Práctica 1. Cada concepto explica qué es, para qué sirve, cómo se usa en este proyecto y por qué se decidió así. Se amplía a medida que avanzan los pasos.

Los valores que aparecen son siempre ficticios.

## Índice

1. [Docker](#1-docker): imagen, contenedor, capas, usuario no root
2. [Docker Compose](#2-docker-compose): YAML, servicios, `name`, `docker-compose.dev.yml`
3. [Datos y configuración](#3-datos-y-configuración): volúmenes, variables de entorno, `.env`
4. [Salud, red y seguridad](#4-salud-red-y-seguridad): healthcheck, `depends_on`, puertos, red interna
5. [Git y repositorio](#5-git-y-repositorio): `.gitignore`, `.gitattributes`, `.editorconfig`, LF/CRLF, SSH, rebase
6. [Entorno de trabajo](#6-entorno-de-trabajo): WSL, NTFS y permisos
7. [Automatización](#7-automatización): Make y Makefile
8. [Aplicación y base de datos](#8-aplicación-y-base-de-datos): PostgreSQL, `psql`, FastAPI, *append-only*
9. [Caché](#9-caché): Redis, *cache-aside*, TTL

---

## 1. Docker

### Imagen
- **Qué es:** una plantilla de solo lectura con un programa y todo lo que necesita para ejecutarse (sistema base, librerías, configuración). No se ejecuta por sí sola. Ejemplo: `postgres:16`.
- **Para qué se usa:** para que el programa funcione igual en cualquier máquina, sin instalarlo a mano.
- **Dónde y cómo se usa en mi proyecto:** `db` usa la imagen oficial `postgres:16`, `cache` usará `redis:7-alpine` y `web` usará una imagen propia construida con un `Dockerfile` sobre `python:3.12-slim`.
- **Por qué así:** se fija siempre una versión (nunca `latest`). Un `latest` puede cambiar sin avisar y, en una base de datos, una actualización de versión mayor puede dejar los datos ilegibles.
- **Pregunta de defensa:** ¿por qué no usas `postgres:latest`?

### Contenedor
- **Qué es:** una imagen en ejecución. Es un proceso aislado del resto del sistema, con su propio sistema de ficheros y su propia red.
- **Para qué se usa:** ejecutar aplicaciones aisladas entre sí y reproducibles.
- **Dónde y cómo se usa en mi proyecto:** cada servicio del compose se convierte en un contenedor (`randomlocke-dev-db-1`, etc.).
- **Por qué así:** el contenedor es **desechable**: al borrarlo, lo que había dentro desaparece. De ahí que los datos vivan en un volumen.
- **Pregunta de defensa:** ¿qué diferencia hay entre una imagen y un contenedor?

### Capas y caché de build (paso 1.3)
- **Qué es:** una imagen se construye con una capa por cada instrucción del `Dockerfile`. Docker reutiliza las capas que no han cambiado.
- **Para qué se usa:** que reconstruir la imagen sea rápido.
- **Dónde y cómo se usa en mi proyecto:** en el `Dockerfile` de `web`, las dependencias (`requirements.txt`) se instalan en una capa propia **antes** de copiar el código. Si solo cambia el código, no se reinstalan las dependencias.
- **Por qué así:** el código cambia constantemente y las dependencias casi nunca.
- **Pregunta de defensa:** ¿por qué se copia `requirements.txt` antes que el resto del código?

### `CMD` en forma *exec*, `EXPOSE` y `--host 0.0.0.0` (paso 1.3)
- **Qué es:** `CMD ["uvicorn", "main:app", ...]` (forma *exec*, con lista) ejecuta Uvicorn directamente como proceso principal del contenedor; la forma *shell* (`CMD uvicorn ...`) lo lanzaría a través de `/bin/sh`. `EXPOSE 8000` solo documenta el puerto. `main:app` significa "el objeto `app` del fichero `main.py`".
- **Dónde y cómo se usa en mi proyecto:** al final de `app/Dockerfile`. Uvicorn arranca con `--host 0.0.0.0` y `--port 8000`.
- **Por qué así:** con la forma *exec*, Uvicorn recibe directamente las señales de parada (`docker stop` lo cierra limpiamente); con la forma *shell* las recibiría `sh`. `0.0.0.0` es imprescindible en un contenedor: con `127.0.0.1` la app solo sería accesible desde dentro y el puerto publicado no funcionaría. El puerto del host lo decide `WEB_PORT` del `.env`; dentro del contenedor es siempre 8000.
- **Pregunta de defensa:** ¿qué pasa con el puerto publicado si Uvicorn escucha en `127.0.0.1` dentro del contenedor?

### Contexto de build y `.dockerignore` (paso 1.3)
- **Qué es:** al construir una imagen, Docker envía al motor una carpeta, el **contexto de build**, y el `Dockerfile` solo puede copiar ficheros de ahí. `.dockerignore` indica qué no enviar, igual que `.gitignore` con Git.
- **Para qué se usa:** seguridad (que un `COPY . .` no meta `.env`, `.git` o claves dentro de una imagen que podría compartirse), velocidad y tamaño.
- **Dónde y cómo se usa en mi proyecto:** `app/.dockerignore`, porque el contexto de la web es `app/` (`build: ./app` en el compose). Excluye cachés de Python, entornos virtuales, `.env` y `.env.*`, metadatos de Git y de VS Code, y el propio `Dockerfile`.
- **Por qué así:** a diferencia del `.gitignore`, aquí sí se ignora `.env.*` entero: la imagen no necesita ninguna plantilla ni valor. Debe estar en la raíz del contexto, no del proyecto.
- **Pregunta de defensa:** ¿por qué es peligroso un `COPY . .` sin `.dockerignore`?

### Instrucciones del Dockerfile: `FROM`, `ENV`, `WORKDIR`, `COPY`, `RUN` (paso 1.3)
- **Qué es:** el `Dockerfile` es la receta de la imagen; cada instrucción crea una capa. `FROM` elige la imagen base; `ENV` fija variables de entorno; `WORKDIR` fija la carpeta de trabajo; `COPY` copia ficheros del contexto a la imagen; `RUN` ejecuta un comando durante la construcción.
- **Dónde y cómo se usa en mi proyecto:** `app/Dockerfile` parte de `python:3.12-slim`, trabaja en `/app`, copia `requirements.txt` y ejecuta `pip install --no-cache-dir -r requirements.txt` **antes** de copiar el código. `PYTHONDONTWRITEBYTECODE=1` evita crear `.pyc` dentro del contenedor y `PYTHONUNBUFFERED=1` hace que los logs salgan al instante en `docker compose logs`.
- **Por qué así:** el orden aprovecha la caché de capas: si solo cambia `main.py`, la capa de dependencias se reutiliza y no se reinstala nada. `--no-cache-dir` evita guardar en la imagen la caché de pip, que no sirve para nada ahí.
- **Cómo leer la salida de `docker build`:** cada instrucción aparece como un paso (`[2/4] WORKDIR /app`...). Si no ha cambiado nada, el paso aparece como `CACHED`. En el proyecto, la primera construcción tardó unos 6 s (instalar FastAPI y Uvicorn) y la segunda 0,3 s con `CACHED` en los tres pasos: es la caché de capas funcionando.
- **Error típico:** el `Dockerfile` es un **fichero** de texto sin extensión, con ese nombre exacto (D mayúscula, sin `.txt`). Caso real: se creó por error como una carpeta vacía, y Docker no encontraba la receta. Se comprueba con `ls -l`: una línea que empieza por `-` es un fichero y por `d` una carpeta.
- **Pregunta de defensa:** ¿por qué se copia `requirements.txt` y se instala antes de copiar el resto del código?

### Preguntas del temario (Tema 5) sobre el Dockerfile
Conceptos que el temario de la asignatura plantea y que conviene saber explicar, aunque el proyecto no los use todos.
- **`COPY` frente a `ADD`:** ambos copian ficheros a la imagen. `ADD` además descomprime archivos `.tar` y admite URLs, lo que lo hace menos predecible. Se prefiere `COPY`, que es el que usa el proyecto.
- **`CMD` frente a `ENTRYPOINT`:** `ENTRYPOINT` define el ejecutable fijo del contenedor y `CMD` sus argumentos por defecto, que se pueden sobrescribir al hacer `docker run`. Si se combinan, `CMD` aporta los argumentos de `ENTRYPOINT`. El proyecto usa solo `CMD` para arrancar Uvicorn.
- **`EXPOSE`:** solo **documenta** el puerto en el que escucha la aplicación; no lo publica. Publicar es `ports:` en el compose.
- ***Multi-stage build*:** construir en una etapa con herramientas pesadas (compiladores...) y copiar solo el resultado a una imagen final ligera. Reduce tamaño y superficie de ataque. En este proyecto no hace falta: `python:3.12-slim` instala dependencias puras sin compilar, así que una sola etapa es más simple.
- **`HEALTHCHECK` en el Dockerfile:** el enunciado permite definirlo en el compose o en el Dockerfile. El proyecto lo define en el compose.
- **Análisis de imágenes (Trivy, Grype):** herramientas que buscan vulnerabilidades conocidas en las dependencias de una imagen. Mejora opcional del proyecto, no obligatoria.
- **Tipos de red de Docker:** *bridge* (la de Compose por defecto: contenedores aislados que se hablan entre sí), *host* (usa la red del host y pierde el aislamiento) y *overlay* (varios hosts, para Swarm o Kubernetes). El proyecto usa *bridge*.
- **Pregunta de defensa:** ¿por qué se prefiere `COPY` a `ADD`, y por qué no hace falta un *multi-stage build* en esta práctica?

### `slim` frente a `alpine` (paso 1.3)
- **Qué es:** variantes reducidas de una imagen base. `slim` es Debian recortado; `alpine` usa otra librería de C (musl) y es aún más pequeña.
- **Dónde y cómo se usa en mi proyecto:** `python:3.12-slim` para `web`; `redis:7-alpine` para `cache`.
- **Por qué así:** con Python, `slim` evita problemas de compatibilidad de paquetes compilados que a veces da `alpine`. Redis no tiene ese problema, y ahí `alpine` ahorra tamaño.
- **Pregunta de defensa:** ¿por qué `slim` para Python y `alpine` para Redis?

### Usuario no root (paso 1.3)
- **Qué es:** por defecto, el proceso de un contenedor corre como `root`. Un usuario no root tiene permisos limitados.
- **Para qué se usa:** reducir el daño si alguien consigue ejecutar código dentro del contenedor.
- **Dónde y cómo se usa en mi proyecto:** el `Dockerfile` de `web` crea el usuario `appuser` con `useradd --system --no-create-home --uid 10001 --shell /usr/sbin/nologin appuser` (usuario de sistema, sin carpeta personal, sin shell de inicio de sesión y con un UID alto y fijo) y cambia a él con `USER appuser` antes del arranque. El código se copia **sin** `--chown`, así que pertenece a `root` y `appuser` solo puede leerlo: la aplicación no puede modificar su propio código. Se comprueba con `docker run --rm <imagen> whoami`.
- **Por qué así:** es una medida básica de seguridad que el enunciado recomienda.
- **Pregunta de defensa:** ¿qué ventaja de seguridad aporta no ejecutar como root?

---

## 2. Docker Compose

### Docker Compose
- **Qué es:** una herramienta que describe en un fichero **varios contenedores** y cómo se relacionan (red, volúmenes, variables) y los levanta con un solo comando.
- **Para qué se usa:** evitar lanzar a mano varios `docker run` largos y propensos a errores.
- **Dónde y cómo se usa en mi proyecto:** `docker-compose.dev.yml` (web y db) y `docker-compose.prod.yml` (web, db y cache). Se invoca con `docker compose` (v2, con espacio, no `docker-compose`).
- **Por qué así:** es lo que pide el enunciado. Es declarativo: se describe cómo debe ser el sistema y Compose lo construye.
- **Pregunta de defensa:** ¿qué ventaja tiene Compose frente a ejecutar `docker run` para cada servicio?

### YAML
- **Qué es:** un formato de texto para configuración, donde la estructura se marca con **sangría** (espacios, nunca tabuladores).
- **Dónde y cómo se usa en mi proyecto:** todos los ficheros de Compose. `.editorconfig` fuerza 2 espacios en `*.yml`.
- **Por qué así:** una sangría incorrecta cambia el significado del fichero o lo rompe. La sangría **es la jerarquía**: cada nivel son 2 espacios más. Caso real del proyecto: el bloque `healthcheck:` se escribió sin sangría, fuera de `db`, y Compose lo rechazó; hay que subirlo a 4 espacios para que sea propiedad del servicio. `docker compose config --quiet` lo detecta.
- **Pregunta de defensa:** ¿qué pasa si mezclas tabuladores y espacios en un YAML?

### Servicio (`services:`)
- **Qué es:** cada pieza del sistema que Compose gestiona; cada servicio genera uno o más contenedores.
- **Dónde y cómo se usa en mi proyecto:** `web`, `db` y (solo en prod) `cache`. El nombre del servicio sirve además de **dirección en la red interna**: `web` llegará a la base de datos usando el host `db`, por eso `DB_HOST=db` coincide con el nombre del servicio.
- **Por qué así:** evita direcciones IP, que cambian al recrear contenedores.
- **Pregunta de defensa:** ¿cómo encuentra `web` a la base de datos sin conocer su IP?

### `name:` (nombre del proyecto)
- **Qué es:** el prefijo que Compose pone a contenedores, redes y volúmenes.
- **Dónde y cómo se usa en mi proyecto:** `name: randomlocke-dev` en el compose de dev y uno distinto en prod.
- **Por qué así:** así dev y prod pueden coexistir en la misma máquina sin pisarse.
- **Pregunta de defensa:** ¿qué pasaría si dev y prod usaran el mismo nombre de proyecto?

### Dos ficheros de Compose independientes
- **Qué es:** un fichero por entorno, sin depender uno de otro.
- **Dónde y cómo se usa en mi proyecto:** `docker-compose.dev.yml` y `docker-compose.prod.yml`.
- **Por qué así:** lo exige el enunciado. La alternativa habitual es un fichero base más un *override* (`-f base.yml -f prod.yml`), que evita repetir texto pero no cumple el enunciado tal cual.
- **Pregunta de defensa:** ¿por qué dos ficheros separados en vez de uno base con *overrides*?

---

## 3. Datos y configuración

### Volumen con nombre
- **Qué es:** un espacio de almacenamiento gestionado por Docker que **vive fuera del contenedor**.
- **Para qué se usa:** que los datos sobrevivan a que el contenedor se borre o se recree.
- **Dónde y cómo se usa en mi proyecto:** la base de datos guarda sus ficheros en un volumen montado en `/var/lib/postgresql/data`.
- **Por qué así:** es el requisito de persistencia del enunciado. Se prefiere al *bind mount* (carpeta del host) porque en `/mnt/c` (NTFS) Postgres puede fallar por los permisos.
- **Qué lo borra:** `docker compose down` **conserva** el volumen; `down -v` lo **elimina**. Por eso `make down` no usa `-v` y `make clean` sí.
- **Pregunta de defensa:** ¿qué diferencia hay entre `down` y `down -v`, y qué pasa con los datos en cada caso?

### Declaración del volumen (`volumes:` de nivel superior)
- **Qué es:** un volumen se usa en **dos sitios** del compose. Dentro del servicio, `pgdata:/var/lib/postgresql/data` dice "monta el volumen `pgdata` en esta carpeta del contenedor". Al final del fichero, sin sangría, `volumes:` + `pgdata:` **declara** que ese volumen existe.
- **Dónde y cómo se usa en mi proyecto:** `docker-compose.dev.yml` tiene el servicio `db` con su montaje y, al final, la declaración `pgdata:`.
- **Por qué así:** sin la declaración, Compose da error por volumen no definido. Dejar `pgdata:` sin nada detrás significa un volumen normal gestionado por Docker. Declararlo aparte permite que varios servicios compartan el mismo volumen.
- **Pregunta de defensa:** ¿qué diferencia hay entre el `volumes:` de dentro del servicio y el del final del fichero?

### Bind mount
- **Qué es:** enlazar una carpeta concreta del host con una carpeta del contenedor.
- **Por qué no se usa para la BD:** en NTFS los permisos de Linux no se respetan y Postgres puede negarse a arrancar. Sí es útil para ver el código en desarrollo sin reconstruir.
- **Pregunta de defensa:** ¿cuándo elegirías un bind mount en vez de un volumen con nombre?

### Variables de entorno
- **Qué es:** pares `NOMBRE=valor` que se pasan a un programa al arrancar.
- **Para qué se usa:** configurar el programa sin escribir los valores en el código.
- **Dónde y cómo se usa en mi proyecto:** usuario, contraseña y nombre de la BD, host de la BD, puerto de `web` e interruptor de la caché. El enunciado prohíbe credenciales en el código y en los YAML.
- **Por qué así:** la alternativa profesional son los *Docker secrets* o un gestor de secretos (Vault...). Aquí sería excesivo, pero conviene saber explicarlo.
- **Pregunta de defensa:** ¿cómo evitas que haya credenciales en el repositorio y qué usarías en un entorno real?

### Interpolación (`${VARIABLE}`)
- **Qué es:** en el YAML se escribe `${POSTGRES_PASSWORD}` y Compose lo sustituye por el valor leído del `.env`.
- **Dónde y cómo se usa en mi proyecto:** en `docker-compose.*.yml`, que solo contienen nombres de variables, no valores.
- **Por qué así:** el YAML se puede subir a GitHub sin riesgo.
- **Pregunta de defensa:** si el YAML dice `${POSTGRES_PASSWORD}`, ¿de dónde sale el valor?

### `environment:` frente a `env_file:`
- **Qué es:** dos formas de pasar variables a un contenedor. `environment:` lista una a una las que recibe; `env_file:` le pasa **todo** el contenido de un fichero.
- **Para qué se usa:** que el programa del contenedor se configure al arrancar. La imagen de Postgres lee `POSTGRES_USER`, `POSTGRES_PASSWORD` y `POSTGRES_DB` la **primera vez** que arranca con un volumen vacío y crea con ellas el usuario, la contraseña y la base de datos.
- **Dónde y cómo se usa en mi proyecto:** el servicio `db` usa `environment:` con `POSTGRES_USER: ${POSTGRES_USER}` y las otras dos. A la izquierda va el nombre que **espera la imagen** (no se puede cambiar) y a la derecha la interpolación.
- **Ojo con el volumen:** Postgres solo lee estas variables cuando el volumen está **vacío**. Si cambias `POSTGRES_PASSWORD` después con el volumen ya creado, la contraseña guardada no cambia; hay que borrar el volumen (`down -v`, o `make clean`) o cambiarla desde dentro de la BD.
- **Por qué así:** con `environment:` cada servicio recibe solo lo que necesita (mínimo privilegio). Con `env_file: .env.dev`, `db` recibiría también variables ajenas, como `WEB_PORT`. `env_file` es más corto, pero menos preciso.
- **Pregunta de defensa:** ¿por qué pasas las variables una a una en vez de usar `env_file`?

### `--env-file` y la lectura del fichero de variables
- **Qué es:** Compose lee automáticamente un fichero llamado `.env`, pero **no** `.env.dev`. La opción `--env-file .env.dev` le indica cuál usar para resolver las interpolaciones `${...}` del YAML.
- **Dónde y cómo se usa en mi proyecto:** el `Makefile` (paso 1.6) lo añade siempre: `docker compose --env-file .env.dev -f docker-compose.dev.yml ...`. Prod usará `.env.prod`.
- **Por qué así:** el enunciado pide un `.env` por entorno, así que los ficheros no se llaman `.env`. Sin esta opción, Compose avisa con `The "POSTGRES_USER" variable is not set. Defaulting to a blank string`. No es un error del YAML: Compose no sabe dónde buscar los valores.
- **Pregunta de defensa:** ¿cómo sabe Compose de qué fichero sacar los valores de `${POSTGRES_PASSWORD}`?

### Comandos del ciclo de vida: `up -d`, `ps`, `exec`, `down` (paso 1.2)
- **Qué es:** `up -d` crea y arranca los servicios en segundo plano (*detached*); `ps` lista los contenedores con su estado y puertos; `exec` ejecuta un comando **dentro** de un contenedor en marcha; `down` para y elimina contenedores y red, pero conserva los volúmenes.
- **Dónde y cómo se usa en mi proyecto:** `up -d db` arranca solo la base de datos; `exec db ...` lanza el `psql` de prueba que exige el enunciado; `ps` muestra `healthy` y confirma que `db` no publica puertos. El `Makefile` (paso 1.6) los envolverá en `make up-dev`, `make ps` y `make down`.
- **Por qué así:** `exec` permite probar la conexión sin publicar el puerto de la BD ni instalar `psql` en tu máquina. Cada comando de Compose necesita `--env-file` y `-f` para saber qué entorno usar; en una sesión se puede abreviar con un `alias`, y de forma definitiva con el Makefile.
- **Pregunta de defensa:** ¿cómo compruebas la conexión a la BD si no publica ningún puerto?

### Prueba de persistencia: borrar el contenedor, no el volumen (paso 2.4)
- **Qué es:** el enunciado exige demostrar la persistencia *insertando información en la base de datos, eliminando el contenedor y volviéndolo a iniciar, verificando que los datos se mantienen*. El contenedor es desechable y el volumen es donde viven los datos, así que borrar el primero no afecta a los segundos. Tres comandos que conviene distinguir: `docker compose rm -s -f db` (para y **elimina solo el contenedor** `db`; conserva red y volumen), `docker compose down` (elimina todos los contenedores y la red; conserva los volúmenes, es `make down`) y `docker compose down -v` (elimina además los **volúmenes**: pierde los datos, es `make clean`).
- **Cómo se demuestra que es un contenedor nuevo:** el ID del contenedor y su fecha de creación cambian tras recrearlo (`docker inspect`), mientras que el volumen (`docker volume ls`) y su contenido son los mismos. Se comprueba además que los datos coinciden antes y después con el API y con `psql`.
- **Dónde y cómo se usa en mi proyecto:** sobre la BD de desarrollo, con partidas y eventos reales creados desde la API. La evidencia se guarda en `docs/pruebas.md`, para el README.
- **Por qué así:** es el requisito central de la práctica y la razón de elegir un volumen con nombre. Contraste: con `down -v` (o `make clean`) los datos **sí** se pierden, por eso van en un target aparte.
- **Pregunta de defensa:** ¿qué diferencia hay entre eliminar el contenedor de la BD y eliminar su volumen, y cuál de los dos pierde los datos?

### Cómo leer la columna PORTS de `docker compose ps` (paso 1.2)
- **Qué es:** un servicio **publicado** muestra una flecha, por ejemplo `0.0.0.0:8000->8000/tcp` (puerto del host hacia el del contenedor). Uno que solo expone el puerto internamente muestra `5432/tcp`, sin flecha.
- **Dónde y cómo se usa en mi proyecto:** `db` debe mostrar `5432/tcp` sin flecha: Postgres escucha dentro de la red de Docker, pero tu máquina no puede conectarse desde fuera.
- **Por qué así:** es el requisito de "solo la aplicación web puede publicar puerto" del enunciado y la forma de demostrarlo.
- **Pregunta de defensa:** ¿qué diferencia hay entre `5432/tcp` y `0.0.0.0:5432->5432/tcp`?

### `docker compose config --quiet`
- **Qué es:** `config` valida el YAML y muestra la configuración ya resuelta. Con `--quiet` solo valida y no imprime nada si es correcto.
- **Dónde y cómo se usa en mi proyecto:** `docker compose --env-file .env.dev -f docker-compose.dev.yml config --quiet`, para comprobar la sintaxis tras cada cambio.
- **Por qué así:** sin `--quiet`, `config` imprime los **valores reales**, incluida la contraseña. Por eso no se ejecuta sin esa opción. Que no salga nada significa que todo va bien.
- **Pregunta de defensa:** ¿por qué no es buena idea ejecutar `docker compose config` sin `--quiet` delante de otras personas?

### `.env.dev`, `.env.prod` y plantillas `.env.*.example`
- **Qué es:** los `.env` reales contienen los valores; las plantillas contienen los **nombres** con valores ficticios.
- **Dónde y cómo se usa en mi proyecto:** `.env.dev.example` se sube a GitHub; `.env.dev` no (está en `.gitignore`). Los `.env` reales se entregan solo en el ZIP del campus, con credenciales exclusivas del proyecto.
- **Por qué así:** quien clone el repo sabe qué variables definir sin ver tus secretos. Una contraseña subida a Git **queda en el historial aunque se borre después**.
- **Incidencia real:** al crear la plantilla se escribió por error una contraseña real; se detectó antes del primer `git add` y se corrigió.
- **Limitación:** `chmod 600` no tiene efecto en `/mnt/c` (NTFS); el fichero sigue `-rwxrwxrwx` y se documenta en el README.
- **Pregunta de defensa:** si un `.env` se cuela en un commit y lo borras en el siguiente, ¿desaparece la contraseña del repositorio?

---

## 4. Salud, red y seguridad

### Healthcheck
- **Qué es:** un comando que Docker ejecuta periódicamente dentro del contenedor para comprobar que el servicio funciona. Estados: `starting`, `healthy`, `unhealthy`.
- **Para qué se usa:** distinguir entre "el contenedor está arrancado" y "el servicio está listo".
- **Dónde y cómo se usa en mi proyecto:** `db` con `pg_isready`, `cache` con `redis-cli ping`, `web` consultando su propio `/status`. El enunciado exige healthcheck en todos los contenedores.
- **Parámetros:** `interval` (cada cuánto), `timeout` (cuánto espera), `retries` (fallos seguidos hasta `unhealthy`), `start_period` (gracia inicial, en la que los fallos no cuentan).
- **Por qué así:** `db` se marca solo si acepta conexiones; `cache` caída no debe marcar `web` como `unhealthy` (ver `/status`).
- **Pregunta de defensa:** ¿qué diferencia hay entre `depends_on` y un healthcheck?

### Healthcheck de PostgreSQL: `pg_isready` y el escape `$$` (paso 1.2)
- **Qué es:** `pg_isready` es un programa incluido en la imagen de Postgres que responde si el servidor acepta conexiones (código de salida 0 = sí). El campo `test: ["CMD-SHELL", "..."]` ejecuta ese texto como un comando de shell **dentro** del contenedor.
- **Dónde y cómo se usa en mi proyecto:** en el servicio `db`: `pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}`, con `interval`, `timeout`, `retries` y `start_period`.
- **Por qué `$$` y no `$`:** Compose interpreta `${VAR}` **al leer el YAML**, en tu máquina. Con `$${VAR}` escapa el símbolo y la variable la resuelve la **shell del contenedor**, que ya tiene `POSTGRES_USER` y `POSTGRES_DB` en su entorno. Así el valor no se expande en el YAML.
- **Por qué `-U` y `-d`:** sin ellos, `pg_isready` comprueba con un usuario por defecto que no existe, y Postgres registra en sus logs un error `role "root" does not exist` en cada comprobación.
- **Por qué `CMD-SHELL`:** la otra forma, `["CMD", "pg_isready", ...]`, ejecuta el programa directamente y no interpreta variables de entorno.
- **Pregunta de defensa:** ¿qué diferencia hay entre `${VAR}` y `$${VAR}` dentro de un compose?

### Healthcheck de la web sin `curl` (paso 1.5)
- **Qué es:** un healthcheck que, desde **dentro** del contenedor `web`, pide `/status` a la propia app con el módulo `urllib` de Python. Si la respuesta es un error HTTP (como `503`) o no llega a tiempo, el comando termina con código distinto de 0 y cuenta como fallo.
- **Dónde y cómo se usa en mi proyecto:** bloque `healthcheck:` del servicio `web` en el compose: `["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/status', timeout=3)"]`, con `interval 10s`, `timeout 5s`, `retries 3` y `start_period 10s`.
- **Por qué así:** la imagen `slim` no incluye `curl`; instalarlo añadiría un paquete y superficie de ataque, mientras que Python ya está. Se define en el compose (como el de `db`) y no en el `Dockerfile`. Se usa `CMD` y no `CMD-SHELL` porque no hay variables que expandir. `localhost:8000` es correcto porque la comprobación corre dentro de `web`, donde la app escucha siempre en 8000.
- **Qué cuenta como sano (decisión 7):** BD caída → `/status` da 503 → `web` `unhealthy`. Caída solo de la caché → `/status` da 200 con `degraded` → `web` sigue `healthy`, porque la caché es opcional.
- **Consecuencia:** Compose no reinicia ni para un contenedor `unhealthy`; el estado es informativo y lo usan los `depends_on` y los orquestadores que sí reinician contenedores.
- **Pregunta de defensa:** ¿por qué el healthcheck de `web` usa Python en lugar de `curl`, y por qué una caché caída no debe marcarlo `unhealthy`?

### `build:` frente a `image:` en un servicio (paso 1.4)
- **Qué es:** `image:` descarga una imagen ya hecha de un registro (como `postgres:16`). `build: ./app` le dice a Compose que construya la imagen con el `Dockerfile` de esa carpeta, que además es el **contexto de build**.
- **Dónde y cómo se usa en mi proyecto:** `db` usa `image:` (imagen oficial) y `web` usa `build: ./app` (imagen propia). `docker compose up -d --build` fuerza la reconstrucción; sin `--build`, Compose reutiliza la imagen ya construida aunque hayas cambiado el código.
- **Por qué así:** la web es código propio y hay que empaquetarlo; la base de datos es software estándar y no hace falta.
- **Pregunta de defensa:** ¿qué diferencia hay entre `image:` y `build:`, y cuándo se reconstruye la imagen?

### `depends_on` con `condition: service_healthy` (paso 1.4)
- **Qué es:** indica que un servicio espera a otro. Sin condición, solo ordena el **arranque**; con `service_healthy`, espera a que esté **listo**.
- **Dónde y cómo se usa en mi proyecto:** `web` espera a que `db` esté `healthy`.
- **Por qué así:** si solo ordenara el arranque y Postgres tardara 10 segundos en aceptar conexiones, `web` fallaría al conectar.
- **Caso real del proyecto:** al probar la imagen de `web`, un `curl` lanzado justo después de `docker run -d` no devolvió nada, y 3 segundos después respondió `200 OK`. Que un contenedor esté arrancado no significa que el servicio ya esté escuchando; es exactamente lo que resuelve un healthcheck.
- **Pregunta de defensa:** si `depends_on` solo ordenara el arranque, ¿qué le pasaría a `web` con una BD lenta?

### Puertos publicados (`ports`)
- **Qué es:** abre una puerta entre el host y un contenedor (`"8000:8000"`).
- **Dónde y cómo se usa en mi proyecto:** solo `web` tiene `ports` (8000 en dev y 8080 en prod). `db` y `cache` no publican nada. Se escribe `"${WEB_PORT}:8000"`: a la izquierda el puerto **del host**, que sale del `.env` de cada entorno, y a la derecha el del **contenedor**, que es siempre 8000 (el que fija el `Dockerfile`).
- **Por qué así:** el enunciado lo exige y reduce la superficie de ataque. Los contenedores se hablan por la red interna sin publicar nada.
- **Pregunta de defensa:** ¿qué ocurre si publicas el puerto de la base de datos?

### Red interna de Docker
- **Qué es:** una red virtual donde los contenedores del mismo Compose se comunican por el nombre de su servicio.
- **Dónde y cómo se usa en mi proyecto:** `web`, `db` y `cache` comparten red. En prod se valorará una segunda red `internal: true` para `db` y `cache` (paso 3.2).
- **Por qué así:** una red `internal: true` no permite publicar puertos ni salir al exterior, así que `web` se conecta a dos redes: una normal (para publicar su puerto) y la interna.
- **Pregunta de defensa:** ¿por qué `web` necesita estar en dos redes?

---

### Arquitectura del proyecto: aplicación multicontenedor, no microservicios
- **Qué es:** en una arquitectura de **microservicios** la lógica de negocio se divide en servicios independientes (cada uno con su código, despliegue y a veces su BD) que se comunican por API. Un **monolito** concentra esa lógica en una sola aplicación. Una aplicación **multicontenedor** puede ser cualquiera de las dos: tener varios contenedores no basta para ser microservicios.
- **Dónde y cómo se usa en mi proyecto:** `web` contiene toda la lógica (un único servicio); `db` (PostgreSQL) y `cache` (Redis) son software de terceros que `web` usa como servicios de apoyo.
- **Por qué así:** es un monolito desplegado con servicios de apoyo (arquitectura en capas), suficiente para el alcance. Aun así comparte ideas con microservicios: servicios desacoplados por red, comunicación por nombre, fallos independientes y degradación si la caché cae.
- **Pregunta de defensa:** ¿tu práctica es una arquitectura de microservicios? Respuesta corta: no; es un monolito con servicios de apoyo, porque la lógica de negocio no está dividida.

### Trivy: análisis de vulnerabilidades (mejora opcional, Fase 4)
- **Qué es:** un escáner de seguridad de código abierto que compara los paquetes del sistema y las librerías de una imagen con bases de datos de vulnerabilidades conocidas (CVE). También detecta secretos olvidados y errores de configuración.
- **Dónde y cómo se usaría en mi proyecto:** sobre la imagen de `web` (por ejemplo `docker run --rm aquasec/trivy image <imagen>`) y en la revisión de seguridad del paso 4.1, con los resultados guardados en `docs/pruebas.md`.
- **Por qué así:** el Tema 5 lo cita como buena práctica. Solo detecta fallos **ya conocidos**, y muchos de la imagen base no tienen arreglo todavía. Dar acceso al socket de Docker a su contenedor le concede control sobre Docker; la alternativa es escanear la imagen exportada con `docker save`.
- **Pregunta de defensa:** ¿qué hace Trivy y qué no puede garantizar?

### Ramas y *merge* (se practicará en la Fase 2 opcional)
- **Qué es:** una rama es una línea de desarrollo independiente; `merge` la integra en otra. Permite trabajar en una funcionalidad sin tocar `main` hasta que esté lista.
- **Dónde y cómo se usará en mi proyecto:** la funcionalidad opcional de la Fase 2 se hará en una rama (por ejemplo `feat/...`) y se fusionará en `main` al terminar. Hasta ahora todo el trabajo ha sido directo en `main`.
- **Por qué así:** es el concepto de Git del Tema 3 que aún no se ha practicado; hacerlo con un caso real sirve para la defensa.
- **Pregunta de defensa:** ¿qué ventaja tiene trabajar en una rama frente a hacerlo directamente en `main`?

## 5. Git y repositorio

### `.gitignore`
- **Qué es:** lista de ficheros que Git no debe seguir.
- **Dónde y cómo se usa en mi proyecto:** ignora los `.env` reales, cachés y entornos de Python, `.vscode/`, `.claude/`, `Practica1.pdf` y `CLAUDE.md`.
- **Por qué así:** es **preventivo**: protege lo que entra después. Un fichero ya subido no deja de estarlo por añadirlo luego al `.gitignore`. Se usan reglas exactas (`.env.dev`) para que la plantilla `.env.dev.example` sí se suba.
- **Pregunta de defensa:** ¿por qué se crea el `.gitignore` antes que los `.env`?

### `.gitattributes` y finales de línea (LF y CRLF)
- **Qué es:** Windows termina las líneas con CRLF y Linux con LF. `.gitattributes` le dice a Git cómo tratar los ficheros al guardarlos y sacarlos.
- **Dónde y cómo se usa en mi proyecto:** `* text=auto eol=lf` fuerza LF y marca imágenes y PDF como binarios.
- **Por qué así:** un `Makefile` o un script con CRLF falla en Linux (`missing separator`, `bad interpreter`). Es una regla del **proyecto** y viaja con el repositorio, a diferencia de `core.autocrlf`, que es una preferencia de cada máquina.
- **Pregunta de defensa:** ¿qué falla en un `Makefile` con CRLF y cómo lo evitas?

### `.editorconfig`
- **Qué es:** reglas de escritura para el editor (UTF-8, LF, salto final, sangría).
- **Dónde y cómo se usa en mi proyecto:** 4 espacios por defecto, 2 en YAML y Markdown y **tabuladores en el `Makefile`**.
- **Por qué así:** actúa mientras escribes; `.gitattributes` actúa al guardar en Git. Son dos capas, y solo `.editorconfig` protege los tabuladores del `Makefile`.
- **Pregunta de defensa:** ¿qué diferencia hay entre `.gitattributes` y `.editorconfig`?

### `.gitkeep`
- **Qué es:** un fichero vacío que obliga a Git a guardar una carpeta, porque Git solo sigue ficheros.
- **Dónde y cómo se usa en mi proyecto:** `app/static/.gitkeep`.
- **Por qué así:** sin él, quien clone el repo no tendría la carpeta y algo que la espere fallaría. La alternativa es un `.gitignore` interno, útil cuando el contenido nunca debe subirse.
- **Pregunta de defensa:** si creas una carpeta vacía y haces commit, ¿llega al repositorio?

### Autenticación por SSH
- **Qué es:** un par de claves: la **privada** se queda en tu máquina y la **pública** se da a GitHub. GitHub comprueba que tienes la privada sin que viaje por la red.
- **Dónde y cómo se usa en mi proyecto:** clave `ed25519` creada en WSL (`~/.ssh`), pública añadida en GitHub. La privada tiene passphrase.
- **Por qué así:** es más segura que una contraseña. La clave pública no da acceso a nadie; nunca se comparte la privada. En la primera conexión se debe comparar la huella de `github.com` antes de aceptarla (protege de un ataque de intermediario).
- **Pregunta de defensa:** ¿qué puede hacer alguien que consiga tu clave pública?

### Conventional Commits
- **Qué es:** formato de mensajes de commit: `tipo(ámbito): descripción`.
- **Dónde y cómo se usa en mi proyecto:** `chore:`, `feat:`, `docs:`, `build:`. Ejemplo: `chore(env): add dev environment variables template`.
- **Por qué así:** el historial se lee como una lista ordenada de lo que se hizo, y se evalúa la organización del proyecto.
- **Pregunta de defensa:** ¿qué significan `chore`, `feat` y el ámbito entre paréntesis?

### Push rechazado, `rebase` y conflictos
- **Qué es:** si el remoto tiene commits que tu copia no tiene, `git push` se rechaza. `git pull --rebase` reaplica tus commits encima de los remotos y deja un historial lineal. Si ambos tocaron la misma línea hay un **conflicto**, que se resuelve a mano.
- **Dónde y cómo se usa en mi proyecto:** ocurrió al editar el diario en la web de GitHub y en local. Se resolvió con `pull --rebase`, conservando la versión local.
- **Por qué así:** `rebase` en lugar de `merge` porque el repo es de una sola persona y queda un historial recto. No se usó `--force`, que habría borrado el commit remoto sin saber qué contenía.
- **Reglas:** no editar en la web de GitHub; no usar `--force` sin revisar el remoto.
- **Pregunta de defensa:** ¿por qué no usar `git push --force` para resolver un push rechazado?

---

## 6. Entorno de trabajo

### WSL
- **Qué es:** el subsistema de Windows para Linux; ejecuta una distro Linux (Ubuntu) dentro de Windows.
- **Dónde y cómo se usa en mi proyecto:** `make`, `docker` y `git` se ejecutan desde la terminal de Ubuntu, con VS Code abierto en modo WSL.
- **Por qué así:** `make` no existe en Windows, y los contenedores son Linux. Un solo entorno evita mezclar dos instalaciones de Git sobre la misma carpeta.
- **Pregunta de defensa:** ¿por qué se ejecuta `make` en WSL y no directamente en Windows?

### Docker Desktop y la integración con WSL
- **Qué es:** Docker Desktop es la aplicación de Windows que ejecuta el motor de Docker. La integración con WSL hace que la distro (Ubuntu) pueda usar el comando `docker`.
- **Dónde y cómo se usa en mi proyecto:** se activa en Docker Desktop → Settings → Resources → WSL integration. Si Docker Desktop no está arrancado, Ubuntu muestra `The command 'docker' could not be found in this WSL 2 distro`, y desde PowerShell `failed to connect to the docker API`.
- **Por qué así:** el motor no corre dentro de Ubuntu, corre en Docker Desktop. **Antes de cualquier `docker` o `make`, comprueba que está arrancado.** Si sigue fallando, `wsl --shutdown` desde PowerShell y volver a abrir Docker Desktop y Ubuntu.
- **Pregunta de defensa:** ¿qué compruebas primero si `docker` no se encuentra desde WSL?

### NTFS (`/mnt/c`) y permisos
- **Qué es:** el sistema de ficheros de Windows. Desde WSL la carpeta aparece en `/mnt/c/...` y no guarda los permisos de Linux.
- **Dónde y cómo se usa en mi proyecto:** `core.filemode=false` en el repositorio, y `chmod 600` sobre `.env.dev` no surte efecto.
- **Por qué así:** se documenta con honestidad en el README. La alternativa es mover el repositorio al sistema de ficheros de WSL (`~/proyectos/...`), donde `chmod` sí funciona.
- **Pregunta de defensa:** ¿por qué `chmod 600` no funciona en tu carpeta y cómo lo solucionarías?

---

## 7. Automatización

### Make y Makefile (paso 1.6)
- **Qué es:** `make` ejecuta "atajos" (*targets*) definidos en un `Makefile`. Cada línea de comando debe empezar con un **tabulador**.
- **Para qué se usa:** convertir comandos largos en uno corto y reproducible.
- **Dónde y cómo se usa en mi proyecto:** `make build`, `make up-dev`, `make down`, `make ps` y `make logs` (y más adelante `make up-prod` y `make clean`). Una variable `COMPOSE_DEV = docker compose --env-file .env.dev -f docker-compose.dev.yml` guarda el comando base una sola vez y los targets la usan con `$(COMPOSE_DEV)`. Sustituye al `alias dc`, que se pierde al cerrar la terminal.
- **Por qué así:** lo exige el enunciado (Makefile o script). Un único sitio con el comando evita olvidar el `--env-file` o mezclar dev con prod. El nombre de proyecto ya lo fija `name:` en el compose, así que no se repite con `-p`.
- **`.PHONY`:** marca los targets que son acciones y no ficheros. Sin él, si existiera un fichero llamado `build`, `make build` diría que ya está hecho y no ejecutaría nada.
- **El tabulador:** si las líneas de comando empiezan con espacios, `make` falla con `*** missing separator. Stop.`. `.editorconfig` fuerza tabuladores en `[Makefile]`, pero solo si la extensión EditorConfig está activa. Se comprueba con `cat -A Makefile` (los tabuladores salen como `^I`).
- **`down` frente a `clean` (decisión 8):** `make down` ejecuta `docker compose down`, que para y elimina contenedores y red pero **conserva los volúmenes**, así que los datos de la BD sobreviven. `make clean` (adelantado al paso 2.1, porque la verificación necesita probar desde cero) ejecuta `down -v` para borrarlos también. Imprime antes un aviso con `@echo` (la `@` oculta el propio comando); no pide confirmación porque `make` usa `/bin/sh` (`dash` en Ubuntu), que no soporta `read -p`. Se comprueba con `docker volume ls | grep pgdata` tras un `make down`: el volumen sigue ahí.
- **`make logs`:** usa `logs -f --tail=50`: sigue los logs en directo empezando por las últimas 50 líneas. Se queda esperando; se sale con Ctrl+C.
- **Ensayo en seco:** `make -n up-dev` imprime el comando que ejecutaría sin ejecutarlo; es la forma segura de comprobar un Makefile.
- **Pregunta de defensa:** ¿qué hace `make up-dev` por debajo, y por qué el Makefile exige tabuladores?

---

## 8. Aplicación y base de datos

### PostgreSQL y `psql`
- **Qué es:** PostgreSQL es la base de datos relacional. `psql` es su cliente de línea de comandos.
- **Dónde y cómo se usa en mi proyecto:** servicio `db`. El "comando de prueba de conexión" del enunciado será un `psql` ejecutado **dentro** del contenedor, sin necesidad de publicar puerto. `pg_isready` es el healthcheck.
- **Por qué así:** el cliente viene en la imagen, así que no instalas nada en tu máquina.
- **Pregunta de defensa:** ¿cómo compruebas la conexión a la BD si no publica ningún puerto?

### `psycopg` y el extra `binary` (paso 1.4)
- **Qué es:** `psycopg` (versión 3) es el *driver* que permite a Python hablar con PostgreSQL. El extra `[binary]` instala `psycopg-binary`, una versión ya compilada que incluye la librería de C que necesita (`libpq`).
- **Para qué se usa:** abrir la conexión a la BD, ejecutar consultas SQL y leer los resultados desde `main.py`.
- **Dónde y cómo se usa en mi proyecto:** `psycopg[binary]==3.3.6` en `app/requirements.txt`. Se conecta al host `db` (nombre del servicio) con las credenciales que llegan como variables de entorno.
- **Por qué así:** sin `binary`, la imagen `slim` tendría que instalar compiladores y cabeceras de PostgreSQL para construir el driver, lo que la haría más pesada y ampliaría su superficie de ataque. La alternativa `psycopg2` es la generación anterior del mismo driver.
- **Pregunta de defensa:** ¿por qué se instala `psycopg[binary]` en lugar de `psycopg` a secas?

### Configuración desde variables de entorno y fallo rápido (paso 1.4)
- **Qué es:** la aplicación lee su configuración con `os.environ["NOMBRE"]`. Si la variable no existe, lanza `KeyError` **al arrancar** (*fail fast*), en lugar de fallar más tarde con un error confuso.
- **Dónde y cómo se usa en mi proyecto:** `main.py` lee `DB_HOST`, `POSTGRES_USER`, `POSTGRES_PASSWORD` y `POSTGRES_DB`, que Compose le pasa desde `.env.dev`. Ninguna credencial está en el código.
- **Por qué así:** si falta una variable, el contenedor se cae enseguida y `docker compose logs web` lo dice. La alternativa, `os.environ.get("X", "valor")`, escondería el fallo o, peor, pondría una contraseña por defecto en el código.
- **Prueba real:** `docker run --rm randomlocke-dev-web` (sin variables) termina al instante con `KeyError: 'DB_HOST'`, porque es la primera que se lee (línea 8 de `main.py`). Dándole las demás y omitiendo solo la contraseña, el error pasa a ser `KeyError: 'POSTGRES_PASSWORD'` (línea 10). El fallo ocurre al **importar** `main.py`, antes de atender ninguna petición, porque esas lecturas están a nivel de módulo.
- **Pregunta de defensa:** ¿qué ocurre si arrancas `web` sin la variable `POSTGRES_PASSWORD`?

### Cómo leer un *traceback* de Python y qué es un `KeyError` (paso 1.4)
- **Qué es:** un *traceback* es la lista de llamadas que llevó hasta un error, de la más antigua (arriba) a la más reciente (abajo). Lo importante está **al final**: la última línea dice el tipo de error y la anterior, en qué fichero y línea ocurrió. Un `KeyError: 'X'` significa "he buscado la clave `X` en un diccionario y no existe". `os.environ` se comporta como un diccionario de variables de entorno.
- **Dónde y cómo se usa en mi proyecto:** `KeyError: 'DB_HOST'` y `KeyError: 'POSTGRES_PASSWORD'`, con la línea `File "/app/main.py", line 8` o `line 10` justo antes. Las líneas de `uvicorn`, `click` o `importlib` son el funcionamiento interno del arranque y se pueden ignorar.
- **Por qué así:** saber leer el final del traceback permite localizar un fallo de configuración en segundos con `docker compose logs web`.
- **Pregunta de defensa:** si `web` se cae al arrancar con un `KeyError`, ¿dónde miras y qué te dice?

### Conexión por petición frente a *pool* de conexiones (paso 1.4)
- **Qué es:** abrir una conexión nueva en cada comprobación, o mantener un conjunto de conexiones abiertas y reutilizarlas (*pool*).
- **Dónde y cómo se usa en mi proyecto:** `/status` abre una conexión nueva, ejecuta `SELECT 1` con `connect_timeout=2` y la cierra.
- **Por qué así:** cada comprobación empieza de cero, así que nunca hay una conexión caducada tras reiniciarse la BD: el estado se **recupera solo**. Es la opción más simple y correcta para un endpoint de salud. A mayor escala se usaría un *pool* (`psycopg_pool`), que reutiliza conexiones pero necesita gestionar las caídas. El `connect_timeout` evita que `/status` se quede colgado si la BD no responde.
- **Pregunta de defensa:** ¿por qué `/status` no reutiliza una conexión abierta?

### FastAPI y Uvicorn (pasos 1.3 y 1.4)
- **Qué es:** FastAPI es el framework de la API; Uvicorn, el servidor que la ejecuta.
- **Dónde y cómo se usa en mi proyecto:** el contenedor `web` sirve la API y el frontend estático (HTML/CSS/JS) en un único puerto, con `/status`.
- **Por qué así:** un solo contenedor y un solo puerto publicado, y documentación interactiva en `/docs`.
- **Pregunta de defensa:** ¿por qué la web y el frontend van en el mismo contenedor?

### `requirements.txt` y versiones fijas (paso 1.3)
- **Qué es:** el fichero donde Python lista las librerías que necesita el proyecto. `fastapi==0.143.0` fija la versión exacta; `fastapi` a secas instalaría siempre la más reciente.
- **Para qué se usa:** que `pip install -r requirements.txt` instale lo mismo hoy y dentro de un mes.
- **Dónde y cómo se usa en mi proyecto:** `app/requirements.txt`, que el `Dockerfile` copia e instala en una capa propia. Contiene `fastapi` y `uvicorn`; `psycopg` (paso 1.4) y `redis` (paso 3.3) se añadirán cuando se necesiten. Las versiones se consultaron con `pip index versions <paquete>` dentro de una imagen `python:3.12-slim`, sin instalar nada en el equipo.
- **Por qué así:** sin versiones fijas, una actualización ajena podría romper la imagen sin tocar tu código. Solo se fijan las dependencias **directas**; las que arrastran (Starlette, Pydantic...) las elige pip. La alternativa más estricta es fijar también las transitivas con `pip freeze` o un fichero de bloqueo, a costa de más mantenimiento.
- **Pregunta de defensa:** ¿por qué fijar versiones en `requirements.txt` si siempre se puede instalar la última?

### Estructura de `app/` y la carpeta pública `static/` (paso 1.3)
- **Qué es:** `app/` contiene todo lo que forma parte de la imagen de `web`. Dentro, `static/` es la carpeta que la API **servirá al navegador**: lo que haya ahí es accesible públicamente.
- **Dónde y cómo se usa en mi proyecto:** `app/requirements.txt`, `app/main.py`, `app/Dockerfile` y `app/.dockerignore` van en la raíz de `app/`; solo HTML, CSS y JS van en `app/static/`.
- **Por qué así:** un `requirements.txt` dentro de `static/` quedaría descargable por cualquiera que visite la web, además de que el `Dockerfile` no lo encontraría al copiarlo. Caso real: el fichero se creó por error en `app/static/` y se detectó al fallar la verificación.
- **Pregunta de defensa:** ¿por qué no se pueden mezclar los ficheros de la aplicación con los que sirve la carpeta estática?

### Verificar sin instalar: `pip install --dry-run` y `docker run --rm -v` (paso 1.3)
- **Qué es:** `--dry-run` simula la instalación y lista lo que instalaría, sin hacerlo. `docker run --rm` crea un contenedor temporal que se borra al terminar. `-v "$PWD/app":/app` monta tu carpeta `app/` dentro de él.
- **Dónde y cómo se usa en mi proyecto:** para comprobar que las versiones de `requirements.txt` existen y son compatibles, sin instalar Python ni librerías en el equipo.
- **Por qué así:** se prueba en el mismo entorno (`python:3.12-slim`) que usará la imagen. Aquí el *bind mount* es de solo lectura puntual, así que no tiene el problema de permisos de NTFS que sí tendría con la base de datos.
- **Pregunta de defensa:** ¿qué significan `--rm` y `-v` en un `docker run`?

### `/status`
- **Qué es:** endpoint que consulta de forma real el estado de la BD y de la caché y lo devuelve en JSON.
- **Dónde y cómo se usa en mi proyecto:** BD caída → `503`; caché caída → `200` con estado `degraded`; en dev la caché figura como "no aplica". La UI lo consulta periódicamente y el healthcheck de `web` lo usa.
- **Por qué así:** la BD es imprescindible y la caché es opcional. Si el healthcheck de `web` fallara por la caché, el contenedor se marcaría `unhealthy` por un servicio no crítico.
- **Pregunta de defensa:** ¿por qué la BD caída da 503 y la caché caída solo `degraded`?

### Inicialización de la base de datos: `initdb.d` o SQL idempotente (decisión 5, paso 2.1)
- **Qué es:** las tablas tienen que crearse automáticamente (lo exige el enunciado: "inicializarse automáticamente o generarse al iniciar la aplicación"). Hay dos formas. **`initdb.d`:** la imagen de Postgres ejecuta los `.sql` que haya en `/docker-entrypoint-initdb.d`, **solo la primera vez**, cuando el volumen está vacío. **SQL idempotente al arrancar la app:** `web` ejecuta `CREATE TABLE IF NOT EXISTS ...` cada vez que arranca; si la tabla ya existe, no hace nada.
- **Para qué se usa:** que la base de datos tenga su esquema sin crearlo a mano.
- **Dónde y cómo se usa en mi proyecto:** pendiente de decidir (decisión 5). Con `initdb.d` habría una carpeta `db/` con un `.sql` montada en el servicio `db`; con SQL idempotente, el código estaría en `app/`.
- **Por qué importa la diferencia:** con `initdb.d`, si el volumen ya existe, el script **no se vuelve a ejecutar**, y para aplicar un cambio de esquema hay que borrar el volumen (`make clean`). Con SQL idempotente funciona con volúmenes ya existentes. Ojo: `IF NOT EXISTS` no modifica tablas ya creadas; para añadir una columna haría falta además `ALTER TABLE ... ADD COLUMN IF NOT EXISTS ...`.
- **Pregunta de defensa:** ¿qué ocurre con las tablas si reinicias la base de datos con el volumen ya lleno, según cada opción?

### Decisión 5 cerrada: SQL idempotente al arrancar la app (paso 2.1)
- **Qué es:** se eligió la opción B: `web` ejecuta `CREATE TABLE IF NOT EXISTS` al arrancar. Idempotente significa que ejecutarlo muchas veces da el mismo resultado.
- **Por qué así:** con `initdb.d` solo se ejecuta con el volumen vacío, y cambiar el esquema obligaría a borrar el volumen (perder datos), justo lo que demuestra la persistencia. El enunciado admite "generarse al iniciar la aplicación". `IF NOT EXISTS` no modifica tablas ya creadas: para una columna nueva se usaría `ALTER TABLE ... ADD COLUMN IF NOT EXISTS ...`. Por eso `encounters` incluye `details JSONB`: para ampliar el modelo en la Fase 2 sin tocar el esquema.
- **Pregunta de defensa:** ¿por qué se inicializa la BD desde la aplicación y no con `initdb.d`, y qué no resuelve `IF NOT EXISTS`?

### Inicialización al arrancar: `lifespan` y reintentos (paso 2.1)
- **Qué es:** el `lifespan` de FastAPI es un hook que ejecuta código **al arrancar** la aplicación, antes de atender peticiones (lo que va antes del `yield`). `inicializar_db()` lee `schema.sql` y lo ejecuta contra la BD, con hasta 10 intentos separados por 2 segundos; si se agotan, la excepción detiene el arranque (*fail fast*).
- **Dónde y cómo se usa en mi proyecto:** `app/main.py` (`inicializar_db` y `lifespan`) y `app/schema.sql`, que el `Dockerfile` copia con `COPY . .`. `conectar()` centraliza los parámetros de conexión y lo usan `inicializar_db` y `comprobar_db`. Se verifica con `make clean` y `make up-dev`: las tablas aparecen sin crearlas a mano, y con `make down` y `make up-dev` (volumen lleno) no hay errores.
- **Por qué así:** el `depends_on: service_healthy` cubre el arranque conjunto, pero no un reinicio de `web` con la BD caída; el reintento es una defensa barata. Como el SQL es idempotente, ejecutarlo en cada arranque es seguro. Es el cierre de la decisión 5 (opción B).
- **Prueba real:** se borraron las tablas con `DROP TABLE encounters, runs;` (`\dt` dijo `Did not find any relations`) y se reinició solo `web` con `docker compose restart web`: unos segundos después `\dt` volvía a mostrar `encounters` y `runs`, creadas por la aplicación. `db` seguía `Up 6 minutes`, es decir, no se había reiniciado. Reiniciar `db` con su volumen intacto tampoco pierde las tablas: los datos viven en el volumen, no en el contenedor.
- **Pregunta de defensa:** ¿qué ocurre con las tablas si reinicias solo `web`, y qué si borras el volumen?

### Modelo de datos: `runs`, `encounters` y el equipo derivado (paso 2.1)
- **Qué es:** `runs` guarda cada partida (`id`, `name`, `created_at`). `encounters` guarda cada evento (`id`, `run_id`, `event_type` ∈ {`captura`, `fallo`, `muerte`}, `route`, `species`, `created_at`, `details JSONB`). El **equipo activo** no se almacena: se calcula como las capturas sin una muerte posterior en la misma ruta.
- **Por qué así:** en un Nuzlocke solo se captura un Pokémon por ruta, así que la ruta identifica al Pokémon dentro de una partida, y la muerte se enlaza por ruta sin columnas extra (alternativa: una columna `capture_id`, más precisa pero más compleja). `event_type` será `TEXT` con `CHECK` en vez de un `ENUM` de Postgres, porque añadir un tipo después es más fácil; los identificadores usarán `GENERATED ALWAYS AS IDENTITY`, la forma estándar de autonumerar frente al antiguo `SERIAL`.
- **Pregunta de defensa:** ¿por qué registrar una muerte es un `INSERT` y no un `UPDATE`, y cómo se sabe qué Pokémon está vivo?

### Esquema SQL: claves, restricciones y tipos (paso 2.1)
- **Qué es:** `app/schema.sql` crea las tablas con `CREATE TABLE IF NOT EXISTS`. `PRIMARY KEY` identifica cada fila; `GENERATED ALWAYS AS IDENTITY` hace que Postgres autonumere ese identificador; `REFERENCES runs (id)` es una **clave foránea** (un evento no puede apuntar a una partida inexistente); `CHECK (event_type IN (...))` limita los valores admitidos; `NOT NULL` hace obligatorio un dato; `TIMESTAMPTZ DEFAULT now()` guarda fecha y hora con zona horaria y se rellena sola; `JSONB` guarda datos flexibles en JSON; `CREATE INDEX` acelera buscar los eventos de una partida.
- **Dónde y cómo se usa en mi proyecto:** tablas `runs` y `encounters` y el índice `idx_encounters_run_id`. Se prueba aplicando el fichero dos veces con `psql`: la segunda da `NOTICE: relation ... already exists, skipping`, lo que demuestra que es idempotente.
- **Por qué así:** las restricciones son una **segunda línea de defensa**: la API valida los datos, pero la base de datos tampoco admite datos inválidos si algo falla o alguien inserta a mano. La clave foránea y el `CHECK` mantienen la integridad.
- **Pregunta de defensa:** ¿qué hace `IF NOT EXISTS` y por qué la base de datos debe validar datos aunque la API ya lo haga?

### Consultas parametrizadas e inyección SQL (paso 2.2)
- **Qué es:** una **inyección SQL** ocurre cuando el texto que escribe el usuario se pega dentro de la sentencia SQL y la base de datos lo ejecuta como código. Con `f"... WHERE name = '{nombre}'"`, un nombre como `x'; DROP TABLE runs; --` cierra la cadena y ejecuta un `DROP`. Una consulta **parametrizada** envía por separado la sentencia (con huecos `%s`) y los datos, que la BD trata siempre como **valores**.
- **Dónde y cómo se usa en mi proyecto:** todas las consultas de `main.py` usan `%s` y una tupla de valores, por ejemplo `conn.execute("INSERT INTO runs (name) VALUES (%s) RETURNING id, name, created_at", (run.name,))`. Prueba real: crear una partida con el nombre `x'; DROP TABLE runs; --` devuelve `201`, se guarda como texto y la tabla `runs` sigue existiendo.
- **Por qué así:** es la defensa estándar y la más fiable; no depende de "limpiar" caracteres. Nunca se construye SQL concatenando datos del usuario.
- **Pregunta de defensa:** ¿por qué una consulta parametrizada evita la inyección SQL?

### Validación de entrada con Pydantic y códigos HTTP (paso 2.2)
- **Qué es:** Pydantic describe qué datos acepta un endpoint (`class RunNueva(BaseModel)` con `Field(min_length=1, max_length=100)`). FastAPI valida el cuerpo **antes** de ejecutar la función y, si no cumple, responde `422 Unprocessable Entity` con el detalle. `str_strip_whitespace=True` recorta espacios, así que un nombre de solo espacios queda vacío y se rechaza.
- **Códigos HTTP del proyecto:** `200` correcto, `201` recurso creado, `404` no existe, `409` conflicto con las reglas, `422` entrada inválida, `503` servicio de apoyo (BD) caído.
- **Dónde y cómo se usa en mi proyecto:** `POST /runs` devuelve `201` y el JSON de la fila creada (`RETURNING`); un nombre vacío da `422`. La documentación interactiva se genera sola en `/docs`.
- **Por qué así:** la validación en la API da errores claros al usuario; la BD (`NOT NULL`, `CHECK`, clave foránea) es la segunda línea de defensa si algo falla.
- **Pregunta de defensa:** ¿qué devuelve la API ante un nombre vacío y quién lo detecta primero, la API o la base de datos?

### Reglas de negocio: `409`, índices únicos parciales y condiciones de carrera (paso 2.2)
- **Qué es:** `POST /runs/{id}/events` aplica las reglas del Nuzlocke. `404` si la partida no existe; `422` si el tipo de evento no es `captura`, `fallo` o `muerte` (`Literal` en Pydantic) o faltan campos; `409 Conflict` cuando la petición es válida pero choca con el estado actual: segundo resultado de primer encuentro (`captura` o `fallo`) en la misma ruta, `muerte` sin captura previa en esa ruta, o segunda `muerte`. Un **índice único parcial** (`CREATE UNIQUE INDEX ... WHERE event_type IN (...)`) impide filas duplicadas solo para un subconjunto de filas.
- **Dónde y cómo se usa en mi proyecto:** la API comprueba las reglas leyendo los eventos previos de esa ruta y devuelve un mensaje claro; `schema.sql` define `uq_encounters_primer_encuentro`, que hace que la BD rechace un segundo resultado de primer encuentro aunque la API falle. La regla de "una sola muerte por ruta" se comprueba **solo en la API**, sin índice único, para no atar el esquema a una regla que podría ser configurable en la funcionalidad opcional de la Fase 4.
- **Por qué dos capas:** comprobar y luego insertar no es atómico (*condición de carrera*): dos peticiones simultáneas pueden pasar la comprobación a la vez. El índice único garantiza la regla siempre, y la API captura `UniqueViolation` y responde `409`. Además, los índices se aplicaron sobre el volumen ya existente porque `schema.sql` se ejecuta en cada arranque, algo que `initdb.d` no habría permitido sin borrar los datos.
- **Prueba real:** sobre la partida 1: captura en Ruta 1 → `201`; segunda captura en Ruta 1 → `409` («Esa ruta ya tiene un resultado de primer encuentro»); fallo en Ruta 2 → `201`; muerte en Ruta 2 sin captura → `409` («No hay ninguna captura en esa ruta»); tipo `huida` → `422` (`literal_error`); partida 999 → `404`. Insertar a mano en `psql` un segundo primer encuentro en Ruta 1 lo rechaza el índice único (`duplicate key value violates unique constraint "uq_encounters_primer_encuentro"`) aunque la API no intervenga.
- **Limitación conocida:** `"Ruta 1"` y `"ruta 1"` se consideran rutas distintas; normalizar mayúsculas sería una mejora.
- **Pregunta de defensa:** ¿por qué hace falta el índice único si la API ya comprueba las reglas?

### Reglas configurables por partida (idea opcional, Fase 4)
- **Qué es:** en vez de reglas fijas, el jugador elegiría las reglas de cada partida al crearla. Se guardarían en una columna `rules JSONB` de `runs`, por ejemplo `{"primer_encuentro": true, "clausula_especies": true, "objetos_curativos": false}`.
- **Tipos de regla:** *comprobables* (primer encuentro por ruta, cláusula de especies: la API responde `409`), *de honor* (prohibir objetos curativos, nivel máximo: solo se muestran, el juego no permite verificarlas) y *que cambian el modelo* (vidas por Pokémon: exigiría distinguir "debilitado" de "muerto" y replantear el equipo activo; queda fuera).
- **Dónde y cómo se usaría en mi proyecto:** `ALTER TABLE runs ADD COLUMN IF NOT EXISTS rules JSONB ...` en `schema.sql`, aplicado sobre el volumen existente al arrancar la app (ventaja de la decisión 5 B), y `POST /runs` aceptaría las reglas. Se haría en una **rama** (práctica del concepto del Tema 3).
- **Por qué así / estado:** generaliza la funcionalidad opcional «validador de reglas de la run». Solo se hará si se cierra el MVP a tiempo (Puerta 1, 13 oct); el plan permite como máximo una funcionalidad opcional. Pendiente de decidir por el alumno.
- **Pregunta de defensa:** ¿qué reglas de un Nuzlocke puede hacer cumplir la aplicación y cuáles dependen de la honestidad del jugador?

### Consultas derivadas: `NOT EXISTS` y *self join* (paso 2.2)
- **Qué es:** el equipo activo y el cementerio no se guardan: se **calculan** a partir de los eventos. `NOT EXISTS (subconsulta)` significa «no hay ninguna fila que cumpla esto»; un *self join* une una tabla consigo misma, usando dos alias (`c` para la captura y `m` para la muerte) enlazados por `(run_id, route)`.
- **Dónde y cómo se usa en mi proyecto:** `GET /runs/{id}/team` devuelve las capturas **sin** una `muerte` en la misma ruta (`NOT EXISTS`); `GET /runs/{id}/graveyard` devuelve las capturas **con** una `muerte` en la misma ruta (`JOIN`). Ambas devuelven la especie de la fila de la **captura** (`c.species`), no de la muerte, para que un error al escribir el nombre al registrar la muerte no altere el cementerio. `existe_run()` comprueba que la partida existe y da `404`; está definida una sola vez, junto a `comprobar_db`, y la usan los tres endpoints (`registrar_evento`, `equipo_activo` y `cementerio`) para no repetir código.
- **«Equipo activo» significa «Pokémon vivos»:** la consulta devuelve todas las capturas sin muerte, es decir, tanto los del equipo de 6 como los guardados en la PC. La aplicación no conoce esa distinción (es una mecánica del juego y solo ve eventos `captura`, `fallo` y `muerte`), y el límite de 6 es una regla de honor que no se comprueba. Por eso, en la interfaz la sección se llamará «Pokémon vivos». Distinguir equipo y PC sería una funcionalidad opcional: dos eventos nuevos (`a_caja` y `a_equipo`), con el estado derivado del último movimiento y una migración del `CHECK` de `event_type`.
- **Por qué así:** es coherente con el modelo *append-only*: registrar una muerte es un `INSERT` más, y el equipo cambia solo porque la consulta lo refleja. El `JOIN` es además lo que justifica la caché de la Fase 3: es una consulta con agregación entre filas, no una lectura trivial.
- **Pregunta de defensa:** ¿cómo se sabe qué Pokémon está vivo si nunca se actualiza ni se borra ninguna fila?

### Servir la interfaz desde la API: `StaticFiles`, orden de rutas y mismo origen (paso 2.3)
- **Qué es:** `app.mount("/", StaticFiles(directory=..., html=True))` hace que FastAPI sirva los ficheros de `app/static/` (HTML, CSS y JS) y que `/` devuelva `index.html`. Los montajes se evalúan **por orden** y uno en `/` captura todo lo que no coincida con otra ruta, así que va **al final** del fichero y las rutas de la API, antes. Se eliminó el antiguo `GET /` (un JSON), porque una ruta explícita tiene prioridad y taparía la página.
- **Política del mismo origen y CORS:** un navegador bloquea que el JavaScript de una página pida datos a un origen distinto (otro dominio, puerto o protocolo) salvo que ese servidor lo autorice con cabeceras CORS (`Access-Control-Allow-Origin`). Sirviendo la interfaz desde la propia API el origen es el mismo y no hace falta configurar CORS.
- **Dónde y cómo se usa en mi proyecto:** un solo contenedor `web` y un solo puerto publicado sirven la API y la interfaz. Se añadieron `GET /runs` (lista de partidas) y `GET /runs/{id}/encounters` (todos los eventos de una partida, para las capturas por ruta).
- **Por qué así:** cumple «solo `web` publica un puerto» sin proxy ni segundo contenedor, y evita CORS. Todo lo que está en `static/` es **público**: no debe haber ahí nada sensible (por eso `requirements.txt` no va en esa carpeta).
- **Pregunta de defensa:** ¿por qué la interfaz se sirve desde la propia API y qué bloquearía el navegador si estuviera en otro puerto?

### Interfaz sin frameworks: HTML, CSS y orden de carga (paso 2.3)
- **Qué es:** `app/static/` contiene tres ficheros: `index.html` (estructura), `style.css` (estilos) y `app.js` (comportamiento). Sin frameworks ni paso de *build* (lo que pide el plan): el navegador los carga tal cual.
- **Dónde y cómo se usa en mi proyecto:** `index.html` tiene la cabecera con el **indicador de estado** (`#estado-db`, un círculo, y `#estado-texto`), el selector y formulario de partida, el formulario de eventos y tres bloques: **Pokémon vivos**, **Capturas por ruta** y **Cementerio**. Las dos secciones que dependen de una partida elegida llevan el atributo `hidden`. `style.css` guarda los colores en variables (`--ok`, `--caido`, `--desconocido`) y define `.punto.ok/.caido/.desconocido`, las clases que el JS cambiará para pasar el círculo de verde a rojo.
- **Por qué así:** `hidden` en el HTML evita el parpadeo de ver secciones vacías antes de que se ejecute el JavaScript. El `<script>` va **al final del `body`**: si estuviera en el `<head>`, se ejecutaría antes de que existan los elementos y `getElementById` devolvería `null` (la alternativa es el atributo `defer`). `<meta name="viewport">` y una sola columna hacen que se vea bien en el móvil, que es el uso previsto (segunda pantalla). `role="alert"` hace que los lectores de pantalla anuncien los mensajes de error.
- **Pregunta de defensa:** ¿por qué el `<script>` va al final del `body` y por qué `hidden` está en el HTML y no se aplica con JavaScript?

### Estado en vivo: *polling* con `fetch` y `setInterval` (paso 2.3)
- **Qué es:** *polling* es preguntar al servidor cada cierto tiempo. `fetch("/status", { cache: "no-store" })` pide el estado a la propia API (ruta relativa: mismo origen, sin CORS) y `setInterval(actualizarEstado, 3000)` lo repite cada 3 segundos. `cache: "no-store"` evita que el navegador devuelva una respuesta guardada.
- **Dónde y cómo se usa en mi proyecto:** `app/static/app.js` actualiza el círculo y el texto del encabezado: verde y «BD conectada» si `/status` devuelve `{"db":"ok"}`, rojo y «BD caída» si devuelve `{"db":"down"}`, y rojo y «Sin conexión con la web» si ni siquiera responde la web. Con la BD caída `/status` da `503` pero con cuerpo JSON, así que `fetch` **no lanza error** (solo falla por red) y el JSON se lee igual; el `catch` cubre el caso de que la propia web no responda.
- **Prueba real (sin recargar la página):** con la BD parada con `docker compose stop db`, el indicador pasó a rojo/«BD caída»; al arrancarla de nuevo con `start db` volvió a verde/«BD conectada». La navegación de la página siguió siendo la original (`performance.getEntriesByType('navigation')[0].type` = `navigate`, no `reload`).
- **Por qué así:** WebSockets o *Server-Sent Events* serían más eficientes, pero añaden complejidad; consultar cada 3 s basta para un indicador de estado. Se usa `textContent` (texto plano) y no `innerHTML` para escribir en la página. En la Fase 3 se añadirá el estado de la caché (en dev, «no aplica»).
- **Pregunta de defensa:** ¿por qué `fetch` no lanza un error cuando `/status` devuelve `503`, y qué dos estados de fallo distingue el indicador?

### XSS y `textContent` frente a `innerHTML` (paso 2.3)
- **Qué es:** el *Cross-Site Scripting* (XSS) ocurre cuando texto que escribe un usuario se inserta en la página como **HTML**, y el navegador ejecuta el código que contiene (por ejemplo `<img src=x onerror="...">`). `innerHTML` interpreta el texto como HTML; `textContent` lo trata siempre como **texto literal**.
- **Dónde y cómo se usa en mi proyecto:** en `app.js`, todo lo que viene de la API (nombres de partida, rutas y especies) se escribe con `textContent` mediante la función `elemento(etiqueta, texto)` y con `new Option(texto, valor)`; `innerHTML` no aparece en ningún sitio.
- **Prueba real:** se creó una partida llamada `<b>hola</b><img src=x onerror="window.__xss=1">` y un evento con ruta `<i>Ruta</i>` y especie `<img src=x onerror="window.__xss=2">`. La página los muestra como texto (se ven las etiquetas), `window.__xss` sigue en `0`, y no se creó ningún `<img>` ni `<b>`. Es la misma idea que las consultas parametrizadas frente a la inyección SQL: tratar los datos **como datos, nunca como código**.
- **Pregunta de defensa:** si alguien guarda `<script>alert(1)</script>` como especie, ¿qué pasa con `innerHTML` y qué con `textContent`?

### Errores en la interfaz y tiempos con la BD caída (paso 2.3)
- **Qué es:** `pedir(url, opciones)` envuelve `fetch`: si la respuesta no es correcta lanza un `Error` con el mensaje de la API (`409`: «Esa ruta ya tiene un resultado de primer encuentro»; `422`: el primer `msg` de la validación); el `catch` de cada formulario lo muestra en `#mensaje`.
- **Hallazgo real:** con la BD parada, la API tarda **~3,1 s** en responder (`connect_timeout=2` más el reintento del DNS de Compose, que ya no resuelve `db`). `GET /status` devuelve `503` y un `POST` de evento devuelve `500` con texto plano («Internal Server Error»), que no es JSON, por lo que la interfaz mostraba «Solicitud no válida», un mensaje engañoso. El indicador pasa a rojo en unos segundos (hasta ~3 s de respuesta más hasta 3 s de intervalo de *polling*). El healthcheck de `web` tiene `timeout: 5s`, así que sigue marcando `unhealthy` correctamente.
- **Mejoras aplicadas:** (1) `pedir` distingue los errores `5xx` («El servidor no puede acceder a la base de datos ahora mismo. Inténtalo de nuevo.») de los errores de validación del usuario. (2) **Recuperación automática:** `dbAnterior` guarda el estado de la comprobación anterior y, al pasar de «caída» (`false`) a «conectada», `recuperar()` borra el mensaje y recarga las partidas conservando la elegida. La condición es `dbAnterior === false` y no `!dbAnterior` porque la primera vez vale `null` (aún no hay estado anterior) y no debe contar como recuperación. Comprobado sin recargar la página, incluso cargándola con la BD ya caída.
- **Pregunta de defensa:** ¿por qué tarda más de 3 s en responder `/status` con la BD caída y cómo afecta al healthcheck y al indicador?

### Modelo *append-only* (pendiente de ver en el paso 2.1)
- **Qué es:** los eventos solo se **añaden**, nunca se actualizan ni se borran.
- **Dónde y cómo se usa en mi proyecto:** `encounters` es un registro de eventos (captura, fallo, muerte). El equipo activo no se guarda: se **deriva** de las capturas sin muerte posterior.
- **Por qué así:** una muerte permanente no se revierte, así que es coherente con el dominio y con un registro inmutable.
- **Pregunta de defensa:** ¿por qué registrar una muerte es un `INSERT` y no un `UPDATE`?

---

## 9. Caché

### Redis y *cache-aside* (pendiente de ver en el paso 3.3)
- **Qué es:** Redis es una base de datos en memoria, muy rápida. *Cache-aside*: la aplicación mira primero la caché y, si no está (MISS), consulta la BD y guarda el resultado.
- **Dónde y cómo se usa en mi proyecto:** solo en prod (`cache`). Se cachea la lectura del equipo activo y se invalida al registrar un evento.
- **Por qué así:** el enunciado exige demostrar su uso. La invalidación se hace **después del `COMMIT`**: si fuera antes, una lectura intermedia podría volver a cachear el estado antiguo. A esta escala el beneficio es sobre todo pedagógico.
- **Pregunta de defensa:** ¿por qué se invalida la caché después del commit y no antes?

### TTL (pendiente de ver en el paso 3.3)
- **Qué es:** *time to live*: los segundos que un dato permanece en la caché antes de caducar.
- **Dónde y cómo se usa en mi proyecto:** cada entrada del equipo activo lleva un TTL; la UI muestra el TTL restante.
- **Por qué así:** actúa como red de seguridad si una invalidación falla: el dato antiguo desaparece solo.
- **Pregunta de defensa:** ¿qué aporta el TTL si ya invalidas la caché al escribir?

### Degradación elegante (pendiente de ver en el paso 3.3)
- **Qué es:** si un servicio no crítico falla, la aplicación sigue funcionando con menos prestaciones.
- **Dónde y cómo se usa en mi proyecto:** si Redis cae, la app consulta Postgres directamente y `/status` indica `degraded`.
- **Por qué así:** la caché es opcional y la BD es imprescindible.
- **Pregunta de defensa:** ¿qué pasa con la aplicación si cae Redis? ¿Y si cae Postgres?
