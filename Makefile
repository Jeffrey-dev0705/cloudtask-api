.PHONY: up down logs migrate migration test lint format
up:
	cp -n .env.example .env || true
	docker compose up -d --build
down:
	docker compose down
logs:
	docker compose logs -f api worker
migration:
	docker compose exec api alembic revision --autogenerate -m "$(m)"
migrate:
	docker compose exec api alembic upgrade head
test:
	pytest -q
lint:
	ruff check .
format:
	ruff format .
