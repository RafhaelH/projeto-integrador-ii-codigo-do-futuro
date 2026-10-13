PROD_ENV ?= deploy/production.env
PROD_COMPOSE = docker compose --env-file $(PROD_ENV) -f compose.production.yaml

.PHONY: install db-up db-down migrate run test lint format check \
	prod-config prod-build prod-up prod-down prod-logs prod-check prod-seed prod-backup

install:
	uv sync

db-up:
	docker compose up -d database

db-down:
	docker compose down

migrate:
	uv run python src/manage.py migrate

run:
	uv run python src/manage.py runserver

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .
	uv run ruff check --fix .

check: lint test
	uv run python src/manage.py check
	uv run python src/manage.py makemigrations --check --dry-run

prod-config:
	./deploy/check-env.sh $(PROD_ENV)
	$(PROD_COMPOSE) config --quiet

prod-build: prod-config
	$(PROD_COMPOSE) build --pull app

prod-up: prod-config
	./deploy/deploy.sh $(PROD_ENV)

prod-down:
	$(PROD_COMPOSE) down

prod-logs:
	$(PROD_COMPOSE) logs --tail=200 -f app

prod-check:
	$(PROD_COMPOSE) exec -T app python src/manage.py check --deploy

prod-seed:
	$(PROD_COMPOSE) exec -T app python src/manage.py seed_demo --allow-production

prod-backup:
	./deploy/backup.sh $(PROD_ENV)
