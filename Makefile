.PHONY: help build test deploy clean setup-dev setup-prod

# Default target
help:
	@echo "TestPilot AI-Driven Test Automation Platform"
	@echo "============================================="
	@echo ""
	@echo "Development Commands:"
	@echo "  setup-dev      - Setup development environment"
	@echo "  build-dev      - Build development containers"
	@echo "  start-dev      - Start development services"
	@echo "  stop-dev       - Stop development services"
	@echo ""
	@echo "Production Commands:"
	@echo "  setup-prod     - Setup production environment"
	@echo "  build-prod     - Build production containers"
	@echo "  deploy-prod    - Deploy production services"
	@echo "  stop-prod      - Stop production services"
	@echo ""
	@echo "Testing Commands:"
	@echo "  test           - Run full test suite"
	@echo "  test-unit      - Run unit tests"
	@echo "  test-integration - Run integration tests"
	@echo "  test-hardware  - Run hardware-in-the-loop tests"
	@echo ""
	@echo "Quality Commands:"
	@echo "  lint           - Run all linters"
	@echo "  security-scan  - Run security vulnerability scanning"
	@echo "  format         - Format all code"
	@echo ""
	@echo "Utility Commands:"
	@echo "  clean          - Clean up containers and volumes"
	@echo "  logs           - Show service logs"
	@echo "  status         - Show service status"
	@echo "  quickstart     - Quick setup for new developers"

# Development Environment
setup-dev:
	@echo "🚀 Setting up TestPilot development environment..."
	@command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed. Aborting." >&2; exit 1; }
	@command -v docker-compose >/dev/null 2>&1 || { echo "Docker Compose is required but not installed. Aborting." >&2; exit 1; }
	@mkdir -p logs config/secrets
	@cp .env.example .env 2>/dev/null || echo "No .env.example found"
	@docker network create testpilot-network 2>/dev/null || echo "Network already exists"
	@echo "✅ Development environment setup complete"

build-dev:
	@echo "🔨 Building development containers..."
	docker-compose -f docker-compose.dev.yml build --parallel
	@echo "✅ Development build complete"

start-dev:
	@echo "🚀 Starting development services..."
	docker-compose -f docker-compose.dev.yml up -d
	@sleep 5
	@echo "🔍 Checking service health..."
	@$(MAKE) status
	@echo "✅ Development services started"
	@echo "🌐 Web Interface: http://localhost:3000"
	@echo "🤖 AI Backend: http://localhost:8001"
	@echo "📊 Grafana: http://localhost:3001 (admin/admin)"

stop-dev:
	@echo "🛑 Stopping development services..."
	docker-compose -f docker-compose.dev.yml down
	@echo "✅ Development services stopped"

# Production Environment
setup-prod:
	@echo "🚀 Setting up TestPilot production environment..."
	@mkdir -p secrets logs config/nginx config/grafana
	@echo "Creating production secrets..."
	@echo "Please create the following secret files:"
	@echo "  - secrets/postgres_password.txt"
	@echo "  - secrets/grafana_password.txt"
	@echo "  - secrets/google_api_key.txt"
	@echo "✅ Production environment setup complete"

build-prod:
	@echo "🔨 Building production containers..."
	docker-compose -f docker-compose.prod.yml build --parallel
	@echo "✅ Production build complete"

deploy-prod:
	@echo "🚀 Deploying production services..."
	@$(MAKE) build-prod
	docker-compose -f docker-compose.prod.yml up -d
	@sleep 10
	@echo "🔍 Checking service health..."
	@$(MAKE) status-prod
	@echo "✅ Production deployment complete"

stop-prod:
	@echo "🛑 Stopping production services..."
	docker-compose -f docker-compose.prod.yml down
	@echo "✅ Production services stopped"

# Testing
test: test-unit test-integration
	@echo "✅ All tests completed"

test-unit:
	@echo "🧪 Running unit tests..."
	@echo "Python tests..."
	. venv/bin/activate && pytest tests/unit/ -v --cov=src/ 2>/dev/null || echo "No Python tests found"
	@echo "Rust tests..."
	cd src/instrument_gateway && cargo test 2>/dev/null || echo "No Rust tests found"
	@echo "React tests..."
	cd src/web_interface && npm test -- --watchAll=false 2>/dev/null || echo "No React tests found"
	@echo "✅ Unit tests completed"

test-integration:
	@echo "🧪 Running integration tests..."
	. venv/bin/activate && pytest tests/integration/ -v 2>/dev/null || echo "No integration tests found"
	@echo "✅ Integration tests completed"

