package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"
	"time"

	_ "github.com/lib/pq"
	_ "github.com/mattn/go-sqlite3"
)

// Configuration for the migration
type MigrationConfig struct {
	SQLitePath    string
	PostgreSQLURL string
	DryRun        bool
	ValidateOnly  bool
	BatchSize     int
}

// SQLite schema structures
type SQLiteUser struct {
	ID          string `json:"id"`
	Email       string `json:"email"`
	Name        string `json:"name"`
	CreatedAt   string `json:"created_at"`
	Preferences string `json:"preferences"`
}

type SQLiteUserGoal struct {
	UserID           string  `json:"user_id"`
	GoalName         string  `json:"goal_name"`
	GoalDescription  *string `json:"goal_description"`
	GoalAmount       float64 `json:"goal_amount"`
	TargetDate       string  `json:"target_date"`
	NetMonthlyIncome float64 `json:"net_monthly_income"`
	CreatedAt        string  `json:"created_at"`
}

type SQLiteTransaction struct {
	TransactionID string  `json:"transaction_id"`
	UserID        string  `json:"user_id"`
	AccountID     string  `json:"account_id"`
	Amount        float64 `json:"amount"`
	Date          string  `json:"date"`
	Description   string  `json:"description"`
	Category      string  `json:"category"`
	MerchantName  *string `json:"merchant_name"`
	CreatedAt     string  `json:"created_at"`
}

type SQLitePlaidConnection struct {
	UserID      string `json:"user_id"`
	AccessToken string `json:"access_token"`
	Accounts    string `json:"accounts"`
	ConnectedAt string `json:"connected_at"`
}

type SQLiteWeeklyPlan struct {
	UserID    string `json:"user_id"`
	WeekStart string `json:"week_start"`
	PlanData  string `json:"plan_data"`
	CreatedAt string `json:"created_at"`
}

type SQLiteWeeklyRecap struct {
	UserID    string `json:"user_id"`
	WeekStart string `json:"week_start"`
	RecapData string `json:"recap_data"`
	CreatedAt string `json:"created_at"`
}

// Migration statistics
type MigrationStats struct {
	UsersProcessed            int
	GoalsProcessed            int
	TransactionsProcessed     int
	PlaidConnectionsProcessed int
	WeeklyPlansProcessed      int
	WeeklyRecapsProcessed     int
	Errors                    []string
}

func main() {
	config := parseArgs()

	log.Printf("Starting SQLite to PostgreSQL migration")
	log.Printf("SQLite path: %s", config.SQLitePath)
	log.Printf("PostgreSQL URL: %s", maskPassword(config.PostgreSQLURL))
	log.Printf("Dry run: %t", config.DryRun)
	log.Printf("Validate only: %t", config.ValidateOnly)

	migrator := NewMigrator(config)
	defer migrator.Close()

	if err := migrator.Connect(); err != nil {
		log.Fatalf("Failed to connect to databases: %v", err)
	}

	if config.ValidateOnly {
		if err := migrator.ValidateSchemas(); err != nil {
			log.Fatalf("Schema validation failed: %v", err)
		}
		log.Println("Schema validation completed successfully")
		return
	}

	stats, err := migrator.Migrate()
	if err != nil {
		log.Fatalf("Migration failed: %v", err)
	}

	migrator.PrintStats(stats)

	if !config.DryRun {
		if err := migrator.ValidateDataIntegrity(); err != nil {
			log.Printf("Data integrity validation failed: %v", err)
		} else {
			log.Println("Data integrity validation passed")
		}
	}

	log.Println("Migration completed successfully")
}

func parseArgs() *MigrationConfig {
	config := &MigrationConfig{
		BatchSize: 100,
	}

	args := os.Args[1:]
	for i := 0; i < len(args); i++ {
		switch args[i] {
		case "--sqlite-path":
			if i+1 < len(args) {
				config.SQLitePath = args[i+1]
				i++
			}
		case "--postgres-url":
			if i+1 < len(args) {
				config.PostgreSQLURL = args[i+1]
				i++
			}
		case "--dry-run":
			config.DryRun = true
		case "--validate-only":
			config.ValidateOnly = true
		case "--batch-size":
			if i+1 < len(args) {
				if size, err := strconv.Atoi(args[i+1]); err == nil {
					config.BatchSize = size
				}
				i++
			}
		case "--help":
			printUsage()
			os.Exit(0)
		}
	}

	// Set defaults from environment if not provided
	if config.SQLitePath == "" {
		config.SQLitePath = os.Getenv("SQLITE_PATH")
		if config.SQLitePath == "" {
			config.SQLitePath = "./noumi.db"
		}
	}

	if config.PostgreSQLURL == "" {
		config.PostgreSQLURL = os.Getenv("DATABASE_URL")
		if config.PostgreSQLURL == "" {
			log.Fatal("PostgreSQL URL must be provided via --postgres-url or DATABASE_URL environment variable")
		}
	}

	return config
}

