COMPOSE_DEV = docker compose --env-file .env.dev -f docker-compose.dev.yml

.PHONY: build up-dev down ps logs clean

build:
	$(COMPOSE_DEV) build

up-dev:
	$(COMPOSE_DEV) up -d --build

down:
	$(COMPOSE_DEV) down

ps:
	$(COMPOSE_DEV) ps

logs:
	$(COMPOSE_DEV) logs -f --tail=50

clean:
	@echo "Se eliminan contenedores, red y VOLUMENES (los datos de la base de datos)."
	$(COMPOSE_DEV) down -v
