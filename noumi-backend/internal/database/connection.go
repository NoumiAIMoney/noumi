package database

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	_ "github.com/lib/pq" // PostgreSQL driver
	"github.com/sirupsen/logrus"
)

// Config holds database configuration
type Config struct {
	// URL takes precedence over individual parameters
	URL             string        `env:"DATABASE_URL"`
	Host            string        `env:"DB_HOST" envDefault:"localhost"`
	Port            int           `env:"DB_PORT" envDefault:"5432"`
	User            string        `env:"DB_USER" envDefault:"postgres"`
	Password        string        `env:"DB_PASSWORD" envDefault:""`
	Database        string        `env:"DB_NAME" envDefault:"noumidb"`
	SSLMode         string        `env:"DB_SSL_MODE" envDefault:"disable"`
	MaxOpenConns    int           `env:"DB_MAX_OPEN_CONNS" envDefault:"25"`
	MaxIdleConns    int           `env:"DB_MAX_IDLE_CONNS" envDefault:"5"`
	ConnMaxLifetime time.Duration `env:"DB_CONN_MAX_LIFETIME" envDefault:"5m"`
	ConnMaxIdleTime time.Duration `env:"DB_CONN_MAX_IDLE_TIME" envDefault:"5m"`
}

// DB wraps the sql.DB connection with additional functionality
type DB struct {
	*sql.DB
	config *Config
	logger *logrus.Logger
}

// NewConnection creates a new database connection with connection pooling
func NewConnection(config *Config, logger *logrus.Logger) (*DB, error) {
	var dsn string

	// Use URL if provided, otherwise build from individual parameters
	if config.URL != "" {
		dsn = config.URL
	} else {
		dsn = fmt.Sprintf(
			"host=%s port=%d user=%s password=%s dbname=%s sslmode=%s",
			config.Host,
			config.Port,
			config.User,
			config.Password,
			config.Database,
			config.SSLMode,
		)
	}

	// Open database connection
	sqlDB, err := sql.Open("postgres", dsn)
	if err != nil {
		return nil, fmt.Errorf("failed to open database connection: %w", err)
	}

	// Configure connection pool
	sqlDB.SetMaxOpenConns(config.MaxOpenConns)
	sqlDB.SetMaxIdleConns(config.MaxIdleConns)
	sqlDB.SetConnMaxLifetime(config.ConnMaxLifetime)
	sqlDB.SetConnMaxIdleTime(config.ConnMaxIdleTime)

	// Test the connection
	if err := sqlDB.Ping(); err != nil {
		sqlDB.Close()
		return nil, fmt.Errorf("failed to ping database: %w", err)
	}

	db := &DB{
		DB:     sqlDB,
		config: config,
		logger: logger,
	}

	logger.WithFields(logrus.Fields{
		"host":     config.Host,
		"port":     config.Port,
		"database": config.Database,
	}).Info("Database connection established")

	return db, nil
}

// Close closes the database connection
func (db *DB) Close() error {
	if db.DB != nil {
		db.logger.Info("Closing database connection")
		return db.DB.Close()
	}
	return nil
}

// Health checks the database connection health
func (db *DB) Health() error {
	if db.DB == nil {
		return fmt.Errorf("database connection is nil")
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	return db.PingContext(ctx)
}

// Stats returns database connection statistics
func (db *DB) Stats() sql.DBStats {
	if db.DB == nil {
		return sql.DBStats{}
	}
	return db.DB.Stats()
}

// GetConfig returns the database configuration
func (db *DB) GetConfig() *Config {
	return db.config
}