func printUsage() {
	fmt.Println("SQLite to PostgreSQL Migration Tool")
	fmt.Println("Usage: migrate-sqlite [options]")
	fmt.Println("")
	fmt.Println("Options:")
	fmt.Println("  --sqlite-path PATH     Path to SQLite database file (default: ./noumi.db)")
	fmt.Println("  --postgres-url URL     PostgreSQL connection URL")
	fmt.Println("  --dry-run              Perform a dry run without writing to PostgreSQL")
	fmt.Println("  --validate-only        Only validate schemas, don't migrate data")
	fmt.Println("  --batch-size SIZE      Number of records to process in each batch (default: 100)")
	fmt.Println("  --help                 Show this help message")
	fmt.Println("")
	fmt.Println("Environment variables:")
	fmt.Println("  SQLITE_PATH           SQLite database file path")
	fmt.Println("  DATABASE_URL          PostgreSQL connection URL")
}

func maskPassword(url string) string {
	if strings.Contains(url, "@") {
		parts := strings.Split(url, "@")
		if len(parts) >= 2 {
			userPart := parts[0]
			if strings.Contains(userPart, ":") {
				userParts := strings.Split(userPart, ":")
				if len(userParts) >= 3 {
					return userParts[0] + ":" + userParts[1] + ":****@" + strings.Join(parts[1:], "@")
				}
			}
		}
	}
	return url
}

// Migrator handles the migration process
type Migrator struct {
	config     *MigrationConfig
	sqliteDB   *sql.DB
	postgresDB *sql.DB
}

func NewMigrator(config *MigrationConfig) *Migrator {
	return &Migrator{
		config: config,
	}
}

func (m *Migrator) Connect() error {
	// Connect to SQLite
	sqliteDB, err := sql.Open("sqlite3", m.config.SQLitePath)
	if err != nil {
		return fmt.Errorf("failed to open SQLite database: %w", err)
	}

	if err := sqliteDB.Ping(); err != nil {
		return fmt.Errorf("failed to ping SQLite database: %w", err)
	}

	m.sqliteDB = sqliteDB
	log.Println("Connected to SQLite database")

	// Connect to PostgreSQL
	postgresDB, err := sql.Open("postgres", m.config.PostgreSQLURL)
	if err != nil {
		return fmt.Errorf("failed to open PostgreSQL database: %w", err)
	}

	if err := postgresDB.Ping(); err != nil {
		return fmt.Errorf("failed to ping PostgreSQL database: %w", err)
	}

	m.postgresDB = postgresDB
	log.Println("Connected to PostgreSQL database")

	return nil
}

func (m *Migrator) Close() {
	if m.sqliteDB != nil {
		m.sqliteDB.Close()
	}
	if m.postgresDB != nil {
		m.postgresDB.Close()
	}
}

func (m *Migrator) ValidateSchemas() error {
	log.Println("Validating database schemas...")

	// Check SQLite tables exist
	sqliteTables := []string{"users", "user_goals", "transactions", "plaid_connections", "weekly_plans", "weekly_recaps"}
	for _, table := range sqliteTables {
		var count int
		err := m.sqliteDB.QueryRow(fmt.Sprintf("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='%s'", table)).Scan(&count)
		if err != nil {
			return fmt.Errorf("failed to check SQLite table %s: %w", table, err)
		}
		if count == 0 {
			return fmt.Errorf("SQLite table %s does not exist", table)
		}
	}

	// Check PostgreSQL tables exist
	postgresTables := []string{"users", "goals", "transactions", "plaid_accounts", "weekly_plans"}
	for _, table := range postgresTables {
		var count int
		err := m.postgresDB.QueryRow("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = $1", table).Scan(&count)
		if err != nil {
			return fmt.Errorf("failed to check PostgreSQL table %s: %w", table, err)
		}
		if count == 0 {
			return fmt.Errorf("PostgreSQL table %s does not exist", table)
		}
	}

	log.Println("Schema validation completed successfully")
	return nil
}

