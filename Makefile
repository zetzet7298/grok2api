.PHONY: help build up down restart logs ps clean status health

help:
	@echo "Grok2API - Makefile"
	@echo "===================="
	@echo "Available targets:"
	@echo "  make build      - Build Docker image"
	@echo "  make up         - Start containers (production)"
	@echo "  make dev        - Start with live reload (local)"
	@echo "  make down       - Stop containers"
	@echo "  make restart    - Restart containers"
	@echo "  make logs       - View logs (follow)"
	@echo "  make ps         - Show container status"
	@echo "  make clean      - Remove containers and volumes"
	@echo "  make status     - Show service status"
	@echo "  make health     - Check container health"

build:
	@echo "Building Docker image..."
	docker compose build --no-cache

up:
	@echo "Starting Grok2API..."
	docker compose up -d --remove-orphans
	@echo "✅ Service started on http://localhost:8011"
	@echo "✅ Admin panel: http://localhost:8011/admin (password: grok2api)"

dev:
	@echo "Starting locally (not in Docker)..."
	@echo "Run: uv sync && uv run granian --interface asgi --host 0.0.0.0 --port 8000 main:app"

down:
	@echo "Stopping containers..."
	docker compose down

restart: down up

logs:
	docker compose logs -f --tail=100

logs-app:
	docker compose logs -f --tail=100 grok2api

ps:
	docker compose ps

status:
	@echo "=== Container Status ==="
	@docker compose ps
	@echo ""
	@echo "=== Resource Usage ==="
	docker stats --no-stream --format "table {{.Name}}\t{{.CPU}}\t{{.MemUsage}}\t{{.NetIO}}"

health:
	@echo "Checking container health..."
	@docker inspect --format='{{.State.Health.Status}}' grok2api 2>/dev/null || echo "No health check configured"

clean:
	@echo "⚠️  WARNING: This will remove ALL data including tokens!"
	@read -p "Are you sure? Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		docker compose down -v --remove-orphans; \
		echo "✅ Cleaned up"; \
	else \
		echo "Cancelled"; \
	fi

install-deps:
	@echo "Installing Python dependencies with uv..."
	uv sync

check-env:
	@echo "Checking environment configuration..."
	@if [ ! -f .env ]; then \
		echo "Creating .env from defaults..."; \
		echo "HOST_PORT=8011" > .env; \
		echo "SERVER_PORT=8000" >> .env; \
		echo "LOG_LEVEL=INFO" >> .env; \
		echo "✅ .env created"; \
	fi

exec:
	@docker compose exec grok2api $(CMD)

shell:
	@docker compose exec grok2api /bin/sh

admin:
	@echo "Admin panel: http://localhost:8011/admin"
	@echo "Default password: grok2api"