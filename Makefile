.PHONY: install db-up db-down migrate run test lint format check

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
