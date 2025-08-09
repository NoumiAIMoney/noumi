package database

import (
	"context"
	"database/sql"
	"fmt"
	"path/filepath"
	"time"

	"noumi-backend/internal/database/repository"

	"github.com/sirupsen/logrus"
)

// Manager manages database connections and repositories
type Manager struct {
	db         *DB
	repository *repository.Repository
	migrator   *Migrator
	logger     *logrus.Logger
}

// NewManager creates a new database manager
func NewManager(config *Config, logger *logrus.Logger) (*Manager, error) {
	// Create database connection
	db, err := NewConnection(config, logger)
	if err != nil {
		return nil, fmt.Errorf("failed to create database connection: %w", err)
	}

	// Create migrator with migrations directory
	migrationsDir := filepath.Join("internal", "database", "migrations")
	migrator := NewMigrator(db.DB, logger, migrationsDir)

	// Create repository layer
	repo := repository.NewRepository(db.DB)

	return &Manager{
		db:         db,
		repository: repo,
		migrator:   migrator,
		logger:     logger,
	}, nil
}

// GetRepository returns the repository instance
func (m *Manager) GetRepository() *repository.Repository {
	return m.repository
}

// GetDB returns the database connection
func (m *Manager) GetDB() *DB {
	return m.db
}

// GetMigrator returns the migrator instance
func (m *Manager) GetMigrator() *Migrator {
	return m.migrator
}

// RunMigrations executes all pending database migrations
func (m *Manager) RunMigrations() error {
	if m.migrator == nil {
		return fmt.Errorf("migrator is not initialized")
	}
	return m.migrator.RunMigrations()
}

// Initialize performs initial setup including running migrations
func (m *Manager) Initialize() error {
	m.logger.Info("Initializing database manager")

	// Run migrations first
	if err := m.RunMigrations(); err != nil {
		return fmt.Errorf("failed to run migrations: %w", err)
	}

	// Verify database health after migrations
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := m.Health(ctx); err != nil {
		return fmt.Errorf("database health check failed after migrations: %w", err)
	}

	m.logger.Info("Database manager initialized successfully")
	return nil
}

// Close closes the database connection
func (m *Manager) Close() error {
	if m.db != nil {
		return m.db.Close()
	}
	return nil
}

// Health checks the database health
func (m *Manager) Health(ctx context.Context) error {
	if m.db == nil {
		return fmt.Errorf("database connection is nil")
	}

	// Create a context with timeout for health check
	healthCtx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()

	return m.db.PingContext(healthCtx)
}

// Stats returns database connection statistics
func (m *Manager) Stats() interface{} {
	if m.db == nil {
		return nil
	}

	stats := m.db.Stats()
	return map[string]interface{}{
		"max_open_connections": stats.MaxOpenConnections,
		"open_connections":     stats.OpenConnections,
		"in_use":               stats.InUse,
		"idle":                 stats.Idle,
		"wait_count":           stats.WaitCount,
		"wait_duration":        stats.WaitDuration.String(),
		"max_idle_closed":      stats.MaxIdleClosed,
		"max_idle_time_closed": stats.MaxIdleTimeClosed,
		"max_lifetime_closed":  stats.MaxLifetimeClosed,
	}
}

// Ping pings the database to verify connectivity
func (m *Manager) Ping(ctx context.Context) error {
	if m.db == nil {
		return fmt.Errorf("database connection is nil")
	}
	return m.db.PingContext(ctx)
}

// BeginTx starts a new database transaction
func (m *Manager) BeginTx(ctx context.Context) (*Tx, error) {
	if m.db == nil {
		return nil, fmt.Errorf("database connection is nil")
	}

	sqlTx, err := m.db.BeginTx(ctx, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to begin transaction: %w", err)
	}

	return &Tx{
		Tx:     sqlTx,
		logger: m.logger,
	}, nil
}

// Tx wraps sql.Tx with additional functionality
type Tx struct {
	*sql.Tx
	logger *logrus.Logger
}

// Commit commits the transaction
func (tx *Tx) Commit() error {
	err := tx.Tx.Commit()
	if err != nil {
		tx.logger.WithError(err).Error("Failed to commit transaction")
		return fmt.Errorf("failed to commit transaction: %w", err)
	}
	tx.logger.Debug("Transaction committed successfully")
	return nil
}

// Rollback rolls back the transaction
func (tx *Tx) Rollback() error {
	err := tx.Tx.Rollback()
	if err != nil {
		tx.logger.WithError(err).Error("Failed to rollback transaction")
		return fmt.Errorf("failed to rollback transaction: %w", err)
	}
	tx.logger.Debug("Transaction rolled back successfully")
	return nil
}
