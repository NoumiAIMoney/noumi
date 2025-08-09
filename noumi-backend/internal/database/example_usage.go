package database

import (
	"context"
	"time"

	"noumi-backend/internal/database/models"

	"github.com/sirupsen/logrus"
)

// ExampleUsage demonstrates how to use the database layer
// This file is for documentation purposes and should not be included in production builds
func ExampleUsage() {
	// Initialize logger
	logger := logrus.New()

	// Database configuration
	config := &Config{
		Host:     "localhost",
		Port:     5432,
		User:     "postgres",
		Password: "password",
		Database: "noumidb",
		SSLMode:  "disable",
	}

	// Create database manager
	dbManager, err := NewManager(config, logger)
	if err != nil {
		logger.WithError(err).Fatal("Failed to create database manager")
		return
	}
	defer dbManager.Close()

	// Initialize database (run migrations)
	err = dbManager.Initialize()
	if err != nil {
		logger.WithError(err).Fatal("Failed to initialize database")
		return
	}

	logger.Info("Database initialized successfully with migrations")

	// Get repository
	repo := dbManager.GetRepository()
	ctx := context.Background()

	// Example: Create a user
	user := &models.User{
		Email:           "user@example.com",
		PasswordHash:    "hashed_password",
		Name:            "John Doe",
		FinancialGoal:   "GOAL_SAVINGS",
		ImpulseTriggers: models.StringSlice{"Stress", "FOMO"},
		BudgetingScore:  3,
		CreatedAt:       time.Now(),
	}

	err = repo.User.Create(ctx, user)
	if err != nil {
		logger.WithError(err).Error("Failed to create user")
		return
	}

	logger.WithField("user_id", user.UserID).Info("User created successfully")

	// Example: Create a goal for the user
	goal := &models.Goal{
		UserID:           user.UserID,
		GoalName:         "Emergency Fund",
		GoalDescription:  "Build a 6-month emergency fund",
		GoalAmount:       10000.00,
		TargetDate:       time.Now().AddDate(1, 0, 0), // 1 year from now
		NetMonthlyIncome: func() *float64 { v := 5000.00; return &v }(),
		CreatedAt:        time.Now(),
	}

	err = repo.Goal.Create(ctx, goal)
	if err != nil {
		logger.WithError(err).Error("Failed to create goal")
		return
	}

	logger.WithField("goal_id", goal.GoalID).Info("Goal created successfully")

	// Example: Create a Plaid account
	plaidAccount := &models.PlaidAccount{
		AccountID:   "account_123",
		UserID:      user.UserID,
		PlaidItemID: "item_123",
		AccountName: "Checking Account",
		AccountType: "depository",
		BankName:    "Chase Bank",
		IsActive:    true,
		CreatedAt:   time.Now(),
	}

	err = repo.PlaidAccount.Create(ctx, plaidAccount)
	if err != nil {
		logger.WithError(err).Error("Failed to create Plaid account")
		return
	}

	logger.WithField("account_id", plaidAccount.AccountID).Info("Plaid account created successfully")

	// Example: Create a transaction
	transaction := &models.Transaction{
		TransactionID: "txn_123",
		AccountID:     plaidAccount.AccountID,
		UserID:        user.UserID,
		Amount:        -50.00, // Negative for spending
		Date:          time.Now(),
		MerchantName:  "Starbucks",
		Category:      "Food & Drink",
		MCC:           5814,
		CreatedAt:     time.Now(),
	}

	err = repo.Transaction.Create(ctx, transaction)
	if err != nil {
		logger.WithError(err).Error("Failed to create transaction")
		return
	}

	logger.WithField("transaction_id", transaction.TransactionID).Info("Transaction created successfully")

	// Example: Query user transactions
	filters := models.TransactionFilters{
		StartDate: func() *time.Time { t := time.Now().AddDate(0, -1, 0); return &t }(), // Last month
		EndDate:   func() *time.Time { t := time.Now(); return &t }(),
		Limit:     func() *int { v := 10; return &v }(),
	}

	transactions, err := repo.Transaction.GetByUserID(ctx, user.UserID, filters)
	if err != nil {
		logger.WithError(err).Error("Failed to get user transactions")
		return
	}

	logger.WithField("count", len(transactions)).Info("Retrieved user transactions")

	// Example: Create an anomaly record
	anomaly := &models.Anomaly{
		UserID:        user.UserID,
		TransactionID: transaction.TransactionID,
		Date:          transaction.Date,
		IsAnomaly:     true,
		AnomalyScore:  func() *float64 { v := -0.75; return &v }(),
		CreatedAt:     time.Now(),
	}

	err = repo.Anomaly.Create(ctx, anomaly)
	if err != nil {
		logger.WithError(err).Error("Failed to create anomaly")
		return
	}

	logger.WithField("anomaly_id", anomaly.AnomalyID).Info("Anomaly created successfully")

	// Example: Create a weekly plan
	weeklyPlan := &models.WeeklyPlan{
		UserID:        user.UserID,
		WeekStartDate: time.Now().Truncate(24 * time.Hour),                  // Start of today
		WeekEndDate:   time.Now().AddDate(0, 0, 6).Truncate(24 * time.Hour), // 6 days later
		PlanData: models.JSONMap{
			"budget_categories": map[string]interface{}{
				"food":           200.00,
				"transportation": 100.00,
				"entertainment":  50.00,
			},
			"savings_goal": 500.00,
			"recommendations": []string{
				"Limit dining out to 3 times this week",
				"Use public transportation when possible",
			},
		},
		MLFeatures: models.JSONMap{
			"avg_weekly_spending": 350.00,
			"category_variance":   0.25,
			"anomaly_frequency":   0.1,
		},
		IsActive:  true,
		CreatedAt: time.Now(),
	}

	err = repo.WeeklyPlan.Create(ctx, weeklyPlan)
	if err != nil {
		logger.WithError(err).Error("Failed to create weekly plan")
		return
	}

	logger.WithField("weekly_plan_id", weeklyPlan.WeeklyPlanID).Info("Weekly plan created successfully")

	// Example: Health check
	err = dbManager.Health(ctx)
	if err != nil {
		logger.WithError(err).Error("Database health check failed")
		return
	}

	logger.Info("Database health check passed")

	// Example: Get database stats
	stats := dbManager.Stats()
	logger.WithField("stats", stats).Info("Database connection statistics")
}

