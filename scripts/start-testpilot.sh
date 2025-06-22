#!/bin/bash
# TestPilot Production Startup Script
# Orchestrates all services with proper health checking and error handling

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MAX_RETRIES=30
RETRY_INTERVAL=2
TIMEOUT=300

# Logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌${NC} $1"
}

# Health check function
check_service_health() {
    local service_name=$1
    local health_url=$2
    local retries=0
    
    log "Checking health of $service_name..."
    
    while [ $retries -lt $MAX_RETRIES ]; do
        if curl -f -s "$health_url" >/dev/null 2>&1; then
            log_success "$service_name is healthy"
            return 0
        fi
        
        retries=$((retries + 1))
        log "Attempt $retries/$MAX_RETRIES: $service_name not ready, waiting ${RETRY_INTERVAL}s..."
        sleep $RETRY_INTERVAL
    done
    
    log_error "$service_name failed to become healthy after $((MAX_RETRIES * RETRY_INTERVAL)) seconds"
    return 1
}

# Wait for database to be ready
wait_for_database() {
    log "Waiting for PostgreSQL to be ready..."
    
    local retries=0
    while [ $retries -lt $MAX_RETRIES ]; do
        if docker-compose exec -T postgres pg_isready -U testpilot >/dev/null 2>&1; then
            log_success "PostgreSQL is ready"
            return 0
        fi
        
        retries=$((retries + 1))
        log "Attempt $retries/$MAX_RETRIES: PostgreSQL not ready, waiting ${RETRY_INTERVAL}s..."
        sleep $RETRY_INTERVAL
    done
    
    log_error "PostgreSQL failed to become ready"
    return 1
}

# Check dependencies
check_dependencies() {
    log "Checking dependencies..."
    
    if ! command -v docker >/dev/null 2>&1; then
        log_error "Docker is required but not installed"
        exit 1
    fi
    
    if ! command -v docker-compose >/dev/null 2>&1; then
        log_error "Docker Compose is required but not installed"
        exit 1
    fi
    
    if ! command -v curl >/dev/null 2>&1; then
        log_error "curl is required but not installed"
        exit 1
    fi
    
    log_success "All dependencies are available"
}

# Create necessary directories
setup_directories() {
    log "Setting up directories..."
    
    mkdir -p logs
    mkdir -p config/secrets
    mkdir -p config/nginx
    mkdir -p config/grafana
    mkdir -p data/postgres
    mkdir -p data/timescaledb
    mkdir -p data/redis
    mkdir -p data/qdrant
    
    log_success "Directories created"
}

# Generate default configuration files
setup_configuration() {
    log "Setting up configuration..."
    
    # Create .env if it doesn't exist
    if [ ! -f .env ]; then
        log "Creating default .env file..."
        cat > .env << EOF
# TestPilot Environment Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO

# Database
POSTGRES_DB=test_automation
POSTGRES_USER=testpilot
POSTGRES_PASSWORD=testpilot_dev

# Redis
REDIS_PASSWORD=testpilot_redis_dev

# API Keys (set these for production)
GOOGLE_API_KEY=your_google_api_key_here

# Network
INSTRUMENT_NETWORK=192.168.100.0/24
EOF
        log_warning "Please edit .env file with your API keys and settings"
    fi
    
    log_success "Configuration setup complete"
}

# Start infrastructure services first
start_infrastructure() {
    log "Starting infrastructure services..."
    
    # Start databases and messaging
    docker-compose up -d postgres timescaledb redis nats qdrant
    
    # Wait for databases
    wait_for_database
    
    log_success "Infrastructure services started"
}

# Start application services
start_applications() {
    log "Starting application services..."
    
    # Start monitoring
    docker-compose up -d prometheus grafana
    
    # Start core services
    docker-compose up -d ai-orchestrator instrument-gateway
    
    # Wait for backend services
    check_service_health "AI Orchestrator" "http://localhost:8001/health"
    check_service_health "Instrument Gateway" "http://localhost:8002/health"
    
    # Start web interface last
    docker-compose up -d web-interface
    
    # Check web interface
    check_service_health "Web Interface" "http://localhost:3000/health"
    
    log_success "Application services started"
}

# Display service status
show_status() {
    log "Service Status:"
    echo
    
    # Show running containers
    docker-compose ps
    echo
    
    # Show service URLs
    echo -e "${BLUE}🌐 Service URLs:${NC}"
    echo "  Web Interface:     http://localhost:3000"
    echo "  AI Orchestrator:   http://localhost:8001"
    echo "  Instrument Gateway: http://localhost:8002"
    echo "  Grafana:          http://localhost:3001 (admin/admin)"
    echo "  Prometheus:       http://localhost:9090"
    echo
    
    # Health check all services
    echo -e "${BLUE}🔍 Health Status:${NC}"
    
    services=(
        "AI Orchestrator:http://localhost:8001/health"
        "Instrument Gateway:http://localhost:8002/health"
        "Web Interface:http://localhost:3000/health"
        "Prometheus:http://localhost:9090/-/healthy"
    )
    
    for service in "${services[@]}"; do
        name="${service%%:*}"
        url="${service#*:}"
        
        if curl -f -s "$url" >/dev/null 2>&1; then
            echo -e "  ${name}: ${GREEN}Healthy${NC}"
        else
            echo -e "  ${name}: ${RED}Unhealthy${NC}"
        fi
    done
}

# Cleanup function for graceful shutdown
cleanup() {
    log "Shutting down services..."
    docker-compose down
    log_success "Shutdown complete"
}

# Trap signals for graceful shutdown
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║                    TestPilot Startup                     ║"
    echo "║            AI-Driven Test Automation Platform           ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Parse command line arguments
    COMPOSE_FILE="docker-compose.dev.yml"
    ENVIRONMENT="development"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --production|-p)
                COMPOSE_FILE="docker-compose.prod.yml"
                ENVIRONMENT="production"
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [--production|-p] [--help|-h]"
                echo "  --production, -p    Start in production mode"
                echo "  --help, -h          Show this help message"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    log "Starting TestPilot in $ENVIRONMENT mode..."
    export COMPOSE_FILE
    
    # Execute startup sequence
    check_dependencies
    setup_directories
    setup_configuration
    
    # Set compose file for docker-compose commands
    export COMPOSE_FILE
    
    log "Building containers..."
    docker-compose -f "$COMPOSE_FILE" build --parallel
    
    start_infrastructure
    start_applications
    
    echo
    log_success "TestPilot startup complete!"
    echo
    show_status
    
    echo
    echo -e "${GREEN}🎉 TestPilot is now running!${NC}"
    echo -e "${BLUE}💬 Try: 'Test a WiFi amplifier' in the chat interface${NC}"
    echo
    echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
    
    # Keep script running to handle signals
    while true; do
        sleep 10
        
        # Optional: Periodic health checks
        if ! curl -f -s "http://localhost:8001/health" >/dev/null 2>&1; then
            log_warning "AI Orchestrator health check failed"
        fi
    done
}

# Run main function
main "$@"