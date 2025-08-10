#!/bin/bash

# Migration validation script
# This script validates the SQLite to PostgreSQL migration by comparing data integrity

set -e

# Configuration
SQLITE_PATH="${SQLITE_PATH:-./Back_End/Middleware/noumi.db}"
POSTGRES_URL="${DATABASE_URL:-postgres://user:password@localhost:5432/noumidb}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are available
check_dependencies() {
    log_info "Checking dependencies..."
    
    if ! command -v sqlite3 &> /dev/null; then
        log_error "sqlite3 is required but not installed"
        exit 1
    fi
    
    if ! command -v psql &> /dev/null; then
        log_error "psql is required but not installed"
        exit 1
    fi
    
    log_info "Dependencies check passed"
}

# Check if databases are accessible
check_database_connectivity() {
    log_info "Checking database connectivity..."
    
    # Check SQLite
    if [ ! -f "$SQLITE_PATH" ]; then
        log_error "SQLite database not found at: $SQLITE_PATH"
        exit 1
    fi
    
    if ! sqlite3 "$SQLITE_PATH" "SELECT 1;" &> /dev/null; then
        log_error "Cannot connect to SQLite database"
        exit 1
    fi
    
    # Check PostgreSQL
    if ! psql "$POSTGRES_URL" -c "SELECT 1;" &> /dev/null; then
        log_error "Cannot connect to PostgreSQL database"
        exit 1
    fi
    
    log_info "Database connectivity check passed"
}

# Validate table counts
validate_table_counts() {
    log_info "Validating table counts..."
    
    # Users
    sqlite_users=$(sqlite3 "$SQLITE_PATH" "SELECT COUNT(*) FROM users;")
    postgres_users=$(psql "$POSTGRES_URL" -t -c "SELECT COUNT(*) FROM users;" | tr -d ' ')
    
    if [ "$sqlite_users" != "$postgres_users" ]; then
        log_error "User count mismatch: SQLite=$sqlite_users, PostgreSQL=$postgres_users"
        return 1
    fi
    log_info "Users: $postgres_users records ✓"
    
    # Goals
    sqlite_goals=$(sqlite3 "$SQLITE_PATH" "SELECT COUNT(*) FROM user_goals;")
    postgres_goals=$(psql "$POSTGRES_URL" -t -c "SELECT COUNT(*) FROM goals;" | tr -d ' ')
    
    if [ "$sqlite_goals" != "$postgres_goals" ]; then
        log_error "Goal count mismatch: SQLite=$sqlite_goals, PostgreSQL=$postgres_goals"
        return 1
    fi
    log_info "Goals: $postgres_goals records ✓"
    
    # Transactions
    sqlite_transactions=$(sqlite3 "$SQLITE_PATH" "SELECT COUNT(*) FROM transactions;")
    postgres_transactions=$(psql "$POSTGRES_URL" -t -c "SELECT COUNT(*) FROM transactions;" | tr -d ' ')
    
    if [ "$sqlite_transactions" != "$postgres_transactions" ]; then
        log_error "Transaction count mismatch: SQLite=$sqlite_transactions, PostgreSQL=$postgres_transactions"
        return 1
    fi
    log_info "Transactions: $postgres_transactions records ✓"
    
    # Plaid connections
    sqlite_plaid=$(sqlite3 "$SQLITE_PATH" "SELECT COUNT(*) FROM plaid_connections;")
    postgres_plaid=$(psql "$POSTGRES_URL" -t -c "SELECT COUNT(*) FROM plaid_accounts;" | tr -d ' ')
    
    # Note: Plaid connections might create multiple plaid_accounts, so we check if PostgreSQL has at least as many
    if [ "$postgres_plaid" -lt "$sqlite_plaid" ]; then
        log_error "Plaid account count too low: SQLite connections=$sqlite_plaid, PostgreSQL accounts=$postgres_plaid"
        return 1
    fi
    log_info "Plaid accounts: $postgres_plaid records (from $sqlite_plaid connections) ✓"
    
    # Weekly plans
    sqlite_plans=$(sqlite3 "$SQLITE_PATH" "SELECT COUNT(*) FROM weekly_plans;")
    postgres_plans=$(psql "$POSTGRES_URL" -t -c "SELECT COUNT(*) FROM weekly_plans;" | tr -d ' ')
    
    if [ "$sqlite_plans" != "$postgres_plans" ]; then
        log_error "Weekly plan count mismatch: SQLite=$sqlite_plans, PostgreSQL=$postgres_plans"
        return 1
    fi
    log_info "Weekly plans: $postgres_plans records ✓"
    
    log_info "Table count validation passed"
}

