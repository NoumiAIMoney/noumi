# Noumi Backend

A Go-based backend service for the Noumi financial management application with PostgreSQL database and automated migrations.

## Features

- **Database Migrations**: Automated schema management with golang-migrate
- **Docker Support**: Containerized PostgreSQL for development and testing
- **RESTful API**: Built with Gin framework
- **Health Checks**: Database connectivity and migration status monitoring
- **Comprehensive Testing**: Automated migration testing suite

## Quick Start

### Prerequisites

- Go 1.24.2 or later
- Docker and Docker Compose
- Make (optional, for convenience commands)

### Setup

1. **Clone and navigate to the project:**
   ```bash
   cd noumi-backend
   ```

2. **Start the database:**
   ```bash
   make db-setup
   # or manually:
   docker-compose up -d postgres
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

4. **Run migrations and start the server:**
   ```bash
   make build
   make run
   ```

The server will automatically run database migrations on startup.

## Database Management

### Using Make Commands

```bash
# Database setup
make db-setup          # Start PostgreSQL with Docker
make db-stop           # Stop PostgreSQL
make db-reset          # Reset database (drop and recreate)

# Migration management
make migrate-up        # Run all pending migrations
make migrate-down      # Rollback last migration
make migrate-version   # Show current migration version
make migrate-drop      # Drop all tables (dangerous!)

# Testing
make test-migrations                # Basic migration tests
make test-migrations-comprehensive # Full migration test suite
make test-server-with-migrations   # Test server startup with migrations
```

### Using Migration Tool Directly

```bash
# Build the migration tool
go build -o bin/migrate-tool cmd/migrate/main.go

# Run migrations
DATABASE_URL=postgres://postgres:password@127.0.0.1:5432/noumidb?sslmode=disable ./bin/migrate-tool -action=up

# Check version
DATABASE_URL=postgres://postgres:password@127.0.0.1:5432/noumidb?sslmode=disable ./bin/migrate-tool -action=version

# Rollback
DATABASE_URL=postgres://postgres:password@127.0.0.1:5432/noumidb?sslmode=disable ./bin/migrate-tool -action=down
```

## Docker Services

The `docker-compose.yml` includes:

- **postgres**: Main PostgreSQL database (port 5432)
- **postgres-test**: Test database (port 5433)
- **pgadmin**: Database administration UI (port 8081, optional)

### Starting Services

```bash
# Start main database only
docker-compose up -d postgres

# Start all services including pgAdmin
docker-compose --profile admin up -d

# View logs
docker-compose logs -f postgres

# Stop all services
docker-compose down
```

## Environment Variables

### Database Configuration

```bash
# Primary database connection (takes precedence)
DATABASE_URL=postgres://postgres:password@127.0.0.1:5432/noumidb?sslmode=disable

# Alternative: Individual parameters
DB_HOST=127.0.0.1
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=noumidb
DB_SSL_MODE=disable

# Connection pool settings
DB_MAX_OPEN_CONNS=25
DB_MAX_IDLE_CONNS=5
DB_CONN_MAX_LIFETIME=5m
```

### Server Configuration

```bash
PORT=8080
HOST=0.0.0.0
JWT_SECRET=your-secret-key
LOG_LEVEL=info
LOG_FORMAT=json
```

## API Endpoints

- `GET /health` - Health check with database status
- `GET /api/v1/status` - API status with database and migration info

## Database Schema

The application uses the following main tables:

- **users**: User accounts and profiles
- **goals**: Financial goals set by users
- **plaid_accounts**: Bank accounts connected via Plaid
- **transactions**: Financial transactions from connected accounts
- **anomalies**: Anomaly detection results for transactions
- **weekly_plans**: AI-generated weekly financial plans
- **streak_data**: User streak tracking for various activities

See `internal/database/migrations/001_initial_schema.up.sql` for the complete schema.

## Development

### Building

```bash
# Build server
make build

# Build migration tool
make build-migrate

# Build all binaries
make build-all
```

### Testing

```bash
# Run all tests
make test

# Run tests with coverage
make test-coverage

# Run migration tests
make test-migrations-comprehensive
```

### Code Quality

```bash
# Format code
make fmt

# Run linter
make lint

# Run vet
make vet

# Run all checks
make check
```

## Migration Testing

The project includes comprehensive migration testing:

### Automated Test Suite

```bash
# Run the full migration test suite
./scripts/test-migrations.sh
```

This tests:
1. Initial migration up
2. Table creation verification
3. Index and constraint verification
4. Migration version tracking
5. Migration rollback
6. Table removal verification
7. Re-migration
8. Idempotency
9. Server startup with automatic migrations

### Manual Testing

```bash
# Test basic migration cycle
make test-migrations

# Test full migration cycle with verification
make test-migrations-full

# Test server startup with migrations
make test-server-with-migrations
```

## Troubleshooting

### Database Connection Issues

1. **Check if PostgreSQL is running:**
   ```bash
   docker-compose ps postgres
   ```

2. **Check database logs:**
   ```bash
   docker-compose logs postgres
   ```

3. **Test connection manually:**
   ```bash
   PGPASSWORD=password psql -h 127.0.0.1 -p 5432 -U postgres -d noumidb -c "SELECT 1;"
   ```

### Migration Issues

1. **Check migration status:**
   ```bash
   make migrate-version
   ```

2. **Reset database if needed:**
   ```bash
   make db-reset
   ```

3. **Run health check:**
   ```bash
   ./scripts/health-check.sh
   ```

### Common Issues

- **Port conflicts**: Change ports in `docker-compose.yml` if 5432 is in use
- **Permission issues**: Ensure Docker has proper permissions
- **IPv6 issues**: Use `127.0.0.1` instead of `localhost` in connection strings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make check`
5. Submit a pull request

## License

[Add your license information here]