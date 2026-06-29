.PHONY: install dev test lint format migrate

install:
	uv sync --all-extras --dev

dev:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	uv run pytest

lint:
	uv run ruff check app tests

format:
	uv run ruff format app tests

migrate:
	psql "$$DATABASE_URL_SYNC" -f migrations/001_initial_schema.sql