# Validate data integrity
validate_data_integrity() {
    log_info "Validating data integrity..."
    
    # Check for orphaned records
    orphaned_goals=$(psql "$POSTGRES_URL" -t -c "
        SELECT COUNT(*) FROM goals g 
        LEFT JOIN users u ON g.user_id = u.user_id 
        WHERE u.user_id IS NULL;
    " | tr -d ' ')
    
    if [ "$orphaned_goals" != "0" ]; then
        log_error "Found $orphaned_goals orphaned goals"
        return 1
    fi
    
    orphaned_transactions=$(psql "$POSTGRES_URL" -t -c "
        SELECT COUNT(*) FROM transactions t 
        LEFT JOIN users u ON t.user_id = u.user_id 
        WHERE u.user_id IS NULL;
    " | tr -d ' ')
    
    if [ "$orphaned_transactions" != "0" ]; then
        log_error "Found $orphaned_transactions orphaned transactions"
        return 1
    fi
    
    orphaned_plaid=$(psql "$POSTGRES_URL" -t -c "
        SELECT COUNT(*) FROM plaid_accounts p 
        LEFT JOIN users u ON p.user_id = u.user_id 
        WHERE u.user_id IS NULL;
    " | tr -d ' ')
    
    if [ "$orphaned_plaid" != "0" ]; then
        log_error "Found $orphaned_plaid orphaned plaid accounts"
        return 1
    fi
    
    # Check for invalid dates
    invalid_dates=$(psql "$POSTGRES_URL" -t -c "
        SELECT COUNT(*) FROM goals 
        WHERE target_date < created_at::date;
    " | tr -d ' ')
    
    if [ "$invalid_dates" != "0" ]; then
        log_warn "Found $invalid_dates goals with target_date before created_at"
    fi
    
    # Check for negative goal amounts
    negative_goals=$(psql "$POSTGRES_URL" -t -c "
        SELECT COUNT(*) FROM goals 
        WHERE goal_amount <= 0;
    " | tr -d ' ')
    
    if [ "$negative_goals" != "0" ]; then
        log_error "Found $negative_goals goals with non-positive amounts"
        return 1
    fi
    
    log_info "Data integrity validation passed"
}

# Validate sample data consistency
validate_sample_data() {
    log_info "Validating sample data consistency..."
    
    # Get a sample user from SQLite and verify in PostgreSQL
    sample_user_email=$(sqlite3 "$SQLITE_PATH" "SELECT email FROM users LIMIT 1;")
    
    if [ -n "$sample_user_email" ]; then
        postgres_user_exists=$(psql "$POSTGRES_URL" -t -c "
            SELECT COUNT(*) FROM users WHERE email = '$sample_user_email';
        " | tr -d ' ')
        
        if [ "$postgres_user_exists" != "1" ]; then
            log_error "Sample user with email '$sample_user_email' not found in PostgreSQL"
            return 1
        fi
        
        log_info "Sample user validation passed"
    fi
    
    # Validate transaction amounts are preserved
    sqlite_total_amount=$(sqlite3 "$SQLITE_PATH" "SELECT ROUND(SUM(amount), 2) FROM transactions;")
    postgres_total_amount=$(psql "$POSTGRES_URL" -t -c "SELECT ROUND(SUM(amount), 2) FROM transactions;" | tr -d ' ')
    
    if [ "$sqlite_total_amount" != "$postgres_total_amount" ]; then
        log_error "Total transaction amount mismatch: SQLite=$sqlite_total_amount, PostgreSQL=$postgres_total_amount"
        return 1
    fi
    
    log_info "Transaction amount validation passed"
}

# Generate validation report
generate_report() {
    log_info "Generating validation report..."
    
    report_file="migration-validation-report-$(date +%Y%m%d-%H%M%S).txt"
    
    {
        echo "SQLite to PostgreSQL Migration Validation Report"
        echo "Generated: $(date)"
        echo "=============================================="
        echo ""
        
        echo "Database Information:"
        echo "SQLite Path: $SQLITE_PATH"
        echo "PostgreSQL URL: $(echo $POSTGRES_URL | sed 's/:\/\/.*@/:\/\/***@/')"
        echo ""
        
        echo "Record Counts:"
        echo "Users: $(psql "$POSTGRES_URL" -t -c "SELECT COUNT(*) FROM users;" | tr -d ' ')"
        echo "Goals: $(psql "$POSTGRES_URL" -t -c "SELECT COUNT(*) FROM goals;" | tr -d ' ')"
        echo "Transactions: $(psql "$POSTGRES_URL" -t -c "SELECT COUNT(*) FROM transactions;" | tr -d ' ')"
        echo "Plaid Accounts: $(psql "$POSTGRES_URL" -t -c "SELECT COUNT(*) FROM plaid_accounts;" | tr -d ' ')"
        echo "Weekly Plans: $(psql "$POSTGRES_URL" -t -c "SELECT COUNT(*) FROM weekly_plans;" | tr -d ' ')"
        echo ""
        
        echo "Data Quality Checks:"
        echo "Orphaned Goals: $(psql "$POSTGRES_URL" -t -c "SELECT COUNT(*) FROM goals g LEFT JOIN users u ON g.user_id = u.user_id WHERE u.user_id IS NULL;" | tr -d ' ')"
        echo "Orphaned Transactions: $(psql "$POSTGRES_URL" -t -c "SELECT COUNT(*) FROM transactions t LEFT JOIN users u ON t.user_id = u.user_id WHERE u.user_id IS NULL;" | tr -d ' ')"
        echo "Invalid Goal Amounts: $(psql "$POSTGRES_URL" -t -c "SELECT COUNT(*) FROM goals WHERE goal_amount <= 0;" | tr -d ' ')"
        echo ""
        
        echo "Sample Data:"
        echo "First User: $(psql "$POSTGRES_URL" -t -c "SELECT name, email FROM users ORDER BY user_id LIMIT 1;" | tr -d ' ')"
        echo "Latest Transaction: $(psql "$POSTGRES_URL" -t -c "SELECT transaction_id, amount, date FROM transactions ORDER BY date DESC LIMIT 1;")"
        echo ""
        
        echo "Validation Status: PASSED"
        
    } > "$report_file"
    
    log_info "Validation report saved to: $report_file"
}

# Main validation function
main() {
    log_info "Starting migration validation..."
    
    check_dependencies
    check_database_connectivity
    validate_table_counts
    validate_data_integrity
    validate_sample_data
    generate_report
    
    log_info "Migration validation completed successfully! ✅"
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Migration Validation Script"
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h          Show this help message"
        echo "  --counts-only       Only validate record counts"
        echo "  --integrity-only    Only validate data integrity"
        echo ""
        echo "Environment Variables:"
        echo "  SQLITE_PATH         Path to SQLite database (default: ./Back_End/Middleware/noumi.db)"
        echo "  DATABASE_URL        PostgreSQL connection URL"
        exit 0
        ;;
    --counts-only)
        check_dependencies
        check_database_connectivity
        validate_table_counts
        ;;
    --integrity-only)
        check_dependencies
        check_database_connectivity
        validate_data_integrity
        ;;
    *)
        main
        ;;
esac