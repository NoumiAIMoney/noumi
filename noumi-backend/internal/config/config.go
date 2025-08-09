package config

import (
	"fmt"
	"time"

	"github.com/kelseyhightower/envconfig"
)

// Config holds all configuration for the application
type Config struct {
	Server struct {
		Port         string        `envconfig:"PORT" default:"8080"`
		Host         string        `envconfig:"HOST" default:"0.0.0.0"`
		ReadTimeout  time.Duration `envconfig:"READ_TIMEOUT" default:"30s"`
		WriteTimeout time.Duration `envconfig:"WRITE_TIMEOUT" default:"30s"`
	}

	Database struct {
		URL             string        `envconfig:"DATABASE_URL" default:"postgres://localhost/noumidb?sslmode=disable"`
		MaxOpenConns    int           `envconfig:"DB_MAX_OPEN_CONNS" default:"25"`
		MaxIdleConns    int           `envconfig:"DB_MAX_IDLE_CONNS" default:"5"`
		ConnMaxLifetime time.Duration `envconfig:"DB_CONN_MAX_LIFETIME" default:"5m"`
	}

	OpenAI struct {
		APIKey      string  `envconfig:"OPENAI_API_KEY"`
		Model       string  `envconfig:"OPENAI_MODEL" default:"gpt-4"`
		MaxTokens   int     `envconfig:"OPENAI_MAX_TOKENS" default:"1000"`
		Temperature float32 `envconfig:"OPENAI_TEMPERATURE" default:"0.7"`
	}

	Auth struct {
		JWTSecret     string        `envconfig:"JWT_SECRET" required:"true"`
		TokenExpiry   time.Duration `envconfig:"TOKEN_EXPIRY" default:"24h"`
		RefreshExpiry time.Duration `envconfig:"REFRESH_EXPIRY" default:"168h"`
	}

	Logging struct {
		Level  string `envconfig:"LOG_LEVEL" default:"info"`
		Format string `envconfig:"LOG_FORMAT" default:"json"`
	}
}

// Load loads configuration from environment variables
func Load() (*Config, error) {
	var cfg Config

	if err := envconfig.Process("", &cfg); err != nil {
		return nil, fmt.Errorf("failed to load configuration: %w", err)
	}

	// Validate required fields
	if cfg.Auth.JWTSecret == "" {
		return nil, fmt.Errorf("JWT_SECRET is required")
	}

	return &cfg, nil
}

// GetServerAddress returns the full server address
func (c *Config) GetServerAddress() string {
	return fmt.Sprintf("%s:%s", c.Server.Host, c.Server.Port)
}