func (m *Migrator) Migrate() (*MigrationStats, error) {
	stats := &MigrationStats{}

	log.Println("Starting data migration...")

	// Begin transaction for PostgreSQL if not dry run
	var tx *sql.Tx
	if !m.config.DryRun {
		var err error
		tx, err = m.postgresDB.Begin()
		if err != nil {
			return stats, fmt.Errorf("failed to begin transaction: %w", err)
		}
		defer func() {
			if err := recover(); err != nil {
				tx.Rollback()
				panic(err)
			}
		}()
	}

	// Migrate users first (they are referenced by other tables)
	if err := m.migrateUsers(tx, stats); err != nil {
		if tx != nil {
			tx.Rollback()
		}
		return stats, fmt.Errorf("failed to migrate users: %w", err)
	}

	// Migrate goals
	if err := m.migrateGoals(tx, stats); err != nil {
		if tx != nil {
			tx.Rollback()
		}
		return stats, fmt.Errorf("failed to migrate goals: %w", err)
	}

	// Migrate Plaid connections (creates plaid_accounts)
	if err := m.migratePlaidConnections(tx, stats); err != nil {
		if tx != nil {
			tx.Rollback()
		}
		return stats, fmt.Errorf("failed to migrate plaid connections: %w", err)
	}

	// Migrate transactions
	if err := m.migrateTransactions(tx, stats); err != nil {
		if tx != nil {
			tx.Rollback()
		}
		return stats, fmt.Errorf("failed to migrate transactions: %w", err)
	}

	// Migrate weekly plans
	if err := m.migrateWeeklyPlans(tx, stats); err != nil {
		if tx != nil {
			tx.Rollback()
		}
		return stats, fmt.Errorf("failed to migrate weekly plans: %w", err)
	}

	// Commit transaction if not dry run
	if !m.config.DryRun && tx != nil {
		if err := tx.Commit(); err != nil {
			return stats, fmt.Errorf("failed to commit transaction: %w", err)
		}
		log.Println("Transaction committed successfully")
	}

	return stats, nil
}

func (m *Migrator) migrateUsers(tx *sql.Tx, stats *MigrationStats) error {
	log.Println("Migrating users...")

	rows, err := m.sqliteDB.Query("SELECT id, email, name, created_at, preferences FROM users")
	if err != nil {
		return fmt.Errorf("failed to query SQLite users: %w", err)
	}
	defer rows.Close()

	for rows.Next() {
		var user SQLiteUser
		if err := rows.Scan(&user.ID, &user.Email, &user.Name, &user.CreatedAt, &user.Preferences); err != nil {
			stats.Errors = append(stats.Errors, fmt.Sprintf("Failed to scan user: %v", err))
			continue
		}

		if m.config.DryRun {
			log.Printf("DRY RUN: Would migrate user %s (%s)", user.Name, user.Email)
		} else {
			// Convert SQLite user ID (string) to PostgreSQL user_id (integer)
			// We'll use a simple hash-based approach to generate consistent integer IDs
			userID := hashStringToInt(user.ID)

			// Parse preferences JSON or set default
			var preferences map[string]interface{}
			if user.Preferences != "" && user.Preferences != "{}" {
				if err := json.Unmarshal([]byte(user.Preferences), &preferences); err != nil {
					preferences = make(map[string]interface{})
				}
			} else {
				preferences = make(map[string]interface{})
			}

			// Extract financial goal and other fields from preferences
			financialGoal := "GOAL_SAVINGS" // default
			if goal, ok := preferences["financial_goal"].(string); ok {
				financialGoal = goal
			}

			// Convert created_at to proper timestamp
			createdAt, err := parseTimestamp(user.CreatedAt)
			if err != nil {
				stats.Errors = append(stats.Errors, fmt.Sprintf("Failed to parse created_at for user %s: %v", user.ID, err))
				continue
			}

			query := `
				INSERT INTO users (user_id, email, password_hash, name, financial_goal, impulse_triggers, budgeting_score, created_at)
				VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
				ON CONFLICT (user_id) DO UPDATE SET
					email = EXCLUDED.email,
					name = EXCLUDED.name,
					financial_goal = EXCLUDED.financial_goal
			`

			var executor interface {
				Exec(query string, args ...interface{}) (sql.Result, error)
			}

			if tx != nil {
				executor = tx
			} else {
				executor = m.postgresDB
			}

			_, err = executor.Exec(query, userID, user.Email, "migrated_user", user.Name,
				financialGoal, "[]", 2, createdAt)
			if err != nil {
				stats.Errors = append(stats.Errors, fmt.Sprintf("Failed to insert user %s: %v", user.ID, err))
				continue
			}
		}

		stats.UsersProcessed++
	}

	log.Printf("Migrated %d users", stats.UsersProcessed)
	return nil
}