// ExampleMigrationUsage demonstrates how to use the migration system
func ExampleMigrationUsage() {
	// Initialize logger
	logger := logrus.New()

	// Database configuration
	config := &Config{
		Host:     "localhost",
		Port:     5432,
		User:     "postgres",
		Password: "password",
		Database: "noumidb",
		SSLMode:  "disable",
	}

	// Create database connection
	db, err := NewConnection(config, logger)
	if err != nil {
		logger.WithError(err).Fatal("Failed to create database connection")
		return
	}
	defer db.Close()

	// Create migrator
	migrator := NewMigrator(db.DB, logger, "internal/database/migrations")

	// Example: Get current migration version
	version, dirty, err := migrator.GetCurrentVersion()
	if err != nil {
		logger.WithError(err).Info("No migrations applied yet")
	} else {
		logger.WithFields(logrus.Fields{
			"version": version,
			"dirty":   dirty,
		}).Info("Current migration status")
	}

	// Example: Run all pending migrations
	err = migrator.RunMigrations()
	if err != nil {
		logger.WithError(err).Error("Failed to run migrations")
		return
	}

	logger.Info("Migrations completed successfully")

	// Example: Get version after migration
	version, dirty, err = migrator.GetCurrentVersion()
	if err != nil {
		logger.WithError(err).Error("Failed to get version after migration")
		return
	}

	logger.WithFields(logrus.Fields{
		"version": version,
		"dirty":   dirty,
	}).Info("Migration status after running migrations")

	// Example: Migrate to a specific version (rollback)
	if version > 0 {
		logger.Info("Demonstrating rollback to previous version")
		err = migrator.MigrateToVersion(version - 1)
		if err != nil {
			logger.WithError(err).Error("Failed to rollback migration")
			return
		}

		// Get version after rollback
		newVersion, _, err := migrator.GetCurrentVersion()
		if err != nil {
			logger.WithError(err).Error("Failed to get version after rollback")
			return
		}

		logger.WithFields(logrus.Fields{
			"from_version": version,
			"to_version":   newVersion,
		}).Info("Rollback completed")

		// Migrate back up
		err = migrator.RunMigrations()
		if err != nil {
			logger.WithError(err).Error("Failed to migrate back up")
			return
		}

		logger.Info("Migrated back to latest version")
	}
}

// ExampleDatabaseManagerWithMigrations demonstrates the full database manager usage with migrations
func ExampleDatabaseManagerWithMigrations() {
	// Initialize logger
	logger := logrus.New()

	// Database configuration
	config := &Config{
		Host:     "localhost",
		Port:     5432,
		User:     "postgres",
		Password: "password",
		Database: "noumidb",
		SSLMode:  "disable",
	}

	// Create database manager
	dbManager, err := NewManager(config, logger)
	if err != nil {
		logger.WithError(err).Fatal("Failed to create database manager")
		return
	}
	defer dbManager.Close()

	// Initialize database (this runs migrations automatically)
	err = dbManager.Initialize()
	if err != nil {
		logger.WithError(err).Fatal("Failed to initialize database")
		return
	}

	// Get migrator for additional migration operations
	migrator := dbManager.GetMigrator()

	// Check migration status
	version, dirty, err := migrator.GetCurrentVersion()
	if err != nil {
		logger.WithError(err).Error("Failed to get migration version")
		return
	}

	logger.WithFields(logrus.Fields{
		"version": version,
		"dirty":   dirty,
	}).Info("Database is ready with migrations applied")

	// Now you can use the repository layer
	repo := dbManager.GetRepository()
	ctx := context.Background()

	// Example: Verify tables exist by trying to query
	// This would fail if migrations didn't run properly
	user, err := repo.User.GetByID(ctx, 1)
	if err != nil {
		logger.WithError(err).Info("No user with ID 1 found (expected for empty database)")
	} else {
		logger.WithField("user_id", user.UserID).Info("Found existing user")
	}

	logger.Info("Database manager with migrations working correctly")
}
