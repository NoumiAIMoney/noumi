#!/bin/bash
set -e

# Create the main database if it doesn't exist
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Enable required extensions
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    
    -- Create a test user for development
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'noumi_user') THEN
            CREATE ROLE noumi_user WITH LOGIN PASSWORD 'noumi_password';
        END IF;
    END
    \$\$;
    
    -- Grant permissions
    GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO noumi_user;
    GRANT ALL ON SCHEMA public TO noumi_user;
    
    -- Log initialization
    SELECT 'Database initialization completed' as status;
EOSQL

echo "Database initialization script completed successfully"