func (m *Migrator) migrateGoals(tx *sql.Tx, stats *MigrationStats) error {
	log.Println("Migrating goals...")

	rows, err := m.sqliteDB.Query(`
		SELECT user_id, goal_name, goal_description, goal_amount, target_date, net_monthly_income, created_at 
		FROM user_goals
	`)
	if err != nil {
		return fmt.Errorf("failed to query SQLite user_goals: %w", err)
	}
	defer rows.Close()

	for rows.Next() {
		var goal SQLiteUserGoal
		if err := rows.Scan(&goal.UserID, &goal.GoalName, &goal.GoalDescription,
			&goal.GoalAmount, &goal.TargetDate, &goal.NetMonthlyIncome, &goal.CreatedAt); err != nil {
			stats.Errors = append(stats.Errors, fmt.Sprintf("Failed to scan goal: %v", err))
			continue
		}

		if m.config.DryRun {
			log.Printf("DRY RUN: Would migrate goal %s for user %s", goal.GoalName, goal.UserID)
		} else {
			userID := hashStringToInt(goal.UserID)

			// Parse dates
			targetDate, err := parseDate(goal.TargetDate)
			if err != nil {
				stats.Errors = append(stats.Errors, fmt.Sprintf("Failed to parse target_date for goal %s: %v", goal.GoalName, err))
				continue
			}

			createdAt, err := parseTimestamp(goal.CreatedAt)
			if err != nil {
				stats.Errors = append(stats.Errors, fmt.Sprintf("Failed to parse created_at for goal %s: %v", goal.GoalName, err))
				continue
			}

			query := `
				INSERT INTO goals (user_id, goal_name, goal_description, goal_amount, target_date, net_monthly_income, created_at)
				VALUES ($1, $2, $3, $4, $5, $6, $7)
			`

			var executor interface {
				Exec(query string, args ...interface{}) (sql.Result, error)
			}

			if tx != nil {
				executor = tx
			} else {
				executor = m.postgresDB
			}

			_, err = executor.Exec(query, userID, goal.GoalName, goal.GoalDescription,
				goal.GoalAmount, targetDate, goal.NetMonthlyIncome, createdAt)
			if err != nil {
				stats.Errors = append(stats.Errors, fmt.Sprintf("Failed to insert goal %s: %v", goal.GoalName, err))
				continue
			}
		}

		stats.GoalsProcessed++
	}

	log.Printf("Migrated %d goals", stats.GoalsProcessed)
	return nil
}

