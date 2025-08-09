# Database Migrations

This directory contains database migration files for the Noumi backend application.

## Migration Files

Migration files follow the naming convention: `{version}_{description}.{up|down}.sql`

- `version`: Sequential number (e.g., 001, 002, 003)
- `description`: Brief description of the migration (e.g., initial_schema, add_user_preferences)
- `up`: SQL commands to apply the migration
- `down`: SQL commands to rollback the migration

## Current Migrations

### 001_initial_schema

Creates the initial database schema with the following tables:

- **users**: User accounts and profile information
- **goals**: Financial goals set by users
- **plaid_accounts**: Bank accounts connected via Plaid
- **transactions**: Financial transactions from connected accounts
- **anomalies**: Anomaly detection results for transactions
- **weekly_plans**: AI-generated weekly financial plans
- **streak_data**: User streak tracking for various activities

The migration also includes:
- Proper indexes for performance optimization
- Foreign key constraints for data integrity
- Check constraints for data validation
- Views for common queries
- Triggers for automatic timestamp updates
- Comments for documentation

## Running Migrations

### Using the Migration Tool

Build and run the migration tool:

```bash
# Build the migration tool
go build -o bin/migrate cmd/migrate/main.go

# Run all pending migrations
./bin/migrate -action=up

# Rollback the last migration
./bin/migrate -action=down

# Check current migration version
./bin/migrate -action=version

# Migrate to a specific version
./bin/migrate -action=up -version=1

# Drop all tables (dangerous!)
./bin/migrate -action=drop
```

### Using Make Commands

```bash
# Run all pending migrations
make migrate-up

# Rollback the last migration
make migrate-down

# Check current migration version
make migrate-version

# Drop all tables (dangerous!)
make migrate-drop
```

### Automatic Migration on Server Start

The server automatically runs pending migrations on startup. This ensures the database schema is always up-to-date when the application starts.

## Environment Variables

The migration system uses the following environment variables:

- `DATABASE_URL`: PostgreSQL connection string (e.g., `postgres://user:password@localhost/dbname?sslmode=disable`)
- `DB_HOST`: Database host (default: localhost)
- `DB_PORT`: Database port (default: 5432)
- `DB_USER`: Database user (default: postgres)
- `DB_PASSWORD`: Database password
- `DB_NAME`: Database name (default: noumidb)
- `DB_SSL_MODE`: SSL mode (default: disable)

## Creating New Migrations

To create a new migration:

1. Create two files in this directory:
   - `{next_version}_{description}.up.sql` - Contains the SQL to apply the migration
   - `{next_version}_{description}.down.sql` - Contains the SQL to rollback the migration

2. Example for migration 002:
   ```sql
   -- 002_add_user_preferences.up.sql
   ALTER TABLE users ADD COLUMN preferences JSONB DEFAULT '{}';
   CREATE INDEX idx_users_preferences ON users USING GIN (preferences);
   ```

   ```sql
   -- 002_add_user_preferences.down.sql
   DROP INDEX IF EXISTS idx_users_preferences;
   ALTER TABLE users DROP COLUMN IF EXISTS preferences;
   ```

3. Test the migration:
   ```bash
   # Apply the migration
   ./bin/migrate -action=up
   
   # Verify it worked
   ./bin/migrate -action=version
   
   # Test rollback
   ./bin/migrate -action=down
   
   # Apply again
   ./bin/migrate -action=up
   ```

## Best Practices

1. **Always create both up and down migrations**: This allows for easy rollbacks
2. **Test migrations thoroughly**: Test both applying and rolling back migrations
3. **Use transactions when possible**: Wrap related changes in transactions
4. **Add indexes for performance**: Consider query patterns when adding indexes
5. **Use constraints for data integrity**: Add appropriate constraints to maintain data quality
6. **Document complex migrations**: Add comments explaining complex logic
7. **Backup before major migrations**: Always backup production data before running migrations

## Troubleshooting

### Dirty Migration State

If a migration fails and leaves the database in a "dirty" state:

1. Check the current version and dirty status:
   ```bash
   ./bin/migrate -action=version
   ```

2. If dirty, you may need to manually fix the database and force the version:
   ```bash
   # This functionality needs to be implemented in the migrator
   ./bin/migrate -action=force -version=1
   ```

### Migration Conflicts

If multiple developers create migrations with the same version number:

1. Rename one of the migrations to the next available version
2. Update any references to the migration
3. Coordinate with your team to avoid future conflicts

### Performance Issues

If migrations are slow:

1. Consider breaking large migrations into smaller chunks
2. Add appropriate indexes before inserting large amounts of data
3. Use `COPY` instead of `INSERT` for bulk data operations
4. Consider running migrations during maintenance windows for production

## Database Schema Documentation

The current schema supports:

- **User Management**: User accounts, authentication, and profiles
- **Financial Goals**: Goal setting and tracking
- **Bank Integration**: Plaid-based bank account connections
- **Transaction Processing**: Financial transaction storage and analysis
- **Anomaly Detection**: ML-based anomaly detection and scoring
- **AI Planning**: LLM-generated weekly financial plans
- **Streak Tracking**: Habit and achievement tracking

For detailed schema information, see the migration files and database model definitions.