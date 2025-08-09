#!/bin/bash
set -e

# Health check script for the application
# This script checks if the database is ready and migrations have been applied

DATABASE_URL=${DATABASE_URL:-"postgres://postgres:password@localhost:5432/noumidb?sslmode=disable"}

# Check if database is reachable
echo "Checking database connectivity..."
if ! timeout 5 bash -c "until pg_isready -d $DATABASE_URL; do sleep 1; done"; then
    echo "❌ Database is not reachable"
    exit 1
fi

echo "✅ Database is reachable"

# Check if migrations have been applied by looking for the schema_migrations table
echo "Checking if migrations have been applied..."
if psql "$DATABASE_URL" -t -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'schema_migrations');" | grep -q "t"; then
    echo "✅ Migrations table exists"
    
    # Get current migration version
    VERSION=$(psql "$DATABASE_URL" -t -c "SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 1;" | tr -d ' ')
    if [ -n "$VERSION" ]; then
        echo "✅ Current migration version: $VERSION"
    else
        echo "⚠️  No migrations applied yet"
    fi
else
    echo "⚠️  Migrations table does not exist - no migrations applied"
fi

# Check if core tables exist
echo "Checking core application tables..."
CORE_TABLES=("users" "goals" "transactions" "plaid_accounts")
MISSING_TABLES=()

for table in "${CORE_TABLES[@]}"; do
    if psql "$DATABASE_URL" -t -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '$table');" | grep -q "t"; then
        echo "✅ Table '$table' exists"
    else
        echo "❌ Table '$table' is missing"
        MISSING_TABLES+=("$table")
    fi
done

if [ ${#MISSING_TABLES[@]} -eq 0 ]; then
    echo "✅ All core tables exist"
    echo "🎉 Health check passed!"
    exit 0
else
    echo "❌ Missing tables: ${MISSING_TABLES[*]}"
    echo "💡 Run migrations to create missing tables"
    exit 1
fi