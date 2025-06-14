# TestPilot - AI-Driven Test Automation Platform

TestPilot is a hybrid (self-hosted and cloud) AI test automation platform that orchestrates lab workflows with real instruments including oscilloscopes, SMUs, VNAs, thermal chambers, and other test equipment. It combines AI agents with traditional test sequencing to create intelligent, adaptive testing workflows.

## 🚀 Quick Start

### Prerequisites

- Docker 24.0+ and Docker Compose
- Python 3.11+
- Rust 1.70+ (for instrument gateway)
- Node.js 20+ (for web interface)

### Setup Development Environment

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd TestPilot
   ```

2. **Setup environment**
   ```bash
   make setup-dev-env
   ```

3. **Start the development environment**
   ```bash
   make docker-up
   ```

4. **Access the services**
   - Web Interface: http://localhost:3000
   - AI Orchestrator: http://localhost:8001
   - Instrument Gateway: http://localhost:8002
   - Workflow Engine: http://localhost:8003
   - Data Pipeline: http://localhost:8004
   - Grafana: http://localhost:3001 (admin/admin)
   - Prometheus: http://localhost:9090

## 🏗️ Architecture

### Core Services

- **AI Orchestrator** (Python/FastAPI): LLM-powered workflow management
- **Instrument Gateway** (Rust): High-performance SCPI/VISA instrument communication
- **Workflow Engine** (Python/FastAPI): Test sequence execution
- **Data Pipeline** (Python/FastAPI): Time-series data processing
- **Web Interface** (React/TypeScript): Real-time monitoring and control

### Supporting Infrastructure

- **PostgreSQL**: Metadata and configuration storage
- **TimescaleDB**: Time-series measurement data
- **Redis**: Caching and session management
- **NATS**: Message queue for service communication
- **Qdrant**: Vector database for AI document retrieval
- **Prometheus/Grafana**: Monitoring and observability

## 🧭 Project Stacks: UIs & Instrument Gateways

TestPilot provides two alternative stacks for development and demonstration:

- **Full Stack (default, docker-compose.dev.yml):**
  - **Web Interface:** Full-featured React/TypeScript app (http://localhost:3000)
  - **Instrument Gateway:** High-performance Rust service (http://localhost:8002)
- **Simple Stack (docker-compose.simple.yml):**
  - **Web Interface:** Simple static HTML/JS app (http://localhost:3000)
  - **Instrument Gateway:** Python mock service (http://localhost:8002)

> **Note:** The default `make docker-up` uses the full stack. To use the simple stack, run:
> ```bash
> docker-compose -f docker-compose.simple.yml up
> ```

### Why Two UIs and Two Gateways?
- The **React UI** is the main interface for development and production.
- The **static UI** is for quick demos or environments without Node.js.
- The **Rust gateway** is for real instrument control and performance.
- The **Python gateway** is a mock for development or environments without Rust.

### Port Differences
- The simple stack maps Postgres to port 5434 (not 5432). Update your connection strings if switching between stacks.

### React Proxy Limitation
- The React app's `proxy` setting only supports forwarding to one backend (AI Orchestrator at :8001). For calls to other services (e.g., Instrument Gateway), use full URLs or set up a custom proxy.

## 🔧 Development

### Common Commands

```bash
# Build all services
make build

# Run tests
make test

# Run linting
make lint

# Show logs
make logs

# Stop environment
make docker-down

# Clean build artifacts
make clean
```

### Individual Service Development

```bash
# AI Orchestrator
make dev-ai

# Instrument Gateway
make dev-gateway

# Workflow Engine
make dev-workflow

# Data Pipeline
make dev-data

