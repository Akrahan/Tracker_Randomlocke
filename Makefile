.DEFAULT_GOAL := help

.PHONY: help
help: ## Muestra esta ayuda (todos los comandos y lo que hacen)
	@awk 'BEGIN {FS = ":.*## "; print "\nUso: make <comando>"} /^##@/ {printf "\n%s\n", substr($$0, 5)} /^[a-zA-Z0-9_-]+:.*## / {printf "  %-14s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""

COMPOSE_DEV  = docker compose --env-file .env.dev  -f docker-compose.dev.yml
COMPOSE_PROD = docker compose --env-file .env.prod -f docker-compose.prod.yml

.PHONY: build-dev up-dev down-dev ps-dev logs-dev clean-dev \
        build-prod up-prod down-prod ps-prod logs-prod clean-prod \
        stop-cache start-cache stop-db start-db stop-web start-web psql-prod \n        seed-dev seed-prod reset-dev reset-prod fresh-dev fresh-prod fresh

##@ Desarrollo (dev, puerto 8000)
build-dev: ## Construye la imagen de web (dev) sin levantar nada
	$(COMPOSE_DEV) build

up-dev: ## Levanta DEV (web + db) en el puerto 8000, construyendo la imagen
	$(COMPOSE_DEV) up -d --build

down-dev: ## Para DEV; conserva los datos
	$(COMPOSE_DEV) down

ps-dev: ## Estado y salud de los contenedores de DEV
	$(COMPOSE_DEV) ps

logs-dev: ## Sigue los logs de DEV (Ctrl+C para salir)
	$(COMPOSE_DEV) logs -f --tail=50

clean-dev: ## Borra DEV con sus DATOS (volumen)
	@echo "Se eliminan contenedores, red y VOLUMENES de DEV (los datos de la base de datos)."
	$(COMPOSE_DEV) down -v

##@ Produccion (prod, puerto 8080)
build-prod: ## Construye la imagen de web (prod) sin levantar nada
	$(COMPOSE_PROD) build

up-prod: ## Levanta PROD (web + db + cache) en el puerto 8080, construyendo la imagen
	$(COMPOSE_PROD) up -d --build

down-prod: ## Para PROD; conserva los datos
	$(COMPOSE_PROD) down

ps-prod: ## Estado y salud de los contenedores de PROD
	$(COMPOSE_PROD) ps

logs-prod: ## Sigue los logs de PROD (Ctrl+C para salir)
	$(COMPOSE_PROD) logs -f --tail=50

clean-prod: ## Borra PROD con sus DATOS (volumen)
	@echo "Se eliminan contenedores, red y VOLUMENES de PROD (todas las partidas y eventos)."
	$(COMPOSE_PROD) down -v

##@ Simular fallos y comprobar (prod)
stop-cache: ## Simula la caida de Redis (PROD)
	$(COMPOSE_PROD) stop cache

start-cache: ## Recupera Redis (PROD)
	$(COMPOSE_PROD) start cache

stop-db: ## Simula la caida de PostgreSQL (PROD)
	$(COMPOSE_PROD) stop db

start-db: ## Recupera PostgreSQL (PROD)
	$(COMPOSE_PROD) start db

stop-web: ## Para la web (PROD)
	$(COMPOSE_PROD) stop web

start-web: ## Arranca la web (PROD)
	$(COMPOSE_PROD) start web

psql-prod: ## Prueba de conexion a la BD de PROD: SELECT 1 y lista de tablas
	$(COMPOSE_PROD) exec -T db sh -c 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" -c "SELECT 1 AS conexion_ok;" -c "\dt"'

# Datos de demostracion (scripts/seed-demo.sh es local y no esta en el repositorio)
##@ Datos de demostracion
seed-dev: ## Carga las partidas de demo en DEV (script local)
	@test -f scripts/seed-demo.sh || { echo "Falta scripts/seed-demo.sh (fichero local, no versionado)."; exit 1; }
	bash scripts/seed-demo.sh dev

seed-prod: ## Carga las partidas de demo en PROD (script local)
	@test -f scripts/seed-demo.sh || { echo "Falta scripts/seed-demo.sh (fichero local, no versionado)."; exit 1; }
	bash scripts/seed-demo.sh prod

# Empezar de cero: borra los datos, reconstruye, espera a "healthy" y carga la demo
reset-dev: ## Borra datos de DEV, reconstruye, espera y carga la demo
	$(MAKE) clean-dev
	$(COMPOSE_DEV) up -d --build --wait
	$(MAKE) seed-dev

reset-prod: ## Borra datos de PROD, reconstruye, espera y carga la demo
	$(MAKE) clean-prod
	$(COMPOSE_PROD) up -d --build --wait
	$(MAKE) seed-prod

# Desde cero absoluto: borra contenedores, redes, VOLUMENES e IMAGENES y reconstruye todo.
# Los "-" delante de docker image rm ignoran el error si una imagen no existe o la usa otro entorno.
##@ Empezar de cero
fresh-dev: ## DEV desde cero absoluto: sin datos, sin imagenes, reconstruido
	@echo "Se borra TODO el entorno DEV (datos e imagenes) y se reconstruye desde cero."
	$(COMPOSE_DEV) down -v --remove-orphans
	-docker image rm randomlocke-dev-web postgres:16 python:3.12-slim
	docker builder prune -af
	$(COMPOSE_DEV) up -d --build --wait
	-$(MAKE) seed-dev

fresh-prod: ## PROD desde cero absoluto: sin datos, sin imagenes, reconstruido
	@echo "Se borra TODO el entorno PROD (datos e imagenes) y se reconstruye desde cero."
	$(COMPOSE_PROD) down -v --remove-orphans
	-docker image rm randomlocke-prod-web postgres:16 redis:7-alpine python:3.12-slim
	docker builder prune -af
	$(COMPOSE_PROD) up -d --build --wait
	-$(MAKE) seed-prod

fresh: down ## PROD y DEV desde cero absoluto
	$(MAKE) fresh-prod
	$(MAKE) fresh-dev

.PHONY: down
##@ General
down: down-dev down-prod ## Para DEV y PROD; conserva los datos
