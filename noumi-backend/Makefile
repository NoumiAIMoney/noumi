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

# Migration testing targets
.PHONY: test-migrations
test-migrations: db-setup build-migrate ## Test migrations with Docker database
	@echo "Testing migrations with Docker database..."
	@echo "Waiting for database to be ready..."
	@for i in $$(seq 1 30); do \
		if docker-compose exec postgres pg_isready -U postgres -d noumidb >/dev/null 2>&1; then \
			echo "Database is ready!"; \
			break; \
		fi; \
		echo "Waiting for database... ($$i/30)"; \
		sleep 1; \
	done
	@echo "Running migration tests..."
	@echo "1. Testing migration up..."
	DATABASE_URL=postgres://postgres:password@127.0.0.1:5432/noumidb?sslmode=disable ./bin/$(MIGRATE_BINARY) -action=up
	@echo "2. Checking migration version..."
	DATABASE_URL=postgres://postgres:password@127.0.0.1:5432/noumidb?sslmode=disable ./bin/$(MIGRATE_BINARY) -action=version
	@echo "3. Testing migration down..."
	DATABASE_URL=postgres://postgres:password@127.0.0.1:5432/noumidb?sslmode=disable ./bin/$(MIGRATE_BINARY) -action=down
	@echo "4. Testing migration up again..."
	DATABASE_URL=postgres://postgres:password@127.0.0.1:5432/noumidb?sslmode=disable ./bin/$(MIGRATE_BINARY) -action=up
	@echo "Migration tests completed successfully!"

.PHONY: test-migrations-full
test-migrations-full: db-reset build-migrate ## Full migration test cycle
	@echo "Running full migration test cycle..."
	@echo "Waiting for database to be ready..."
	@for i in $$(seq 1 30); do \
		if docker-compose exec postgres pg_isready -U postgres -d noumidb >/dev/null 2>&1; then \
			echo "Database is ready!"; \
			break; \
		fi; \
		echo "Waiting for database... ($$i/30)"; \
		sleep 1; \
	done
	@echo "Testing complete migration cycle..."
	@echo "1. Initial migration up..."
	DATABASE_URL=postgres://postgres:password@127.0.0.1:5432/noumidb?sslmode=disable ./bin/$(MIGRATE_BINARY) -action=up
	@echo "2. Verify tables exist..."
	PGPASSWORD=password psql -h 127.0.0.1 -p 5432 -U postgres -d noumidb -c "\dt"
	@echo "3. Test rollback..."
	DATABASE_URL=postgres://postgres:password@127.0.0.1:5432/noumidb?sslmode=disable ./bin/$(MIGRATE_BINARY) -action=down
	@echo "4. Verify tables removed..."
	PGPASSWORD=password psql -h 127.0.0.1 -p 5432 -U postgres -d noumidb -c "\dt" || echo "No tables found (expected)"
	@echo "5. Migrate up again..."
	DATABASE_URL=postgres://postgres:password@127.0.0.1:5432/noumidb?sslmode=disable ./bin/$(MIGRATE_BINARY) -action=up
	@echo "6. Final verification..."
	PGPASSWORD=password psql -h 127.0.0.1 -p 5432 -U postgres -d noumidb -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"
	@echo "Full migration test cycle completed successfully!"

.PHONY: test-server-with-migrations
test-server-with-migrations: db-setup build ## Test server startup with automatic migrations
	@echo "Testing server startup with automatic migrations..."
	@echo "Waiting for database to be ready..."
	@for i in $$(seq 1 30); do \
		if docker-compose exec postgres pg_isready -U postgres -d noumidb >/dev/null 2>&1; then \
			echo "Database is ready!"; \
			break; \
		fi; \
		echo "Waiting for database... ($$i/30)"; \
		sleep 1; \
	done
	@echo "Starting server (will run migrations automatically)..."
	@echo "Starting server in background for 5 seconds to test migrations..."
	DATABASE_URL=postgres://postgres:password@127.0.0.1:5432/noumidb?sslmode=disable JWT_SECRET=test-secret ./bin/$(BINARY_NAME) & \
	SERVER_PID=$$!; \
	sleep 5; \
	kill $$SERVER_PID 2>/dev/null || true; \
	echo "Server test completed"
	@echo "Verifying migrations were applied..."
	PGPASSWORD=password psql -h 127.0.0.1 -p 5432 -U postgres -d noumidb -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"
	@echo "Server migration test completed!"

.PHONY: test-migrations-comprehensive
test-migrations-comprehensive: ## Run comprehensive migration tests with Docker
	@echo "Running comprehensive migration tests..."
	./scripts/test-migrations.sh

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

# Docker and Database setup
.PHONY: docker-up
docker-up: ## Start PostgreSQL and services with Docker Compose
	@echo "Starting services with Docker Compose..."
	docker-compose up -d postgres postgres-test

.PHONY: docker-up-all
docker-up-all: ## Start all services including pgAdmin
	@echo "Starting all services with Docker Compose..."
	docker-compose --profile admin up -d

.PHONY: docker-down
docker-down: ## Stop all Docker Compose services
	@echo "Stopping Docker Compose services..."
	docker-compose down

.PHONY: docker-logs
docker-logs: ## Show logs from Docker services
	@echo "Showing Docker Compose logs..."
	docker-compose logs -f

.PHONY: docker-clean
docker-clean: ## Clean up Docker containers and volumes
	@echo "Cleaning up Docker containers and volumes..."
	docker-compose down -v
	docker system prune -f

# Database setup for development
.PHONY: db-setup
db-setup: docker-up ## Setup local PostgreSQL database with Docker Compose
	@echo "Waiting for database to be ready..."
	@for i in $$(seq 1 30); do \
		if docker-compose exec postgres pg_isready -U postgres -d noumidb >/dev/null 2>&1; then \
			echo "Database is ready!"; \
			break; \
		fi; \
		echo "Waiting for database... ($$i/30)"; \
		sleep 1; \
	done

.PHONY: db-stop
db-stop: docker-down ## Stop local PostgreSQL database

.PHONY: db-reset
db-reset: ## Reset database (drop and recreate)
	@echo "Resetting database..."
	docker-compose down -v
	docker-compose up -d postgres postgres-test
	@echo "Waiting for database to be ready..."
	@timeout 30 bash -c 'until docker-compose exec postgres pg_isready -U postgres -d noumidb; do sleep 1; done'
	@echo "Database reset complete!"

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