func (m *Migrator) migratePlaidConnections(tx *sql.Tx, stats *MigrationStats) error {
	log.Println("Migrating Plaid connections...")

	rows, err := m.sqliteDB.Query("SELECT user_id, access_token, accounts, connected_at FROM plaid_connections")
	if err != nil {
		return fmt.Errorf("failed to query SQLite plaid_connections: %w", err)
	}
	defer rows.Close()

	for rows.Next() {
		var conn SQLitePlaidConnection
		if err := rows.Scan(&conn.UserID, &conn.AccessToken, &conn.Accounts, &conn.ConnectedAt); err != nil {
			stats.Errors = append(stats.Errors, fmt.Sprintf("Failed to scan plaid connection: %v", err))
			continue
		}

		if m.config.DryRun {
			log.Printf("DRY RUN: Would migrate Plaid connection for user %s", conn.UserID)
		} else {
			userID := hashStringToInt(conn.UserID)

			// Parse accounts JSON
			var accounts []map[string]interface{}
			if err := json.Unmarshal([]byte(conn.Accounts), &accounts); err != nil {
				stats.Errors = append(stats.Errors, fmt.Sprintf("Failed to parse accounts JSON for user %s: %v", conn.UserID, err))
				continue
			}

			createdAt, err := parseTimestamp(conn.ConnectedAt)
			if err != nil {
				stats.Errors = append(stats.Errors, fmt.Sprintf("Failed to parse connected_at for user %s: %v", conn.UserID, err))
				continue
			}

			// Create plaid_accounts entries for each account
			for _, account := range accounts {
				accountID, ok := account["account_id"].(string)
				if !ok {
					continue
				}

				accountName, _ := account["name"].(string)
				accountType, _ := account["type"].(string)
				bankName, _ := account["institution_name"].(string)

				query := `
					INSERT INTO plaid_accounts (account_id, user_id, plaid_item_id, account_name, account_type, bank_name, created_at)
					VALUES ($1, $2, $3, $4, $5, $6, $7)
					ON CONFLICT (account_id) DO UPDATE SET
						account_name = EXCLUDED.account_name,
						account_type = EXCLUDED.account_type,
						bank_name = EXCLUDED.bank_name
				`

				var executor interface {
					Exec(query string, args ...interface{}) (sql.Result, error)
				}

				if tx != nil {
					executor = tx
				} else {
					executor = m.postgresDB
				}

				_, err = executor.Exec(query, accountID, userID, "migrated_item", accountName, accountType, bankName, createdAt)
				if err != nil {
					stats.Errors = append(stats.Errors, fmt.Sprintf("Failed to insert plaid account %s: %v", accountID, err))
					continue
				}
			}

			// Update user with plaid token
			updateQuery := "UPDATE users SET plaid_token = $1 WHERE user_id = $2"
			var executor interface {
				Exec(query string, args ...interface{}) (sql.Result, error)
			}

			if tx != nil {
				executor = tx
			} else {
				executor = m.postgresDB
			}

			_, err = executor.Exec(updateQuery, conn.AccessToken, userID)
			if err != nil {
				stats.Errors = append(stats.Errors, fmt.Sprintf("Failed to update user plaid token for user %s: %v", conn.UserID, err))
			}
		}

		stats.PlaidConnectionsProcessed++
	}

	log.Printf("Migrated %d Plaid connections", stats.PlaidConnectionsProcessed)
	return nil
}

func (m *Migrator) migrateTransactions(tx *sql.Tx, stats *MigrationStats) error {
	log.Println("Migrating transactions...")

	rows, err := m.sqliteDB.Query(`
		SELECT transaction_id, user_id, account_id, amount, date, description, category, merchant_name, created_at 
		FROM transactions
	`)
	if err != nil {
		return fmt.Errorf("failed to query SQLite transactions: %w", err)
	}
	defer rows.Close()

	batch := make([]SQLiteTransaction, 0, m.config.BatchSize)

	for rows.Next() {
		var txn SQLiteTransaction
		if err := rows.Scan(&txn.TransactionID, &txn.UserID, &txn.AccountID, &txn.Amount,
			&txn.Date, &txn.Description, &txn.Category, &txn.MerchantName, &txn.CreatedAt); err != nil {
			stats.Errors = append(stats.Errors, fmt.Sprintf("Failed to scan transaction: %v", err))
			continue
		}

		batch = append(batch, txn)

		if len(batch) >= m.config.BatchSize {
			if err := m.processBatchTransactions(tx, batch, stats); err != nil {
				return err
			}
			batch = batch[:0] // Reset batch
		}
	}

	// Process remaining transactions
	if len(batch) > 0 {
		if err := m.processBatchTransactions(tx, batch, stats); err != nil {
			return err
		}
	}

	log.Printf("Migrated %d transactions", stats.TransactionsProcessed)
	return nil
}

