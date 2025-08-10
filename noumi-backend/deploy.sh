#!/bin/bash

# Noumi Backend Deployment Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-development}
COMPOSE_FILE="docker-compose.yml"
PROJECT_NAME="noumi"

echo -e "${BLUE}🚀 Starting Noumi Backend Deployment${NC}"
echo -e "${BLUE}Environment: ${ENVIRONMENT}${NC}"

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

print_status "Docker is running"

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose is not installed. Please install it and try again."
    exit 1
fi

print_status "docker-compose is available"

# Set compose file based on environment
if [ "$ENVIRONMENT" = "production" ]; then
    COMPOSE_FILE="docker-compose.yml -f docker-compose.prod.yml"
    print_warning "Production deployment requires environment variables to be set"
    
    # Check required environment variables for production
    required_vars=("POSTGRES_PASSWORD" "JWT_SECRET" "OPENAI_API_KEY")
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            print_error "Required environment variable $var is not set"
            exit 1
        fi
    done
fi

# Stop existing containers
echo -e "${BLUE}🛑 Stopping existing containers...${NC}"
docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME down --remove-orphans

# Pull latest images
echo -e "${BLUE}📥 Pulling latest images...${NC}"
docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME pull

# Build the application
echo -e "${BLUE}🔨 Building application...${NC}"
docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME build --no-cache

# Start the services
echo -e "${BLUE}🚀 Starting services...${NC}"
if [ "$ENVIRONMENT" = "production" ]; then
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME up -d --scale noumi-backend-2=1
else
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME up -d
fi

# Wait for services to be healthy
echo -e "${BLUE}⏳ Waiting for services to be healthy...${NC}"
sleep 10

# Check service health
check_service_health() {
    local service=$1
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME ps $service | grep -q "healthy"; then
            print_status "$service is healthy"
            return 0
        fi
        
        echo -e "${YELLOW}Waiting for $service to be healthy... (attempt $attempt/$max_attempts)${NC}"
        sleep 5
        ((attempt++))
    done
    
    print_error "$service failed to become healthy"
    return 1
}

# Check database health
check_service_health "postgres"

# Check backend health
check_service_health "noumi-backend-1"

# Check nginx health
check_service_health "nginx"

# Test the deployment
echo -e "${BLUE}🧪 Testing deployment...${NC}"

# Test health endpoint through nginx
if curl -f -s http://localhost/health > /dev/null; then
    print_status "Health endpoint is accessible through nginx"
else
    print_error "Health endpoint is not accessible through nginx"
    exit 1
fi

# Test API endpoint
if curl -f -s http://localhost/api/v1/status > /dev/null; then
    print_status "API status endpoint is accessible"
else
    print_warning "API status endpoint is not accessible (this might be expected if authentication is required)"
fi

# Test Swagger documentation
if curl -f -s http://localhost/docs/ > /dev/null; then
    print_status "Swagger documentation is accessible"
else
    print_warning "Swagger documentation is not accessible"
fi

# Show running containers
echo -e "${BLUE}📋 Running containers:${NC}"
docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME ps

# Show logs for the last few minutes
echo -e "${BLUE}📝 Recent logs:${NC}"
docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME logs --tail=20

print_status "Deployment completed successfully!"
echo -e "${GREEN}🎉 Noumi Backend is now running!${NC}"
echo -e "${BLUE}📍 Access points:${NC}"
echo -e "   • API: http://localhost/api/v1/"
echo -e "   • Health: http://localhost/health"
echo -e "   • Swagger: http://localhost/docs/"
echo -e "   • Nginx Health: http://localhost:8081/nginx-health"

if [ "$ENVIRONMENT" = "development" ]; then
    echo -e "   • pgAdmin: http://localhost:8082 (admin@noumi.com / admin)"
fi

echo -e "${BLUE}🔧 Management commands:${NC}"
echo -e "   • View logs: docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME logs -f"
echo -e "   • Stop services: docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME down"
echo -e "   • Restart services: docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME restart"