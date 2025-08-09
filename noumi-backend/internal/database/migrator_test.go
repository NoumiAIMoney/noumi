package database

import (
	"database/sql"
	"os"
	"path/filepath"
	"testing"

	_ "github.com/lib/pq"
	"github.com/sirupsen/logrus"
)

func TestMigrator(t *testing.T) {
	// Skip if no test database URL is provided
	testDBURL := os.Getenv("TEST_DATABASE_URL")
	if testDBURL == "" {
		t.Skip("TEST_DATABASE_URL not set, skipping integration test")
	}

	// Create test logger
	logger := logrus.New()
	logger.SetLevel(logrus.DebugLevel)

	// Connect to test database
	db, err := sql.Open("postgres", testDBURL)
	if err != nil {
		t.Fatalf("Failed to connect to test database: %v", err)
	}
	defer db.Close()

	// Test database connection
	if err := db.Ping(); err != nil {
		t.Fatalf("Failed to ping test database: %v", err)
	}

	// Get migrations directory
	migrationsDir := filepath.Join("migrations")

	// Create migrator
	migrator := NewMigrator(db, logger, migrationsDir)

	// Test getting current version (should be nil for empty database)
	version, dirty, err := migrator.GetCurrentVersion()
	if err != nil && err.Error() != "no migration" {
		t.Logf("Current version: %d, dirty: %t, error: %v", version, dirty, err)
	}

	// Test running migrations
	err = migrator.RunMigrations()
	if err != nil {
		t.Fatalf("Failed to run migrations: %v", err)
	}

	// Test getting version after migration
	version, dirty, err = migrator.GetCurrentVersion()
	if err != nil {
		t.Fatalf("Failed to get version after migration: %v", err)
	}

	if dirty {
		t.Errorf("Database is in dirty state after migration")
	}

	t.Logf("Migration completed successfully. Current version: %d", version)

	// Clean up - drop all tables
	err = migrator.DropDatabase()
	if err != nil {
		t.Fatalf("Failed to drop database: %v", err)
	}

	t.Log("Database cleanup completed")
}

func TestMigratorWithInvalidPath(t *testing.T) {
	// Create test logger
	logger := logrus.New()
	logger.SetLevel(logrus.DebugLevel)

	// Skip this test as it requires a real database connection
	// The migrator needs a valid database connection to work
	t.Skip("Skipping invalid path test - requires real database connection")
}