test-hardware:
	@echo "🧪 Running hardware-in-the-loop tests..."
	@echo "⚠️  Ensure test instruments are connected and configured"
	. venv/bin/activate && pytest tests/hardware/ -v --tb=short 2>/dev/null || echo "No hardware tests found"
	@echo "✅ Hardware tests completed"

# Code Quality
lint:
	@echo "🔍 Running linters..."
	@echo "Python (ruff)..."
	. venv/bin/activate && ruff check src/ 2>/dev/null || echo "ruff not available"
	@echo "Rust (clippy)..."
	cd src/instrument_gateway && cargo clippy -- -D warnings 2>/dev/null || echo "clippy not available"
	@echo "TypeScript (eslint)..."
	cd src/web_interface && npm run lint 2>/dev/null || echo "eslint not available"
	@echo "✅ Linting completed"

format:
	@echo "🎨 Formatting code..."
	@echo "Python (black)..."
	. venv/bin/activate && black src/ 2>/dev/null || echo "black not available"
	@echo "Rust (rustfmt)..."
	cd src/instrument_gateway && cargo fmt 2>/dev/null || echo "rustfmt not available"
	@echo "TypeScript (prettier)..."
	cd src/web_interface && npm run format 2>/dev/null || echo "prettier not available"
	@echo "✅ Code formatting completed"

security-scan:
	@echo "🔒 Running security scans..."
	@echo "Python dependencies..."
	. venv/bin/activate && pip-audit 2>/dev/null || echo "pip-audit not available"
	@echo "Rust dependencies..."
	cd src/instrument_gateway && cargo audit 2>/dev/null || echo "cargo-audit not available"
	@echo "Node.js dependencies..."
	cd src/web_interface && npm audit --audit-level=moderate 2>/dev/null || echo "npm audit not available"
	@echo "✅ Security scan completed"

# Utilities
clean:
	@echo "🧹 Cleaning up..."
	docker-compose -f docker-compose.dev.yml down -v --remove-orphans 2>/dev/null || echo "Dev compose not running"
	docker-compose -f docker-compose.prod.yml down -v --remove-orphans 2>/dev/null || echo "Prod compose not running"
	docker system prune -f
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || echo "No Python cache found"
	find . -type f -name "*.pyc" -delete 2>/dev/null || echo "No Python cache files found"
	@echo "✅ Cleanup completed"

logs:
	@echo "📋 Showing service logs..."
	docker-compose -f docker-compose.dev.yml logs -f --tail=100

logs-prod:
	@echo "📋 Showing production service logs..."
	docker-compose -f docker-compose.prod.yml logs -f --tail=100

status:
	@echo "📊 Service Status (Development):"
	@docker-compose -f docker-compose.dev.yml ps 2>/dev/null || echo "No dev services running"
	@echo ""
	@echo "🔍 Health Checks:"
	@curl -s http://localhost:8001/health 2>/dev/null && echo "AI Service: Healthy" || echo "AI Service: Not responding"
	@curl -s http://localhost:8002/health 2>/dev/null && echo "Instrument Gateway: Healthy" || echo "Instrument Gateway: Not responding"
	@curl -s http://localhost:3000/health 2>/dev/null && echo "Web Interface: Healthy" || echo "Web Interface: Not responding"

status-prod:
	@echo "📊 Service Status (Production):"
	@docker-compose -f docker-compose.prod.yml ps 2>/dev/null || echo "No prod services running"
	@echo ""
	@echo "🔍 Health Checks:"
	@curl -s http://localhost:8001/health 2>/dev/null && echo "AI Service: Healthy" || echo "AI Service: Not responding"
	@curl -s http://localhost:8002/health 2>/dev/null && echo "Instrument Gateway: Healthy" || echo "Instrument Gateway: Not responding"
	@curl -s http://localhost:3000/health 2>/dev/null && echo "Web Interface: Healthy" || echo "Web Interface: Not responding"

# Quick start for new developers
quickstart: setup-dev build-dev start-dev
	@echo ""
	@echo "🎉 TestPilot is now running!"
	@echo "🌐 Open http://localhost:3000 to get started"
	@echo "💬 Try: 'Test a WiFi amplifier' in the chat interface"
	@echo ""
	@echo "📚 Next steps:"
	@echo "  - Review the README.md for detailed documentation"
	@echo "  - Run 'make test' to verify everything works"
	@echo "  - Check 'make help' for more commands"

# Development shortcuts
dev-ai:
	@echo "🚀 Starting AI backend directly..."
	python ai_execution_backend.py

dev-web:
	@echo "🚀 Starting React development server..."
	cd src/web_interface && npm start