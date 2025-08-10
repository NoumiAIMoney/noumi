#!/bin/bash

# SQLite to PostgreSQL Migration Runner
# This script orchestrates the complete migration process

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SQLITE_PATH="${SQLITE_PATH:-$PROJECT_ROOT/../Back_End/Middleware/noumi.db}"
DATABASE_URL="${DATABASE_URL:-postgres://user:password@localhost:5432/noumidb}"
DRY_RUN="${DRY_RUN:-false}"
VALIDATE_ONLY="${VALIDATE_ONLY:-false}"
BATCH_SIZE="${BATCH_SIZE:-100}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Print usage information
print_usage() {
    cat << EOF
SQLite to PostgreSQL Migration Runner

Usage: $0 [options]

Options:
    --sqlite-path PATH      Path to SQLite database file
    --postgres-url URL      PostgreSQL connection URL
    --dry-run              Perform a dry run without writing to PostgreSQL
    --validate-only        Only validate schemas, don't migrate data
    --batch-size SIZE      Number of records to process in each batch (default: 100)
    --skip-build           Skip building the migration tool
    --skip-validation      Skip post-migration validation
    --help                 Show this help message

Environment Variables:
    SQLITE_PATH           SQLite database file path
    DATABASE_URL          PostgreSQL connection URL
    DRY_RUN              Set to 'true' for dry run mode
    VALIDATE_ONLY        Set to 'true' to only validate schemas
    BATCH_SIZE           Batch size for processing records

Examples:
    # Basic migration
    $0 --sqlite-path ./noumi.db --postgres-url "postgres://user:pass@localhost/db"
    
    # Dry run to test migration
    $0 --dry-run
    
    # Validate schemas only
    $0 --validate-only
    
    # Use environment variables
    export DATABASE_URL="postgres://user:pass@localhost/db"
    export SQLITE_PATH="./noumi.db"
    $0

EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --sqlite-path)
                SQLITE_PATH="$2"
                shift 2
                ;;
            --postgres-url)
                DATABASE_URL="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN="true"
                shift
                ;;
            --validate-only)
                VALIDATE_ONLY="true"
                shift
                ;;
            --batch-size)
                BATCH_SIZE="$2"
                shift 2
                ;;
            --skip-build)
                SKIP_BUILD="true"
                shift
                ;;
            --skip-validation)
                SKIP_VALIDATION="true"
                shift
                ;;
            --help)
                print_usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                print_usage
                exit 1
                ;;
        esac
    done
}

# Validate prerequisites
validate_prerequisites() {
    log_step "Validating prerequisites..."
    
    # Check if Go is installed
    if ! command -v go &> /dev/null; then
        log_error "Go is required but not installed"
        exit 1
    fi
    
    # Check if SQLite file exists
    if [ ! -f "$SQLITE_PATH" ]; then
        log_error "SQLite database not found at: $SQLITE_PATH"
        exit 1
    fi
    
    # Check if PostgreSQL is accessible
    if ! command -v psql &> /dev/null; then
        log_warn "psql not found, skipping PostgreSQL connectivity check"
    else
        if ! psql "$DATABASE_URL" -c "SELECT 1;" &> /dev/null; then
            log_error "Cannot connect to PostgreSQL database"
            log_error "URL: $(echo $DATABASE_URL | sed 's/:\/\/.*@/:\/\/***@/')"
            exit 1
        fi
    fi
    
    log_info "Prerequisites validation passed"
}

# Build migration tool
build_migration_tool() {
    if [ "$SKIP_BUILD" = "true" ]; then
        log_info "Skipping build step"
        return
    fi
    
    log_step "Building migration tool..."
    
    cd "$PROJECT_ROOT"
    
    # Ensure dependencies are available
    if [ ! -f "go.mod" ]; then
        log_error "go.mod not found. Please run 'go mod init' first"
        exit 1
    fi
    
    # Build the migration tool
    CGO_ENABLED=1 go build -o bin/migrate-sqlite ./cmd/migrate-sqlite
    
    if [ ! -f "bin/migrate-sqlite" ]; then
        log_error "Failed to build migration tool"
        exit 1
    fi
    
    log_info "Migration tool built successfully"
}

