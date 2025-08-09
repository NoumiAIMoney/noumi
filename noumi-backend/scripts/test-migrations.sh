#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DATABASE_URL="postgres://postgres:password@127.0.0.1:5432/noumidb?sslmode=disable"
TEST_DATABASE_URL="postgres://postgres:password@localhost:5433/noumidb_test?sslmode=disable"
MIGRATE_BINARY="./bin/migrate-tool"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

wait_for_db() {
    local max_attempts=30
    local attempt=1
    
    log_info "Waiting for database to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if PGPASSWORD=password psql -h 127.0.0.1 -p 5432 -U postgres -c "SELECT 1;" >/dev/null 2>&1; then
            log_success "Database is ready!"
            # Ensure noumidb database exists
            PGPASSWORD=password psql -h 127.0.0.1 -p 5432 -U postgres -c "CREATE DATABASE noumidb;" 2>/dev/null || true
            return 0
        fi
        
        log_info "Attempt $attempt/$max_attempts - Database not ready yet..."
        sleep 1
        attempt=$((attempt + 1))
    done
    
    log_error "Database failed to become ready after $max_attempts attempts"
    return 1
}

check_tables_exist() {
    local expected_tables=("users" "goals" "plaid_accounts" "transactions" "anomalies" "weekly_plans" "streak_data")
    
    log_info "Checking if all expected tables exist..."
    
    for table in "${expected_tables[@]}"; do
        if PGPASSWORD=password psql -h 127.0.0.1 -p 5432 -U postgres -d noumidb -t -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '$table');" 2>/dev/null | grep -q "t"; then
            log_success "Table '$table' exists"
        else
            log_error "Table '$table' does not exist"
            return 1
        fi
    done
    
    log_success "All expected tables exist"
    return 0
}

check_indexes_exist() {
    log_info "Checking if indexes exist..."
    
    local index_count=$(PGPASSWORD=password psql -h 127.0.0.1 -p 5432 -U postgres -d noumidb -t -c "SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public';" 2>/dev/null | tr -d ' ')
    
    if [ "$index_count" -gt 10 ]; then
        log_success "Found $index_count indexes (expected > 10)"
    else
        log_error "Found only $index_count indexes (expected > 10)"
        return 1
    fi
    
    return 0
}

check_constraints_exist() {
    log_info "Checking if constraints exist..."
    
    local constraint_count=$(PGPASSWORD=password psql -h 127.0.0.1 -p 5432 -U postgres -d noumidb -t -c "SELECT COUNT(*) FROM information_schema.table_constraints WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')
    
    if [ "$constraint_count" -gt 5 ]; then
        log_success "Found $constraint_count constraints (expected > 5)"
    else
        log_error "Found only $constraint_count constraints (expected > 5)"
        return 1
    fi
    
    return 0
}

test_migration_up() {
    log_info "Testing migration up..."
    
    if DATABASE_URL=$DATABASE_URL $MIGRATE_BINARY -action=up; then
        log_success "Migration up completed successfully"
        return 0
    else
        log_error "Migration up failed"
        return 1
    fi
}

test_migration_down() {
    log_info "Testing migration down..."
    
    if DATABASE_URL=$DATABASE_URL $MIGRATE_BINARY -action=down; then
        log_success "Migration down completed successfully"
        return 0
    else
        log_error "Migration down failed"
        return 1
    fi
}

test_migration_version() {
    log_info "Testing migration version check..."
    
    if DATABASE_URL=$DATABASE_URL $MIGRATE_BINARY -action=version; then
        log_success "Migration version check completed successfully"
        return 0
    else
        log_error "Migration version check failed"
        return 1
    fi
}

cleanup_database() {
    log_info "Cleaning up database..."
    
    if DATABASE_URL=$DATABASE_URL $MIGRATE_BINARY -action=drop 2>/dev/null; then
        log_success "Database cleanup completed"
    else
        log_warning "Database cleanup failed or no tables to drop"
    fi
}

# Main test function
run_migration_tests() {
    log_info "Starting comprehensive migration tests..."
    
    # Build migration binary
    log_info "Building migration binary..."
    if ! go build -o bin/migrate-tool cmd/migrate/main.go; then
        log_error "Failed to build migration binary"
        return 1
    fi
    
    # Start Docker services
    log_info "Starting Docker services..."
    if ! docker-compose up -d postgres postgres-test; then
        log_error "Failed to start Docker services"
        return 1
    fi
    
    # Wait for database
    if ! wait_for_db; then
        log_error "Database failed to start"
        return 1
    fi
    
    # Clean up any existing data
    cleanup_database
    
    # Test 1: Initial migration up
    log_info "=== Test 1: Initial Migration Up ==="
    if ! test_migration_up; then
        return 1
    fi
    
    # Test 2: Check tables exist
    log_info "=== Test 2: Verify Tables Created ==="
    if ! check_tables_exist; then
        return 1
    fi
    
    # Test 3: Check indexes exist
    log_info "=== Test 3: Verify Indexes Created ==="
    if ! check_indexes_exist; then
        return 1
    fi
    
    # Test 4: Check constraints exist
    log_info "=== Test 4: Verify Constraints Created ==="
    if ! check_constraints_exist; then
        return 1
    fi
    
    # Test 5: Check migration version
    log_info "=== Test 5: Check Migration Version ==="
    if ! test_migration_version; then
        return 1
    fi
    
    # Test 6: Migration down (rollback)
    log_info "=== Test 6: Migration Rollback ==="
    if ! test_migration_down; then
        return 1
    fi
    
    # Test 7: Verify tables removed
    log_info "=== Test 7: Verify Tables Removed ==="
    local table_count=$(PGPASSWORD=password psql -h 127.0.0.1 -p 5432 -U postgres -d noumidb -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')
    if [ "$table_count" -eq 1 ]; then  # Only schema_migrations should remain
        log_success "All application tables removed successfully (schema_migrations remains)"
    else
        log_error "Found $table_count tables after rollback (expected 1 - schema_migrations only)"
        return 1
    fi
    
    # Test 8: Migration up again
    log_info "=== Test 8: Migration Up Again ==="
    if ! test_migration_up; then
        return 1
    fi
    
    # Test 9: Verify idempotency (run migration again)
    log_info "=== Test 9: Test Idempotency ==="
    if ! test_migration_up; then
        return 1
    fi
    
    # Test 10: Test server startup with migrations
    log_info "=== Test 10: Server Startup with Migrations ==="
    cleanup_database
    log_info "Building server binary..."
    if ! go build -o bin/noumi-backend cmd/server/main.go; then
        log_error "Failed to build server binary"
        return 1
    fi
    
    log_info "Testing server startup (will run for 5 seconds)..."
    DATABASE_URL=$DATABASE_URL JWT_SECRET=test-secret ./bin/noumi-backend &
    SERVER_PID=$!
    sleep 5
    kill $SERVER_PID 2>/dev/null || true
    wait $SERVER_PID 2>/dev/null || true
    log_success "Server started and ran migrations"
    
    # Verify migrations ran
    if check_tables_exist; then
        log_success "Server migrations test passed"
    else
        log_error "Server migrations test failed"
        return 1
    fi
    
    log_success "All migration tests passed!"
    return 0
}

# Cleanup function
cleanup() {
    log_info "Cleaning up test environment..."
    cleanup_database
    docker-compose down >/dev/null 2>&1 || true
}

# Set up trap for cleanup
trap cleanup EXIT

# Run tests
if run_migration_tests; then
    log_success "🎉 All migration tests completed successfully!"
    exit 0
else
    log_error "❌ Migration tests failed!"
    exit 1
fi