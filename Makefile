COMPOSE_DEV  = docker compose --env-file .env.dev  -f docker-compose.dev.yml
COMPOSE_PROD = docker compose --env-file .env.prod -f docker-compose.prod.yml

.PHONY: build-dev up-dev down-dev ps-dev logs-dev clean-dev \
        build-prod up-prod down-prod ps-prod logs-prod clean-prod \
        stop-cache start-cache stop-db start-db stop-web start-web psql-prod

build-dev:
	$(COMPOSE_DEV) build

up-dev:
	$(COMPOSE_DEV) up -d --build

down-dev:
	$(COMPOSE_DEV) down

ps-dev:
	$(COMPOSE_DEV) ps

logs-dev:
	$(COMPOSE_DEV) logs -f --tail=50

clean-dev:
	@echo "Se eliminan contenedores, red y VOLUMENES de DEV (los datos de la base de datos)."
	$(COMPOSE_DEV) down -v

build-prod:
	$(COMPOSE_PROD) build

up-prod:
	$(COMPOSE_PROD) up -d --build

down-prod:
	$(COMPOSE_PROD) down

ps-prod:
	$(COMPOSE_PROD) ps

logs-prod:
	$(COMPOSE_PROD) logs -f --tail=50

clean-prod:
	@echo "Se eliminan contenedores, red y VOLUMENES de PROD (todas las partidas y eventos)."
	$(COMPOSE_PROD) down -v

stop-cache:
	$(COMPOSE_PROD) stop cache

start-cache:
	$(COMPOSE_PROD) start cache

stop-db:
	$(COMPOSE_PROD) stop db

start-db:
	$(COMPOSE_PROD) start db

stop-web:
	$(COMPOSE_PROD) stop web

start-web:
	$(COMPOSE_PROD) start web

psql-prod:
	$(COMPOSE_PROD) exec -T db sh -c 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" -c "SELECT 1 AS conexion_ok;" -c "\dt"'

.PHONY: down
down: down-dev down-prod
