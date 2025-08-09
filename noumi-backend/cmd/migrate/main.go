package main

import (
	"flag"
	"fmt"
	"strconv"

	"noumi-backend/internal/config"
	"noumi-backend/internal/database"

	"github.com/sirupsen/logrus"
)

func main() {
	var (
		action  = flag.String("action", "up", "Migration action: up, down, version, drop, force")
		version = flag.String("version", "", "Target version for migrate action or force version")
	)
	flag.Parse()

	// Initialize logger
	logger := logrus.New()
	logger.SetLevel(logrus.InfoLevel)
	logger.SetFormatter(&logrus.TextFormatter{
		FullTimestamp: true,
	})

	// Load configuration
	cfg, err := config.Load()
	if err != nil {
		logger.WithError(err).Fatal("Failed to load configuration")
	}

	// Convert config to database config
	dbConfig := &database.Config{
		URL:             cfg.Database.URL,
		MaxOpenConns:    cfg.Database.MaxOpenConns,
		MaxIdleConns:    cfg.Database.MaxIdleConns,
		ConnMaxLifetime: cfg.Database.ConnMaxLifetime,
		ConnMaxIdleTime: cfg.Database.ConnMaxLifetime,
	}

	// Create database connection
	db, err := database.NewConnection(dbConfig, logger)
	if err != nil {
		logger.WithError(err).Fatal("Failed to connect to database")
	}
	defer db.Close()

	// Create migrator
	migrator := database.NewMigrator(db.DB, logger, "internal/database/migrations")

	// Execute migration action
	switch *action {
	case "up":
		if *version != "" {
			// Migrate to specific version
			v, err := strconv.ParseUint(*version, 10, 32)
			if err != nil {
				logger.WithError(err).Fatal("Invalid version number")
			}
			if err := migrator.MigrateToVersion(uint(v)); err != nil {
				logger.WithError(err).Fatal("Failed to migrate to version")
			}
		} else {
			// Migrate up (all pending migrations)
			if err := migrator.RunMigrations(); err != nil {
				logger.WithError(err).Fatal("Failed to run migrations")
			}
		}

	case "down":
		// Rollback migration
		if err := migrator.RollbackMigration(); err != nil {
			logger.WithError(err).Fatal("Failed to rollback migration")
		}

	case "version":
		// Get current version
		currentVersion, dirty, err := migrator.GetCurrentVersion()
		if err != nil {
			logger.WithError(err).Fatal("Failed to get current version")
		}
		fmt.Printf("Current version: %d\n", currentVersion)
		fmt.Printf("Dirty: %t\n", dirty)

	case "drop":
		// Drop all tables (dangerous!)
		fmt.Print("Are you sure you want to drop all tables? This action cannot be undone. (yes/no): ")
		var confirmation string
		fmt.Scanln(&confirmation)
		if confirmation == "yes" {
			if err := migrator.DropDatabase(); err != nil {
				logger.WithError(err).Fatal("Failed to drop database")
			}
			logger.Info("Database dropped successfully")
		} else {
			logger.Info("Operation cancelled")
		}

	case "force":
		// Force version (use when migrations are in dirty state)
		if *version == "" {
			logger.Fatal("Version is required for force action")
		}
		v, err := strconv.ParseUint(*version, 10, 32)
		if err != nil {
			logger.WithError(err).Fatal("Invalid version number")
		}

		// This requires direct access to the migrate instance
		logger.WithField("version", v).Warn("Forcing migration version - use with caution")
		// Note: Force functionality would need to be added to the Migrator struct
		logger.Info("Force version functionality needs to be implemented in migrator")

	default:
		logger.WithField("action", *action).Fatal("Unknown migration action")
	}

	logger.Info("Migration operation completed successfully")
}
