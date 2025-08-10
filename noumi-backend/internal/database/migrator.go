package database

import (
	"database/sql"
	"fmt"
	"path/filepath"

	"github.com/golang-migrate/migrate/v4"
	"github.com/golang-migrate/migrate/v4/database/postgres"
	_ "github.com/golang-migrate/migrate/v4/source/file"
	"github.com/sirupsen/logrus"
)

// Migrator handles database migrations
type Migrator struct {
	db            *sql.DB
	logger        *logrus.Logger
	migrationsDir string
}

// NewMigrator creates a new migrator instance
func NewMigrator(db *sql.DB, logger *logrus.Logger, migrationsDir string) *Migrator {
	return &Migrator{
		db:            db,
		logger:        logger,
		migrationsDir: migrationsDir,
	}
}

// RunMigrations executes all pending migrations
func (m *Migrator) RunMigrations() error {
	m.logger.Info("Starting database migrations")

	// Create postgres driver instance
	driver, err := postgres.WithInstance(m.db, &postgres.Config{})
	if err != nil {
		return fmt.Errorf("failed to create postgres driver: %w", err)
	}

	// Get absolute path to migrations directory
	migrationsPath, err := filepath.Abs(m.migrationsDir)
	if err != nil {
		return fmt.Errorf("failed to get absolute path for migrations: %w", err)
	}

	// Create migrate instance
	migrator, err := migrate.NewWithDatabaseInstance(
		fmt.Sprintf("file://%s", migrationsPath),
		"postgres",
		driver,
	)
	if err != nil {
		return fmt.Errorf("failed to create migrator: %w", err)
	}
	// Note: We don't close the migrator here because it would close the shared database connection

	// Get current version
	currentVersion, dirty, err := migrator.Version()
	if err != nil && err != migrate.ErrNilVersion {
		return fmt.Errorf("failed to get current migration version: %w", err)
	}

	if dirty {
		m.logger.WithField("version", currentVersion).Warn("Database is in dirty state, attempting to force version")
		if err := migrator.Force(int(currentVersion)); err != nil {
			return fmt.Errorf("failed to force migration version: %w", err)
		}
	}

	m.logger.WithField("current_version", currentVersion).Info("Current migration version")

	// Run migrations
	err = migrator.Up()
	if err != nil && err != migrate.ErrNoChange {
		return fmt.Errorf("failed to run migrations: %w", err)
	}

	// Get new version after migration
	newVersion, _, err := migrator.Version()
	if err != nil && err != migrate.ErrNilVersion {
		return fmt.Errorf("failed to get new migration version: %w", err)
	}

	if err == migrate.ErrNoChange {
		m.logger.Info("No new migrations to apply")
	} else {
		m.logger.WithFields(logrus.Fields{
			"from_version": currentVersion,
			"to_version":   newVersion,
		}).Info("Migrations completed successfully")
	}

	return nil
}

// RollbackMigration rolls back the last migration
func (m *Migrator) RollbackMigration() error {
	m.logger.Info("Rolling back last migration")

	// Create postgres driver instance
	driver, err := postgres.WithInstance(m.db, &postgres.Config{})
	if err != nil {
		return fmt.Errorf("failed to create postgres driver: %w", err)
	}

	// Get absolute path to migrations directory
	migrationsPath, err := filepath.Abs(m.migrationsDir)
	if err != nil {
		return fmt.Errorf("failed to get absolute path for migrations: %w", err)
	}

	// Create migrate instance
	migrator, err := migrate.NewWithDatabaseInstance(
		fmt.Sprintf("file://%s", migrationsPath),
		"postgres",
		driver,
	)
	if err != nil {
		return fmt.Errorf("failed to create migrator: %w", err)
	}
	defer migrator.Close()

	// Get current version
	currentVersion, dirty, err := migrator.Version()
	if err != nil {
		if err == migrate.ErrNilVersion {
			m.logger.Info("No migrations to rollback")
			return nil
		}
		return fmt.Errorf("failed to get current migration version: %w", err)
	}

	if dirty {
		return fmt.Errorf("database is in dirty state, cannot rollback")
	}

	// Rollback one step
	err = migrator.Steps(-1)
	if err != nil {
		return fmt.Errorf("failed to rollback migration: %w", err)
	}

	m.logger.WithField("from_version", currentVersion).Info("Migration rollback completed")
	return nil
}

// GetCurrentVersion returns the current migration version
func (m *Migrator) GetCurrentVersion() (uint, bool, error) {
	// Create postgres driver instance
	driver, err := postgres.WithInstance(m.db, &postgres.Config{})
	if err != nil {
		return 0, false, fmt.Errorf("failed to create postgres driver: %w", err)
	}

	// Get absolute path to migrations directory
	migrationsPath, err := filepath.Abs(m.migrationsDir)
	if err != nil {
		return 0, false, fmt.Errorf("failed to get absolute path for migrations: %w", err)
	}

	// Create migrate instance
	migrator, err := migrate.NewWithDatabaseInstance(
		fmt.Sprintf("file://%s", migrationsPath),
		"postgres",
		driver,
	)
	if err != nil {
		return 0, false, fmt.Errorf("failed to create migrator: %w", err)
	}
	defer migrator.Close()

	return migrator.Version()
}

// MigrateToVersion migrates to a specific version
func (m *Migrator) MigrateToVersion(version uint) error {
	m.logger.WithField("target_version", version).Info("Migrating to specific version")

	// Create postgres driver instance
	driver, err := postgres.WithInstance(m.db, &postgres.Config{})
	if err != nil {
		return fmt.Errorf("failed to create postgres driver: %w", err)
	}

	// Get absolute path to migrations directory
	migrationsPath, err := filepath.Abs(m.migrationsDir)
	if err != nil {
		return fmt.Errorf("failed to get absolute path for migrations: %w", err)
	}

	// Create migrate instance
	migrator, err := migrate.NewWithDatabaseInstance(
		fmt.Sprintf("file://%s", migrationsPath),
		"postgres",
		driver,
	)
	if err != nil {
		return fmt.Errorf("failed to create migrator: %w", err)
	}
	defer migrator.Close()

	// Migrate to specific version
	err = migrator.Migrate(version)
	if err != nil && err != migrate.ErrNoChange {
		return fmt.Errorf("failed to migrate to version %d: %w", version, err)
	}

	if err == migrate.ErrNoChange {
		m.logger.WithField("version", version).Info("Already at target version")
	} else {
		m.logger.WithField("version", version).Info("Migration to version completed")
	}

	return nil
}

// DropDatabase drops all tables and schema (use with caution)
func (m *Migrator) DropDatabase() error {
	m.logger.Warn("Dropping all database tables and schema")

	// Create postgres driver instance
	driver, err := postgres.WithInstance(m.db, &postgres.Config{})
	if err != nil {
		return fmt.Errorf("failed to create postgres driver: %w", err)
	}

	// Get absolute path to migrations directory
	migrationsPath, err := filepath.Abs(m.migrationsDir)
	if err != nil {
		return fmt.Errorf("failed to get absolute path for migrations: %w", err)
	}

	// Create migrate instance
	migrator, err := migrate.NewWithDatabaseInstance(
		fmt.Sprintf("file://%s", migrationsPath),
		"postgres",
		driver,
	)
	if err != nil {
		return fmt.Errorf("failed to create migrator: %w", err)
	}
	defer migrator.Close()

	// Drop everything
	err = migrator.Drop()
	if err != nil {
		return fmt.Errorf("failed to drop database: %w", err)
	}

	m.logger.Info("Database dropped successfully")
	return nil
}