func (m *Migrator) processBatchTransactions(tx *sql.Tx, batch []SQLiteTransaction, stats *MigrationStats) error {
	for _, txn := range batch {
		if m.config.DryRun {
			log.Printf("DRY RUN: Would migrate transaction %s", txn.TransactionID)
		} else {
			userID := hashStringToInt(txn.UserID)

			// Parse date
			date, err := parseDate(txn.Date)
			if err != nil {
				stats.Errors = append(stats.Errors, fmt.Sprintf("Failed to parse date for transaction %s: %v", txn.TransactionID, err))
				continue
			}

			createdAt, err := parseTimestamp(txn.CreatedAt)
			if err != nil {
				stats.Errors = append(stats.Errors, fmt.Sprintf("Failed to parse created_at for transaction %s: %v", txn.TransactionID, err))
				continue
			}

			// Extract MCC from description or set default
			mcc := 0 // Default MCC

			query := `
				INSERT INTO transactions (transaction_id, account_id, user_id, amount, date, merchant_name, category, mcc, created_at)
				VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
				ON CONFLICT (transaction_id) DO UPDATE SET
					amount = EXCLUDED.amount,
					date = EXCLUDED.date,
					merchant_name = EXCLUDED.merchant_name,
					category = EXCLUDED.category
			`

			var executor interface {
				Exec(query string, args ...interface{}) (sql.Result, error)
			}

			if tx != nil {
				executor = tx
			} else {
				executor = m.postgresDB
			}

			merchantName := ""
			if txn.MerchantName != nil {
				merchantName = *txn.MerchantName
			}

			_, err = executor.Exec(query, txn.TransactionID, txn.AccountID, userID,
				txn.Amount, date, merchantName, txn.Category, mcc, createdAt)
			if err != nil {
				stats.Errors = append(stats.Errors, fmt.Sprintf("Failed to insert transaction %s: %v", txn.TransactionID, err))
				continue
			}
		}

		stats.TransactionsProcessed++
	}

	return nil
}

func (m *Migrator) migrateWeeklyPlans(tx *sql.Tx, stats *MigrationStats) error {
	log.Println("Migrating weekly plans...")

	rows, err := m.sqliteDB.Query("SELECT user_id, week_start, plan_data, created_at FROM weekly_plans")
	if err != nil {
		return fmt.Errorf("failed to query SQLite weekly_plans: %w", err)
	}
	defer rows.Close()

	for rows.Next() {
		var plan SQLiteWeeklyPlan
		if err := rows.Scan(&plan.UserID, &plan.WeekStart, &plan.PlanData, &plan.CreatedAt); err != nil {
			stats.Errors = append(stats.Errors, fmt.Sprintf("Failed to scan weekly plan: %v", err))
			continue
		}

		if m.config.DryRun {
			log.Printf("DRY RUN: Would migrate weekly plan for user %s, week %s", plan.UserID, plan.WeekStart)
		} else {
			userID := hashStringToInt(plan.UserID)

			// Parse dates
			weekStart, err := parseDate(plan.WeekStart)
			if err != nil {
				stats.Errors = append(stats.Errors, fmt.Sprintf("Failed to parse week_start for plan %s: %v", plan.WeekStart, err))
				continue
			}

			// Calculate week end (assuming week_start is Monday, week_end is Sunday)
			weekEnd := weekStart.AddDate(0, 0, 6)

			createdAt, err := parseTimestamp(plan.CreatedAt)
			if err != nil {
				stats.Errors = append(stats.Errors, fmt.Sprintf("Failed to parse created_at for plan %s: %v", plan.WeekStart, err))
				continue
			}

			query := `
				INSERT INTO weekly_plans (user_id, week_start_date, week_end_date, plan_data, ml_features, created_at, is_active)
				VALUES ($1, $2, $3, $4, $5, $6, $7)
				ON CONFLICT (user_id, week_start_date) DO UPDATE SET
					plan_data = EXCLUDED.plan_data,
					ml_features = EXCLUDED.ml_features
			`

			var executor interface {
				Exec(query string, args ...interface{}) (sql.Result, error)
			}

			if tx != nil {
				executor = tx
			} else {
				executor = m.postgresDB
			}

			_, err = executor.Exec(query, userID, weekStart, weekEnd, plan.PlanData, "{}", createdAt, true)
			if err != nil {
				stats.Errors = append(stats.Errors, fmt.Sprintf("Failed to insert weekly plan %s: %v", plan.WeekStart, err))
				continue
			}
		}

		stats.WeeklyPlansProcessed++
	}

	log.Printf("Migrated %d weekly plans", stats.WeeklyPlansProcessed)
	return nil
}

