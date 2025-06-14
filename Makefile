.PHONY: help setup-dev-env build test lint clean docker-build docker-up docker-down

# Default target
help:
	@echo "Available commands:"
	@echo "  setup-dev-env     - Setup development environment"
	@echo "  build            - Build all components"
	@echo "  test             - Run test suite"
	@echo "  lint             - Run linting"
	@echo "  clean            - Clean build artifacts"
	@echo "  docker-build     - Build Docker images"
	@echo "  docker-up        - Start development environment"
	@echo "  docker-down      - Stop development environment"
	@echo "  db-migrate       - Run database migrations"
	@echo "  logs             - Show container logs"

# Setup development environment
setup-dev-env:
	@echo "Setting up development environment..."
	@command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed. Aborting." >&2; exit 1; }
	@command -v docker-compose >/dev/null 2>&1 || { echo "Docker Compose is required but not installed. Aborting." >&2; exit 1; }
	@echo "Creating Python virtual environment..."
	python3 -m venv venv
	@echo "Activating virtual environment and installing dependencies..."
	. venv/bin/activate && pip install -r requirements.txt -r requirements-dev.txt
	@echo "Setup complete! Run 'make docker-up' to start the development environment."

# Build all components
build:
	@echo "Building all components..."
	docker-compose -f docker-compose.dev.yml build

# Run tests
test:
	@echo "Running tests..."
	. venv/bin/activate && pytest tests/ -v --cov=src/

# Run linting
lint:
	@echo "Running linting..."
	. venv/bin/activate && black --check src/
	. venv/bin/activate && ruff check src/
	. venv/bin/activate && mypy src/

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	docker system prune -f
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build Docker images
docker-build:
	@echo "Building Docker images..."
	docker-compose -f docker-compose.dev.yml build

# Start development environment
docker-up:
	@echo "Starting development environment..."
	docker-compose -f docker-compose.dev.yml up -d
	@echo "Environment started! Services available at:"
	@echo "  Web Interface: http://localhost:3000"
	@echo "  AI Orchestrator: http://localhost:8001"
	@echo "  Instrument Gateway: http://localhost:8002"
	@echo "  Workflow Engine: http://localhost:8003"
	@echo "  Data Pipeline: http://localhost:8004"
	@echo "  Grafana: http://localhost:3001 (admin/admin)"
	@echo "  Prometheus: http://localhost:9090"

# Stop development environment
docker-down:
	@echo "Stopping development environment..."
	docker-compose -f docker-compose.dev.yml down

# Database migrations
db-migrate:
	@echo "Running database migrations..."
	docker-compose -f docker-compose.dev.yml exec postgres createdb -U testpilot test_automation || true
	docker-compose -f docker-compose.dev.yml exec timescaledb createdb -U testpilot timeseries || true

# Show logs
logs:
	@echo "Showing container logs..."
	docker-compose -f docker-compose.dev.yml logs -f

# Development shortcuts
dev-ai:
	@echo "Starting AI Orchestrator in development mode..."
	. venv/bin/activate && cd src/ai_orchestrator && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001

dev-gateway:
	@echo "Starting Instrument Gateway in development mode..."
	cd src/instrument_gateway && cargo run

dev-workflow:
	@echo "Starting Workflow Engine in development mode..."
	. venv/bin/activate && cd src/workflow_engine && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8003

dev-data:
	@echo "Starting Data Pipeline in development mode..."
	. venv/bin/activate && cd src/data_pipeline && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8004

dev-web:
	@echo "Starting Web Interface in development mode..."
	cd src/web_interface && npm start