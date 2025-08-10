# SQLite to PostgreSQL Migration Tool

This tool migrates data from the existing SQLite database to PostgreSQL format, ensuring data integrity and compatibility with the new Go backend.

## Overview

The migration tool handles the complete transformation of data from SQLite to PostgreSQL, including:

- **Schema Transformation**: Converts SQLite schema to PostgreSQL format
- **Data Type Conversion**: Handles differences between SQLite and PostgreSQL data types
- **Foreign Key Mapping**: Maintains referential integrity during migration
- **Batch Processing**: Processes large datasets efficiently
- **Data Validation**: Ensures data integrity after migration
- **Rollback Support**: Provides transaction-based rollback capabilities

## Features

### Core Migration Features
- ✅ **Users**: Migrates user accounts with profile information
- ✅ **Goals**: Converts user goals with proper date handling
- ✅ **Transactions**: Migrates financial transactions with category mapping
- ✅ **Plaid Connections**: Transforms Plaid account data
- ✅ **Weekly Plans**: Migrates AI-generated weekly plans

### Data Integrity Features
- ✅ **Foreign Key Preservation**: Maintains relationships between tables
- ✅ **Data Type Conversion**: Handles SQLite TEXT to PostgreSQL proper types
- ✅ **Date/Time Parsing**: Converts various date formats to PostgreSQL timestamps
- ✅ **JSON Handling**: Preserves JSON data structures
- ✅ **Batch Processing**: Efficient processing of large datasets

### Validation Features
- ✅ **Schema Validation**: Verifies target schema exists
- ✅ **Record Count Validation**: Ensures all records are migrated
- ✅ **Data Integrity Checks**: Validates foreign key relationships
- ✅ **Sample Data Verification**: Spot-checks migrated data accuracy

## Quick Start

### Prerequisites

1. **Go 1.21+** with CGO enabled (for SQLite support)
2. **PostgreSQL 15+** running and accessible
3. **SQLite database** file with existing data

### Basic Migration

```bash
# Using the migration script
./scripts/run-migration.sh \
  --sqlite-path ./Back_End/Middleware/noumi.db \
  --postgres-url "postgres://user:password@localhost:5432/noumidb"

# Using Make
make migrate DATABASE_URL="postgres://user:password@localhost:5432/noumidb"

# Using Docker
make docker-migrate
```

### Dry Run (Test Migration)

```bash
# Test migration without making changes
./scripts/run-migration.sh --dry-run

# Using Make
make migrate-dry

# Using Docker
make docker-migrate-dry
```

## Installation

### Option 1: Direct Build

```bash
# Clone and build
cd noumi-backend
go mod download
make build

# Run migration
./bin/migrate-sqlite --help
```

### Option 2: Docker Build

```bash
# Build Docker image
docker build -f Dockerfile.migration -t noumi-migration .

# Run migration
docker run --rm \
  -v /path/to/sqlite:/data \
  -e DATABASE_URL="postgres://user:pass@host:5432/db" \
  noumi-migration
```

### Option 3: Docker Compose

```bash
# Start PostgreSQL and run migration
docker-compose -f docker-compose.migration.yml up --build
```

## Usage

### Command Line Options

```bash
migrate-sqlite [options]

Options:
  --sqlite-path PATH     Path to SQLite database file
  --postgres-url URL     PostgreSQL connection URL
  --dry-run              Perform a dry run without writing to PostgreSQL
  --validate-only        Only validate schemas, don't migrate data
  --batch-size SIZE      Number of records to process in each batch (default: 100)
  --help                 Show help message

Environment Variables:
  SQLITE_PATH           SQLite database file path
  DATABASE_URL          PostgreSQL connection URL
```

### Migration Workflow

1. **Schema Validation**: Verifies both databases are accessible and have required tables
2. **Data Migration**: Migrates data in dependency order (users → goals → accounts → transactions)
3. **Data Validation**: Verifies record counts and data integrity
4. **Report Generation**: Creates detailed migration report

### Examples

#### Basic Migration
```bash
./bin/migrate-sqlite \
  --sqlite-path ./noumi.db \
  --postgres-url "postgres://user:password@localhost:5432/noumidb"
```

#### Dry Run with Custom Batch Size
```bash
./bin/migrate-sqlite \
  --sqlite-path ./noumi.db \
  --postgres-url "postgres://user:password@localhost:5432/noumidb" \
  --dry-run \
  --batch-size 50
```

#### Schema Validation Only
```bash
./bin/migrate-sqlite \
  --sqlite-path ./noumi.db \
  --postgres-url "postgres://user:password@localhost:5432/noumidb" \
  --validate-only
```

## Data Mapping

### Users Table
| SQLite Field | PostgreSQL Field | Transformation |
|--------------|------------------|----------------|
| `id` (TEXT) | `user_id` (INTEGER) | Hash-based conversion |
| `email` | `email` | Direct copy |
| `name` | `name` | Direct copy |
| `created_at` (TEXT) | `created_at` (TIMESTAMP) | Date parsing |
| `preferences` (TEXT) | `financial_goal`, `impulse_triggers` | JSON extraction |

### Goals Table (user_goals → goals)
| SQLite Field | PostgreSQL Field | Transformation |
|--------------|------------------|----------------|
| `user_id` (TEXT) | `user_id` (INTEGER) | Hash-based conversion |
| `goal_name` | `goal_name` | Direct copy |
| `goal_description` | `goal_description` | Direct copy |
| `goal_amount` | `goal_amount` | Direct copy |
| `target_date` (TEXT) | `target_date` (DATE) | Date parsing |
| `net_monthly_income` | `net_monthly_income` | Direct copy |

