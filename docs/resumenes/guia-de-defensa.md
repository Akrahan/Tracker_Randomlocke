# Guía de defensa

> Preguntas probables del profesor, cada una con una respuesta de 3-4 líneas para decir en voz alta y apoyada en algo que se hizo de verdad. Se ordenan por temas. Para las demostraciones en directo, usa la [`chuleta-de-comandos.md`](chuleta-de-comandos.md). Para repasar el porqué de cada concepto: `docs/conceptos-para-estudiar.md`.
>
> **Consejo:** si no sabes algo, no inventes. Di qué comprobaste y qué no. Las limitaciones contadas con honestidad suman.

## Índice

1. [Visión general](#1-visión-general)
2. [Docker y Compose](#2-docker-y-compose)
3. [Datos y persistencia](#3-datos-y-persistencia)
4. [Red y seguridad](#4-red-y-seguridad)
5. [Healthchecks y estado](#5-healthchecks-y-estado)
6. [La caché](#6-la-caché)
7. [La aplicación](#7-la-aplicación)
8. [Make y Git](#8-make-y-git)
9. [Problemas reales que tuvimos](#9-problemas-reales-que-tuvimos)
10. [Preguntas incómodas](#10-preguntas-incómodas)
11. [Demostraciones en directo](#11-demostraciones-en-directo)

---

## 1. Visión general

**¿Qué hace tu práctica en una frase?**
Es una web de «segunda pantalla» para llevar una partida de Pokémon con muerte permanente: se apuntan capturas, fallos y muertes y se ve quién sigue vivo. Está desplegada con Docker Compose en dos entornos (dev y prod), con una base de datos PostgreSQL y, solo en producción, una caché Redis.

**¿Por qué necesitas un entorno de desarrollo y otro de producción?**
Dev es sencillo y desechable para programar y probar (sin caché, con `/docs` visible, puerto 8000). Prod simula el despliegue real: añade la caché, dos redes con una interna, reinicio automático y `/docs` oculta (puerto 8080). El código es el mismo; cambia la configuración. Pueden funcionar a la vez porque tienen nombre de proyecto, puerto y volúmenes distintos.

**¿Tu práctica es una arquitectura de microservicios?**
No: es un monolito con servicios de apoyo. La lógica de negocio está en un solo servicio (`web`); la base de datos y la caché son piezas de apoyo, no servicios de negocio independientes.

**¿Por qué la interfaz se sirve desde la propia API y no desde otro contenedor?**
Porque solo `web` puede publicar un puerto y así tengo un contenedor y un puerto. Además el navegador ve un único origen, así que no hace falta configurar CORS.

---

## 2. Docker y Compose

**¿Qué diferencia hay entre una imagen y un contenedor?**
La imagen es la receta, de solo lectura; el contenedor es una instancia en ejecución creada a partir de ella. Puedes crear muchos contenedores de la misma imagen y borrarlos sin perder la imagen. En el proyecto, `web` se construye desde mi `Dockerfile`; `db` y `cache` usan imágenes oficiales.

**¿Por qué `postgres:16` y no `latest`?**
Porque `latest` puede cambiar de versión mayor sin avisar y, en una base de datos, eso puede dejar ilegibles los datos del volumen. Fijar la versión hace el despliegue reproducible. Lo mismo con `python:3.12-slim`, `redis:7-alpine` y las dependencias con `==`.

**¿Por qué en el Dockerfile se copia `requirements.txt` antes que el resto del código?**
Por la caché de capas: si solo cambia `main.py`, Docker reutiliza la capa donde ya están instaladas las dependencias y no las vuelve a instalar. Si copiara todo primero, cualquier cambio de código invalidaría esa capa.

**¿Por qué `python:3.12-slim` y no `alpine`?**
`alpine` usa otra librería de C y algunos paquetes de Python dan problemas de compatibilidad. `slim` es pequeña y compatible. En cambio en Redis uso `alpine` porque no tiene esos problemas.

**¿Qué ventaja tiene Compose frente a ejecutar `docker run` por cada servicio?**
Describe todo el conjunto (servicios, redes, volúmenes, variables, orden de arranque) en un fichero que se levanta con un comando. Con `docker run` tendría que acordarme de cada opción y de crear las redes a mano.

**¿Por qué dos ficheros de Compose y no uno base con *overrides*?**
Porque el enunciado pide dos ficheros separados y así cada entorno se entiende leyendo solo uno. El coste es algo de duplicación, que acepto a esta escala.

**¿Qué diferencia hay entre `image:` y `build:`?**
`image:` descarga una imagen ya hecha (`postgres:16`); `build:` la construye desde un Dockerfile local (`./app`). La imagen de `web` se reconstruye con `up --build` (que es lo que hace `make up-prod`).

**¿Qué pasaría si dev y prod usaran el mismo `name:` o el mismo puerto?**
Con el mismo nombre de proyecto compartirían contenedores, redes y **volumen**, y se pisarían los datos; con el mismo puerto, el segundo no arrancaría porque el puerto estaría ocupado. Por eso son `randomlocke-dev` y `randomlocke-prod`, 8000 y 8080.

---

## 3. Datos y persistencia

**¿Cómo demuestras la persistencia?**
Anoto el ID del contenedor de la BD y el número de filas, elimino solo el contenedor (`docker compose rm -s -f db`) y lo recreo. En prod el ID pasó de `dc80222da005` a `c4abb313400c`, y el volumen y las filas (4 partidas y 12 eventos) eran los mismos. Los datos viven en el volumen, no en el contenedor.

**¿Qué rompería la persistencia?**
`docker compose down -v` (o `make clean-*`), que además de los contenedores borra los volúmenes. Por eso `make down` no lo hace y `clean` va separado por entorno y avisa antes.

**¿Qué diferencia hay entre `stop`, `rm -s -f` y `down -v`?**
`stop` para el contenedor sin eliminarlo; `rm -s -f` lo elimina; `down` elimina contenedores y redes; `down -v` además borra los volúmenes. Solo el último pierde los datos.

**¿Por qué un volumen con nombre y no un bind mount?**
El volumen lo gestiona Docker, está aislado y no depende de los permisos del disco. Mi proyecto está en NTFS, donde Postgres puede fallar con un bind mount por permisos.

**¿Cómo se crea el esquema de la BD?**
Lo crea la propia aplicación al arrancar, con SQL idempotente (`CREATE TABLE IF NOT EXISTS`). Elegí esto frente a `initdb.d` porque `initdb.d` solo se ejecuta con el volumen vacío; así funciona con volúmenes ya llenos y puedo añadir tablas sin borrar datos. Lo comprobé: la tabla `species` se añadió sobre una BD que ya tenía datos.

**¿Por qué registrar una muerte es un `INSERT` y no un `UPDATE`?**
Porque una muerte es irreversible y el registro debe ser inmutable: el modelo es *append-only*. Quién está vivo no se guarda, se deriva: capturas sin una muerte posterior en su ruta (`NOT EXISTS`). El cementerio es un *self join*.

**¿Cómo se carga la lista de especies y por qué sobrevive a `make clean-prod`?**
`web` lee `app/species.csv` (1025 especies, descargadas una vez de PokéAPI) al arrancar y las inserta con `INSERT ... ON CONFLICT (id) DO UPDATE`, que es idempotente. Por eso tras vaciar prod y volver a levantarlo, la tabla vuelve a tener 1025 filas sin ningún paso manual.

---

## 4. Red y seguridad

**¿Por qué solo `web` publica un puerto y cómo lo demuestras?**
Porque el enunciado lo exige y reduce la superficie de ataque. Con `make ps-prod` solo `web` aparece con `0.0.0.0:8080->8000`; `db` y `cache` solo muestran `5432/tcp` y `6379/tcp`. Además, una conexión TCP a 5432 o 6379 desde el host es rechazada.

**¿Qué pasaría si publicas el puerto de la base de datos?**
Cualquiera que llegara a tu máquina podría intentar conectarse a PostgreSQL, y dependería solo de la contraseña. Al no publicarlo, solo es accesible desde la red interna de Docker.

**¿Por qué `web` está en dos redes?**
Una red `internal: true` no permite publicar puertos ni salir a internet. Así que `web` está en `frontend` (normal, para publicar su puerto) y en `backend` (interna, donde están `db` y `cache`). `web` hace de puente.

**¿Cómo evitas credenciales en el repositorio y qué harías en un entorno real?**
Todo va por variables de entorno: en el YAML solo hay `${POSTGRES_PASSWORD}` y en Python `os.environ`. Los `.env` reales están en `.gitignore` y solo se versionan las plantillas con valores ficticios. Lo comprobé con `git ls-files`, el historial completo y el `404` de `.env.prod` en GitHub. En un entorno real usaría Docker secrets o un gestor de secretos.

**Si un `.env` se cuela en un commit y lo borras en el siguiente, ¿desaparece la contraseña?**
No: queda en el historial de Git. Por eso `.gitignore` se crea antes que los `.env`. A mí me pasó algo parecido: una contraseña real acabó en la plantilla, lo vi antes del primer `git add` y la regeneré.

**¿Por qué los procesos no corren como root y cómo lo comprobaste?**
Si alguien consigue ejecutar código dentro del contenedor, tendría permisos limitados. Con `docker top` comprobé `web` con uid 10001, `db` con 999 y `cache` con 999. Redis corría como root y lo detectó la revisión de seguridad: lo corregí con `user: redis`.

**¿Por qué desactivas `/docs` en producción?**
Para no enseñar a desconocidos el mapa completo de la API. Lo controla la variable `ENABLE_DOCS`, que vale `false` por defecto: si se olvida, no se publica. En dev la activo porque ahí es útil.

**¿Qué hace tu aplicación contra la inyección SQL y el XSS?**
Las consultas van parametrizadas (`%s`): el texto del usuario nunca se interpreta como SQL; lo probé guardando una partida llamada `x'; DROP TABLE runs; --`. En la interfaz escribo siempre con `textContent` y `new Option`, nunca con `innerHTML`; probé con `<img onerror=...>` y no se ejecutó nada.

**Si la consulta ya está parametrizada, ¿por qué hace falta `escapar_like`?**
Son dos protecciones distintas: los parámetros evitan que el texto sea SQL; el escape evita que sea un patrón de `LIKE`. Sin él, escribir `%` en el buscador casaría todas las especies.

**¿Por qué `chmod 600` no funciona en tu máquina?**
Porque el proyecto está en NTFS montado en WSL sin la opción `metadata`, y `chmod` no tiene efecto. Lo documento en el README; los `.env` están ignorados por Git y en un servidor Linux aplicaría `chmod 600`.

---

## 5. Healthchecks y estado

**¿Qué diferencia hay entre `depends_on` y un healthcheck?**
`depends_on` decide a quién esperar; el healthcheck decide cuándo un servicio está listo. Combinados (`condition: service_healthy`), `web` no arranca hasta que `db` y `cache` están sanos. «Arrancado» no es «listo»: Postgres tarda unos segundos en aceptar conexiones.

**¿Qué comprueba cada healthcheck?**
`db`: `pg_isready`. `cache`: `redis-cli ping` con la contraseña (variable `REDISCLI_AUTH`) y espera `PONG`. `web`: una petición a `/status` hecha con Python, porque la imagen `slim` no trae `curl`. Los tres corren cada 10 s.

**¿Por qué la BD caída da 503 y la caché caída solo `degraded`?**
Porque la BD es imprescindible y la caché es una optimización. Con la BD caída la aplicación no puede funcionar (`503`, y `web` pasa a `unhealthy` tras 3 fallos); con la caché caída sigue funcionando desde PostgreSQL (`200` con `degraded`) y no debe marcarse `unhealthy`.

**¿Cómo se refleja el estado en la interfaz?**
La cabecera consulta `/status` cada 3 segundos con `fetch` y pinta dos círculos (BD y caché) sin recargar la página. Si la BD cae, avisa; cuando vuelve, la página se recupera sola. En dev, la caché sale en gris con «no aplica».

**¿Reinicia Docker un contenedor `unhealthy`?**
No: `restart: unless-stopped` reinicia contenedores que **se paran**, no los que están `unhealthy`. El healthcheck solo marca el estado.

**¿Qué pasa si se apaga el ordenador y se enciende?**
En prod, `restart: unless-stopped` recupera los contenedores solos; en dev no tiene esa política y hay que volver a hacer `make up-dev`. Lo comprobé tras un reinicio: prod seguía `healthy` y dev aparecía `Exited`.

---

## 6. La caché

**¿Qué guardas en la caché y cómo?**
Dos cosas, con el patrón *cache-aside*: los Pokémon vivos de una partida (`team:<id>`, TTL 30 s) y las búsquedas del autocompletado (`species:<prefijo>:<límite>`, TTL 1 h). La API mira en Redis; si no está (`MISS`) consulta PostgreSQL, guarda con TTL y devuelve; si está (`HIT`), devuelve directamente.

**¿Por qué se invalida la caché después del `COMMIT` y no antes?**
Si invalidara antes, otra petición podría leer el dato viejo de la BD (la transacción aún no se ha confirmado) y volver a guardarlo en la caché, que quedaría desfasada. Lo hago fuera del bloque `with` de la conexión, que es donde se confirma. Lo comprobé: un registro rechazado (`409`) no invalida y uno confirmado sí.

**¿Para qué sirve el TTL si ya invalidas?**
Es la red de seguridad: si una invalidación falla, el dato viejo desaparece solo. Lo demostré cambiando un dato directamente en la BD, sin pasar por la API: la caché sirvió el dato viejo hasta que, a los 30 s, caducó.

**¿Por qué las especies tienen un TTL de una hora y no se invalidan?**
Porque son datos de referencia que no cambian mientras la aplicación corre. El equipo cambia con cada evento, por eso se invalida al escribir y tiene un TTL corto.

**¿Por qué la clave de las especies incluye el límite?**
Porque la clave debe incluir todo lo que cambia la respuesta: sin el límite, una petición con `limit=3` y otra con `limit=10` compartirían entrada y la segunda recibiría solo 3 resultados.

**¿Qué pasa con la aplicación si Redis cae? ¿Y si cae PostgreSQL?**
Si cae Redis, la web sigue funcionando leyendo de PostgreSQL: `/status` responde `200 degraded` y las lecturas salen `DEGRADED`. Registrar eventos sigue dando `201`. Si cae PostgreSQL, `/status` da `503`, la interfaz avisa y se recupera sola al volver.

**¿Qué ganas con la caché si la diferencia de velocidad no se nota?**
La carga que ahorra a la BD. Con 100 peticiones idénticas medí 7 transacciones con caché frente a 204 sin ella. La velocidad pasa de ~15 ms a ~1 ms en el servidor, pero a esta escala no se percibe; lo que escalaría es la carga.

**¿Por qué en dev no hay caché y el autocompletado funciona igual?**
Porque la caché es una optimización, no una dependencia: con `CACHE_ENABLED=false`, la consulta va directamente a PostgreSQL y la cabecera `X-Cache` vale `OFF`. El código es el mismo; cambia la configuración.

---

## 7. La aplicación

**¿Qué reglas del Nuzlocke aplica la API y quién las refuerza?**
Un solo resultado de primer encuentro por ruta (`409`) y una muerte solo si hay captura previa y una sola vez (`409`). La API da mensajes claros; la BD lo refuerza con un índice único parcial, que protege incluso ante dos peticiones simultáneas.

**¿Por qué hace falta el índice único si la API ya comprueba?**
Porque entre «comprobar» y «insertar» otra petición podría colarse. El índice garantiza la regla aunque la API falle. «Una sola muerte por ruta» queda solo en la API, para no atar el esquema a una regla que podría variar.

**¿Qué ocurre ante un nombre vacío o un tipo inválido?**
Pydantic lo rechaza con `422` antes de tocar la BD. La BD tiene además `NOT NULL` y `CHECK` como segunda línea de defensa.

**¿Por qué una conexión nueva por petición y no un *pool*?**
Porque se recupera sola cuando la BD vuelve de una caída, y es más simple. A esta escala el coste de abrir conexiones es despreciable; con mucha carga usaría un *pool*.

**¿Qué es el *debounce* del autocompletado?**
Esperar 200 ms sin teclear antes de pedir sugerencias. Escribir «zubat» deprisa lanza 1 petición en vez de 5, lo que protege la BD y la caché. Lo medí contando peticiones en el navegador.

---

## 8. Make y Git

**¿Qué hace `make up-prod` por debajo y por qué exige tabuladores el Makefile?**
Ejecuta `docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build`, guardado en la variable `COMPOSE_PROD`. Las líneas de comando deben empezar con un tabulador porque es la sintaxis de `make`; con espacios da `missing separator`.

**¿Para qué sirve `.PHONY`?**
Marca los targets que son acciones y no ficheros. Sin él, si existiera un fichero llamado `up-prod`, `make up-prod` diría que ya está hecho y no ejecutaría nada.

**¿Qué diferencia hay entre `make down` y `make clean-prod`?**
`down` apaga y elimina contenedores y redes pero conserva los datos; `clean-prod` hace `down -v` y borra todas las partidas. Por eso `clean` va separado por entorno y avisa antes.

**¿Cómo demuestras que tu proyecto funciona desde cero?**
Cloné el repositorio en una carpeta nueva, sin ningún `.env`, creé los ficheros desde las plantillas y levanté prod con otro nombre de proyecto y puerto para no tocar el real: tres contenedores `healthy`, `/status` ok y `MISS` → `HIT`. Una limitación: las capas de la imagen salieron en caché de Docker, así que no fue un *build* sin caché.

**¿Qué hace `.gitignore` y por qué se crea antes que los `.env`?**
Evita que se suban ficheros (los `.env`, el enunciado, `CLAUDE.md`). Solo protege lo que entra después, y un secreto subido una vez queda en el historial aunque se borre. Por eso es lo primero que se crea.

**¿Por qué `make` en WSL y no en Windows?**
Porque `make` no existe en Windows y los contenedores son Linux; con todo en WSL evito mezclar finales de línea (CRLF y LF), que rompen un Makefile.

---

## 9. Problemas reales que tuvimos

**La caché parada tumbaba la web. ¿Qué pasó y cómo lo resolviste?**
Con Redis parado, `web` pasaba a `unhealthy`. Medí en vez de adivinar: `redis-py` reintenta por defecto con esperas crecientes y los *timeouts* del cliente no cubren la resolución DNS, que en Docker Desktop tarda 3-8 s con un contenedor parado. Descarté un arreglo a medias (un temporizador) al ver en el registro del healthcheck que fallaba uno de cada dos chequeos. La solución: sin reintentos y un hilo vigilante que comprueba Redis cada 3 s y apunta el resultado en una variable, de modo que ninguna petición espera a Redis.

**La revisión de seguridad, ¿encontró algo?**
Dos cosas: Redis corría como root (mi `sh -c` se saltaba la bajada de privilegios de la imagen oficial) y `/docs` estaba abierta en producción. Corregí las dos y verifiqué: Redis con uid 999 y `/docs` con `404`.

**Una captura tuya muestra 8 segundos de latencia con la caché caída, ¿por qué?**
Es la primera petición justo después de parar Redis: hasta que el hilo vigilante la marca como caída, esa petición espera la resolución DNS de Docker Desktop (hasta ~8 s). Después las lecturas vuelven a ~13 ms, como muestra la captura siguiente. Está documentado como limitación.

**¿Tuviste algún problema con Git?**
Un `push` rechazado porque había editado un fichero en la web de GitHub. Lo resolví con `git pull --rebase` y resolviendo el conflicto a mano, sin `--force`, que habría sobrescrito lo del remoto.

---

## 10. Preguntas incómodas

**¿Qué hizo la IA y qué hiciste tú?**
Usé Claude Code (modelo Claude Sonnet 5.5) como tutor: me explicó los conceptos, revisó mi código y, en algunos pasos que le pedí expresamente, aplicó cambios (el rediseño del Makefile, la caché de las especies, la interfaz de sugerencias). Ejecutó también las pruebas de verificación y ayudó a redactar la documentación. Las decisiones de diseño son mías y revisé y probé cada paso; está detallado paso a paso en el diario, en el campo «Asistencia de IA».

**¿Qué limitaciones tiene tu práctica?**
Los permisos `chmod 600` no se aplican en NTFS; la primera lectura tras parar Redis puede tardar ~8 s; la verificación en limpio usó capas en caché; la caché a esta escala no se nota en velocidad; y no hay autenticación de usuarios. Las tengo documentadas en el README.

**¿Qué cambiarías para un entorno real?**
Usaría Docker secrets o un gestor de secretos en lugar de ficheros `.env`, un *pool* de conexiones, acotaría la memoria de Redis (`maxmemory`) y añadiría HTTPS con un proxy inverso y autenticación de usuarios.

**¿Por qué una web de Pokémon para una práctica de Docker?**
Porque las reglas del juego se traducen en conceptos técnicos defendibles: la muerte permanente en un modelo *append-only*, los Pokémon vivos como consulta derivada que se cachea, el primer encuentro por ruta como índice único. El valor está en el despliegue, no en el dominio.

**¿Usa tu aplicación alguna API externa mientras funciona?**
No. La lista de especies se descargó una sola vez de PokéAPI, se guardó en el repositorio (solo texto) y se carga en la BD al arrancar; así no hay dependencias externas que puedan fallar durante la ejecución.

---

## 11. Demostraciones en directo

La chuleta de comandos tiene el guion de cada una. Resumen de lo que te pueden pedir:

| Si te piden… | Qué haces |
|---|---|
| **Levantar de cero** | `make clean-prod` → `make up-prod` → `make ps-prod` (esperar a los tres `healthy`) |
| **Tumbar la caché** | `make stop-cache`, esperar ~12 s, `curl localhost:8080/status` → `degraded`; la web sigue funcionando. `make start-cache` |
| **Tumbar la BD** | `make stop-db`, `curl localhost:8080/status` → `503`; círculo rojo y aviso. `make start-db` |
| **Tumbar la web** | `make stop-web` → la página no responde; `make start-web` |
| **Persistencia** | Contar filas, `docker compose rm -s -f db`, `up -d db`, ID distinto y mismas filas |
| **Caché** | Dos lecturas de `/runs/<id>/team`: `MISS` y `HIT`; registrar un evento; `MISS` otra vez |
| **Solo `web` publica puerto** | `make ps-prod` y una conexión a 5432 desde el host (rechazada) |
| **Comprobar la BD** | `make psql-prod` |

**Precauciones:** tras `start-*` espera unos 25-30 s; `make down` no borra datos y `make clean-*` sí; no muestres nunca `.env.dev` ni `.env.prod` en pantalla.