# Run the migration
run_migration() {
    log_step "Running migration..."
    
    cd "$PROJECT_ROOT"
    
    # Prepare migration arguments
    MIGRATION_ARGS=(
        "--sqlite-path" "$SQLITE_PATH"
        "--postgres-url" "$DATABASE_URL"
        "--batch-size" "$BATCH_SIZE"
    )
    
    if [ "$DRY_RUN" = "true" ]; then
        MIGRATION_ARGS+=("--dry-run")
        log_info "Running in DRY RUN mode"
    fi
    
    if [ "$VALIDATE_ONLY" = "true" ]; then
        MIGRATION_ARGS+=("--validate-only")
        log_info "Running in VALIDATE ONLY mode"
    fi
    
    # Run the migration tool
    log_info "Executing migration with arguments: ${MIGRATION_ARGS[*]}"
    ./bin/migrate-sqlite "${MIGRATION_ARGS[@]}"
    
    if [ $? -eq 0 ]; then
        log_info "Migration completed successfully"
    else
        log_error "Migration failed"
        exit 1
    fi
}

# Run post-migration validation
run_validation() {
    if [ "$SKIP_VALIDATION" = "true" ] || [ "$DRY_RUN" = "true" ] || [ "$VALIDATE_ONLY" = "true" ]; then
        log_info "Skipping post-migration validation"
        return
    fi
    
    log_step "Running post-migration validation..."
    
    # Export environment variables for validation script
    export SQLITE_PATH
    export DATABASE_URL
    
    # Run validation script
    if [ -f "$SCRIPT_DIR/validate-migration.sh" ]; then
        bash "$SCRIPT_DIR/validate-migration.sh"
    else
        log_warn "Validation script not found, skipping validation"
    fi
}

# Generate migration summary
generate_summary() {
    log_step "Generating migration summary..."
    
    local summary_file="migration-summary-$(date +%Y%m%d-%H%M%S).txt"
    
    {
        echo "SQLite to PostgreSQL Migration Summary"
        echo "======================================"
        echo "Date: $(date)"
        echo "SQLite Path: $SQLITE_PATH"
        echo "PostgreSQL URL: $(echo $DATABASE_URL | sed 's/:\/\/.*@/:\/\/***@/')"
        echo "Dry Run: $DRY_RUN"
        echo "Validate Only: $VALIDATE_ONLY"
        echo "Batch Size: $BATCH_SIZE"
        echo ""
        
        if [ "$DRY_RUN" != "true" ] && [ "$VALIDATE_ONLY" != "true" ]; then
            echo "Final Record Counts:"
            if command -v psql &> /dev/null; then
                echo "Users: $(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM users;" 2>/dev/null | tr -d ' ' || echo 'N/A')"
                echo "Goals: $(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM goals;" 2>/dev/null | tr -d ' ' || echo 'N/A')"
                echo "Transactions: $(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM transactions;" 2>/dev/null | tr -d ' ' || echo 'N/A')"
                echo "Plaid Accounts: $(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM plaid_accounts;" 2>/dev/null | tr -d ' ' || echo 'N/A')"
                echo "Weekly Plans: $(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM weekly_plans;" 2>/dev/null | tr -d ' ' || echo 'N/A')"
            else
                echo "PostgreSQL client not available for count verification"
            fi
        fi
        
        echo ""
        echo "Migration Status: COMPLETED"
        
    } > "$summary_file"
    
    log_info "Migration summary saved to: $summary_file"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up..."
    # Add any cleanup tasks here
}

# Error handler
error_handler() {
    local line_number=$1
    log_error "An error occurred on line $line_number"
    cleanup
    exit 1
}

# Set error trap
trap 'error_handler $LINENO' ERR

# Main execution
main() {
    log_info "Starting SQLite to PostgreSQL migration process"
    log_info "Script directory: $SCRIPT_DIR"
    log_info "Project root: $PROJECT_ROOT"
    
    parse_args "$@"
    validate_prerequisites
    build_migration_tool
    run_migration
    run_validation
    generate_summary
    
    log_info "Migration process completed successfully! 🎉"
}

# Execute main function with all arguments
main "$@"