func (m *Migrator) ValidateDataIntegrity() error {
	log.Println("Validating data integrity...")

	// Check user counts match
	var sqliteUserCount, postgresUserCount int

	err := m.sqliteDB.QueryRow("SELECT COUNT(*) FROM users").Scan(&sqliteUserCount)
	if err != nil {
		return fmt.Errorf("failed to count SQLite users: %w", err)
	}

	err = m.postgresDB.QueryRow("SELECT COUNT(*) FROM users").Scan(&postgresUserCount)
	if err != nil {
		return fmt.Errorf("failed to count PostgreSQL users: %w", err)
	}

	if sqliteUserCount != postgresUserCount {
		return fmt.Errorf("user count mismatch: SQLite=%d, PostgreSQL=%d", sqliteUserCount, postgresUserCount)
	}

	// Check transaction counts match
	var sqliteTransactionCount, postgresTransactionCount int

	err = m.sqliteDB.QueryRow("SELECT COUNT(*) FROM transactions").Scan(&sqliteTransactionCount)
	if err != nil {
		return fmt.Errorf("failed to count SQLite transactions: %w", err)
	}

	err = m.postgresDB.QueryRow("SELECT COUNT(*) FROM transactions").Scan(&postgresTransactionCount)
	if err != nil {
		return fmt.Errorf("failed to count PostgreSQL transactions: %w", err)
	}

	if sqliteTransactionCount != postgresTransactionCount {
		return fmt.Errorf("transaction count mismatch: SQLite=%d, PostgreSQL=%d", sqliteTransactionCount, postgresTransactionCount)
	}

	// Check goal counts match
	var sqliteGoalCount, postgresGoalCount int

	err = m.sqliteDB.QueryRow("SELECT COUNT(*) FROM user_goals").Scan(&sqliteGoalCount)
	if err != nil {
		return fmt.Errorf("failed to count SQLite goals: %w", err)
	}

	err = m.postgresDB.QueryRow("SELECT COUNT(*) FROM goals").Scan(&postgresGoalCount)
	if err != nil {
		return fmt.Errorf("failed to count PostgreSQL goals: %w", err)
	}

	if sqliteGoalCount != postgresGoalCount {
		return fmt.Errorf("goal count mismatch: SQLite=%d, PostgreSQL=%d", sqliteGoalCount, postgresGoalCount)
	}

	log.Printf("Data integrity validation passed:")
	log.Printf("  Users: %d", postgresUserCount)
	log.Printf("  Goals: %d", postgresGoalCount)
	log.Printf("  Transactions: %d", postgresTransactionCount)

	return nil
}

func (m *Migrator) PrintStats(stats *MigrationStats) {
	log.Println("Migration Statistics:")
	log.Printf("  Users processed: %d", stats.UsersProcessed)
	log.Printf("  Goals processed: %d", stats.GoalsProcessed)
	log.Printf("  Transactions processed: %d", stats.TransactionsProcessed)
	log.Printf("  Plaid connections processed: %d", stats.PlaidConnectionsProcessed)
	log.Printf("  Weekly plans processed: %d", stats.WeeklyPlansProcessed)
	log.Printf("  Errors encountered: %d", len(stats.Errors))

	if len(stats.Errors) > 0 {
		log.Println("Errors:")
		for i, err := range stats.Errors {
			if i < 10 { // Show first 10 errors
				log.Printf("  %s", err)
			} else if i == 10 {
				log.Printf("  ... and %d more errors", len(stats.Errors)-10)
				break
			}
		}
	}
}

// Utility functions
func hashStringToInt(s string) int {
	hash := 0
	for _, c := range s {
		hash = hash*31 + int(c)
	}
	if hash < 0 {
		hash = -hash
	}
	return hash
}

func parseTimestamp(ts string) (time.Time, error) {
	// Try different timestamp formats
	formats := []string{
		time.RFC3339,
		"2006-01-02 15:04:05",
		"2006-01-02T15:04:05",
		"2006-01-02 15:04:05.000000",
		"2006-01-02T15:04:05.000000",
	}

	for _, format := range formats {
		if t, err := time.Parse(format, ts); err == nil {
			return t, nil
		}
	}

	return time.Time{}, fmt.Errorf("unable to parse timestamp: %s", ts)
}

func parseDate(dateStr string) (time.Time, error) {
	// Try different date formats
	formats := []string{
		"2006-01-02",
		"01/02/2006",
		"2006-01-02 15:04:05",
		"2006-01-02T15:04:05",
	}

	for _, format := range formats {
		if t, err := time.Parse(format, dateStr); err == nil {
			return t, nil
		}
	}

	return time.Time{}, fmt.Errorf("unable to parse date: %s", dateStr)
}