### Transactions Table
| SQLite Field | PostgreSQL Field | Transformation |
|--------------|------------------|----------------|
| `transaction_id` | `transaction_id` | Direct copy |
| `user_id` (TEXT) | `user_id` (INTEGER) | Hash-based conversion |
| `account_id` | `account_id` | Direct copy |
| `amount` | `amount` | Direct copy |
| `date` (TEXT) | `date` (DATE) | Date parsing |
| `merchant_name` | `merchant_name` | Direct copy |
| `category` | `category` | Direct copy |
| `description` | N/A | Not migrated |

### Plaid Connections (plaid_connections → plaid_accounts)
| SQLite Field | PostgreSQL Field | Transformation |
|--------------|------------------|----------------|
| `user_id` (TEXT) | `user_id` (INTEGER) | Hash-based conversion |
| `access_token` | `plaid_token` (in users) | Moved to users table |
| `accounts` (JSON) | Multiple `plaid_accounts` rows | JSON parsing |

## Validation

### Automated Validation

The migration tool includes comprehensive validation:

```bash
# Run validation script
./scripts/validate-migration.sh

# Validation checks:
# - Record count matching
# - Foreign key integrity
# - Data type correctness
# - Sample data verification
```

### Manual Validation Queries

```sql
-- Check record counts
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'goals', COUNT(*) FROM goals
UNION ALL
SELECT 'transactions', COUNT(*) FROM transactions;

-- Check for orphaned records
SELECT COUNT(*) as orphaned_goals 
FROM goals g 
LEFT JOIN users u ON g.user_id = u.user_id 
WHERE u.user_id IS NULL;

-- Verify data integrity
SELECT 
    u.user_id,
    u.name,
    COUNT(g.goal_id) as goals,
    COUNT(t.transaction_id) as transactions
FROM users u
LEFT JOIN goals g ON u.user_id = g.user_id
LEFT JOIN transactions t ON u.user_id = t.user_id
GROUP BY u.user_id, u.name;
```

## Troubleshooting

### Common Issues

#### 1. SQLite Database Not Found
```
Error: SQLite database not found at: ./noumi.db
```
**Solution**: Verify the SQLite file path and ensure the file exists.

#### 2. PostgreSQL Connection Failed
```
Error: Cannot connect to PostgreSQL database
```
**Solution**: Check PostgreSQL URL, ensure database is running, and verify credentials.

#### 3. Schema Validation Failed
```
Error: PostgreSQL table 'users' does not exist
```
**Solution**: Run database migrations first to create the PostgreSQL schema.

#### 4. Foreign Key Constraint Violations
```
Error: Failed to insert goal: foreign key constraint violation
```
**Solution**: Ensure users are migrated before goals. The tool handles this automatically.

### Debug Mode

Enable verbose logging:

```bash
# Set log level for detailed output
export LOG_LEVEL=debug
./bin/migrate-sqlite --sqlite-path ./noumi.db --postgres-url "..."
```

### Recovery

If migration fails partway through:

1. **Check the error logs** for specific failure reasons
2. **Use dry run mode** to test fixes without making changes
3. **Rollback transaction** (automatic for most failures)
4. **Fix underlying issues** and retry migration

## Performance

### Optimization Tips

1. **Batch Size**: Adjust `--batch-size` based on available memory
   - Small datasets: 100-500 records
   - Large datasets: 1000-5000 records

2. **Database Tuning**: Temporarily adjust PostgreSQL settings
   ```sql
   -- Increase work memory for migration
   SET work_mem = '256MB';
   SET maintenance_work_mem = '1GB';
   ```

3. **Connection Pooling**: Use connection pooling for large migrations
   ```bash
   # Increase max connections if needed
   --postgres-url "postgres://user:pass@host:5432/db?pool_max_conns=10"
   ```

### Performance Benchmarks

| Dataset Size | Migration Time | Memory Usage |
|--------------|----------------|--------------|
| 1K records | ~30 seconds | ~50MB |
| 10K records | ~2 minutes | ~100MB |
| 100K records | ~15 minutes | ~200MB |

## Security

### Data Protection

1. **Connection Security**: Use SSL connections for PostgreSQL
   ```bash
   --postgres-url "postgres://user:pass@host:5432/db?sslmode=require"
   ```

2. **Credential Management**: Use environment variables
   ```bash
   export DATABASE_URL="postgres://..."
   ./bin/migrate-sqlite --sqlite-path ./noumi.db
   ```

3. **Access Control**: Ensure migration user has minimal required permissions
   ```sql
   -- Create migration user with limited permissions
   CREATE USER migration_user WITH PASSWORD 'secure_password';
   GRANT INSERT, UPDATE, SELECT ON ALL TABLES IN SCHEMA public TO migration_user;
   ```

## Development

### Building from Source

```bash
# Install dependencies
go mod download

# Build with CGO for SQLite support
CGO_ENABLED=1 go build -o bin/migrate-sqlite ./cmd/migrate-sqlite

# Run tests
go test ./cmd/migrate-sqlite/...
```

### Adding New Migrations

1. **Update the migration tool** to handle new tables
2. **Add validation logic** for new data types
3. **Update the schema mapping** documentation
4. **Test with sample data**

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

## Support

### Getting Help

1. **Check the logs** for detailed error messages
2. **Run validation** to identify specific issues
3. **Use dry run mode** to test changes safely
4. **Review the troubleshooting section** for common solutions

### Reporting Issues

When reporting issues, include:

- Migration command used
- Error messages and logs
- SQLite database schema (`sqlite3 db.sqlite ".schema"`)
- PostgreSQL version and configuration
- Sample data (anonymized)

## License

This migration tool is part of the Noumi backend project and follows the same license terms.