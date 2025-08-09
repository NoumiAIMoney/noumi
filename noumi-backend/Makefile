# Makefile for Noumi Backend

# Variables
BINARY_NAME=noumi-backend
MIGRATE_BINARY=migrate-tool
DOCKER_IMAGE=noumi-backend
GO_VERSION=1.24.2

# Default target
.PHONY: help
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Build targets
.PHONY: build
build: ## Build the main server binary
	@echo "Building server binary..."
	go build -o bin/$(BINARY_NAME) cmd/server/main.go

.PHONY: build-migrate
build-migrate: ## Build the migration tool binary
	@echo "Building migration tool binary..."
	go build -o bin/$(MIGRATE_BINARY) cmd/migrate/main.go

.PHONY: build-all
build-all: build build-migrate ## Build all binaries

# Development targets
.PHONY: run
run: ## Run the server in development mode
	@echo "Starting server in development mode..."
	go run cmd/server/main.go

.PHONY: dev
dev: ## Run the server with hot reload (requires air)
	@echo "Starting server with hot reload..."
	air -c .air.toml

# Database migration targets
.PHONY: migrate-up
migrate-up: build-migrate ## Run all pending migrations
	@echo "Running migrations up..."
	./bin/$(MIGRATE_BINARY) -action=up

.PHONY: migrate-down
migrate-down: build-migrate ## Rollback the last migration
	@echo "Rolling back last migration..."
	./bin/$(MIGRATE_BINARY) -action=down

.PHONY: migrate-version
migrate-version: build-migrate ## Show current migration version
	@echo "Getting current migration version..."
	./bin/$(MIGRATE_BINARY) -action=version

.PHONY: migrate-drop
migrate-drop: build-migrate ## Drop all tables (dangerous!)
	@echo "Dropping all tables..."
	./bin/$(MIGRATE_BINARY) -action=drop

# Testing targets
.PHONY: test
test: ## Run all tests
	@echo "Running tests..."
	go test -v ./...

.PHONY: test-coverage
test-coverage: ## Run tests with coverage
	@echo "Running tests with coverage..."
	go test -v -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out -o coverage.html

.PHONY: test-race
test-race: ## Run tests with race detection
	@echo "Running tests with race detection..."
	go test -v -race ./...

# Code quality targets
.PHONY: fmt
fmt: ## Format Go code
	@echo "Formatting code..."
	go fmt ./...

.PHONY: vet
vet: ## Run go vet
	@echo "Running go vet..."
	go vet ./...

.PHONY: lint
lint: ## Run golangci-lint (requires golangci-lint to be installed)
	@echo "Running linter..."
	golangci-lint run

.PHONY: tidy
tidy: ## Tidy go modules
	@echo "Tidying go modules..."
	go mod tidy

# Docker targets
.PHONY: docker-build
docker-build: ## Build Docker image
	@echo "Building Docker image..."
	docker build -t $(DOCKER_IMAGE):latest .

.PHONY: docker-run
docker-run: ## Run Docker container
	@echo "Running Docker container..."
	docker run -p 8080:8080 --env-file .env $(DOCKER_IMAGE):latest

# Clean targets
.PHONY: clean
clean: ## Clean build artifacts
	@echo "Cleaning build artifacts..."
	rm -rf bin/
	rm -f coverage.out coverage.html

.PHONY: clean-all
clean-all: clean ## Clean all artifacts including Docker images
	@echo "Cleaning Docker images..."
	docker rmi $(DOCKER_IMAGE):latest 2>/dev/null || true

# Setup targets
.PHONY: setup
setup: ## Setup development environment
	@echo "Setting up development environment..."
	go mod download
	go install github.com/air-verse/air@latest
	go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

.PHONY: deps
deps: ## Download dependencies
	@echo "Downloading dependencies..."
	go mod download

# Database setup for development
.PHONY: db-setup
db-setup: ## Setup local PostgreSQL database (requires Docker)
	@echo "Setting up local PostgreSQL database..."
	docker run --name noumi-postgres -e POSTGRES_DB=noumidb -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15-alpine

.PHONY: db-stop
db-stop: ## Stop local PostgreSQL database
	@echo "Stopping local PostgreSQL database..."
	docker stop noumi-postgres || true
	docker rm noumi-postgres || true

# All-in-one targets
.PHONY: check
check: fmt vet test ## Run all checks (format, vet, test)

.PHONY: ci
ci: tidy fmt vet test-race ## Run CI pipeline locally

.PHONY: install
install: build ## Install binaries to $GOPATH/bin
	@echo "Installing binaries..."
	go install cmd/server/main.go
	go install cmd/migrate/main.go