# Web Interface
make dev-web
```

## 📊 Features

### AI-Powered Capabilities

- **Natural Language Test Creation**: Describe tests in plain English
- **Intelligent Parameter Optimization**: AI-driven test parameter tuning
- **Failure Analysis**: Automated root cause analysis with suggestions
- **Predictive Maintenance**: Equipment health monitoring

### Instrument Support

- **Oscilloscopes**: Keysight MSO-X, Tektronix MSO, R&S RTO
- **SMUs**: Keysight B2900, Tektronix Keithley 2400
- **VNAs**: Keysight PNA-X, R&S ZVA, Copper Mountain
- **Signal Generators**: Various SCPI-compatible models
- **Custom Instruments**: Extensible driver architecture

### Protocol Support

- **SCPI over TCP/IP**: Primary communication protocol
- **VISA/GPIB**: Legacy instrument support
- **REST APIs**: Modern instrument interfaces
- **MQTT**: IoT sensors and environmental monitoring

## 🔒 Security

- **IEC 62443 Level 2 Compliance**: Industrial cybersecurity standards
- **JWT Authentication**: Secure API access
- **TLS 1.3 Encryption**: All network traffic encrypted
- **Audit Logging**: Comprehensive activity tracking
- **Role-Based Access Control**: Granular permissions

## 📈 Monitoring

### Health Checks

Each service exposes health endpoints:
- AI Orchestrator: http://localhost:8001/api/v1/health
- Instrument Gateway: http://localhost:8002/health
- Workflow Engine: http://localhost:8003/api/v1/health
- Data Pipeline: http://localhost:8004/api/v1/health

### Metrics

Prometheus metrics available at `/metrics` endpoints:
- Request rates and latencies
- Instrument connection status
- Test execution statistics
- Resource utilization

## 🧪 Testing

### Test Levels

- **Unit Tests**: Individual component testing
- **Integration Tests**: Service-to-service communication
- **Hardware-in-Loop**: Real instrument validation
- **Performance Tests**: Load and stress testing

### Running Tests

```bash
# All tests
make test

# Unit tests only
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Hardware tests (requires instruments)
pytest tests/hardware/ -v --instrument-config=config/test-instruments.yml
```

## 🌐 API Documentation

### AI Orchestrator API

- `POST /api/v1/ai/generate-test-plan`: Generate test plan from description
- `POST /api/v1/ai/optimize-parameters`: Optimize test parameters
- `POST /api/v1/ai/analyze-failure`: Analyze test failures
- `GET /api/v1/workflows`: List workflows
- `POST /api/v1/workflows`: Create workflow

### Instrument Gateway API

- `GET /instruments`: List instruments
- `POST /instruments`: Add instrument
- `POST /instruments/{id}/connect`: Connect to instrument
- `POST /instruments/{id}/command`: Send SCPI command

## 🔧 Configuration

### Environment Variables

Key configuration options (see `.env.example`):

```bash
# Database
DATABASE_URL=postgresql://testpilot:password@localhost:5432/test_automation
TIMESCALE_URL=postgresql://testpilot:password@localhost:5433/timeseries
REDIS_URL=redis://localhost:6379

# AI
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=your-key-here
VECTOR_STORE_URL=http://localhost:6333

# Security
JWT_SECRET_KEY=your-secret-key
```

### Instrument Configuration

Instruments can be configured via:
1. Web interface
2. API calls
3. Configuration files
4. Auto-discovery (network scanning)

## 📋 Deployment

### Local Development
```bash
make docker-up
```

### Production Deployment
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy with secrets
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes
```bash
# Deploy to Kubernetes
make k8s-deploy
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run linting and tests
6. Submit a pull request

### Code Style

- **Python**: Black formatting, ruff linting, type hints required
- **Rust**: rustfmt formatting, clippy linting
- **TypeScript**: Prettier formatting, ESLint linting

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- Documentation: https://docs.testpilot.ai
- Issues: https://github.com/company/testpilot/issues
- Slack: #testpilot-support
- Email: support@testpilot.ai

## 🗺️ Roadmap

### Q2 2025
- Enhanced AI capabilities with multimodal models
- Advanced waveform analysis
- Real-time collaboration features

### Q3 2025
- Edge computing support for remote labs
- Mobile app for monitoring
- Advanced analytics dashboard

### Q4 2025
- Quantum instrument integration
- Enhanced security features
- Performance optimizations

### 2026
- Autonomous lab management
- Industry-specific templates
- Advanced ML capabilities