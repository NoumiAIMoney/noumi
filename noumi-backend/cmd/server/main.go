package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"

	"noumi-backend/internal/config"
	"noumi-backend/internal/database"
	"noumi-backend/internal/utils/logger"
)

func main() {
	// Load .env file if it exists (for development)
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found, using environment variables")
	}

	// Load configuration
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("Failed to load configuration: %v", err)
	}

	// Initialize logger
	logger := logger.New(cfg.Logging.Level, cfg.Logging.Format)
	logger.Info("Starting Noumi Backend Server")

	// Convert config to database config
	dbConfig := &database.Config{
		URL:             cfg.Database.URL,
		MaxOpenConns:    cfg.Database.MaxOpenConns,
		MaxIdleConns:    cfg.Database.MaxIdleConns,
		ConnMaxLifetime: cfg.Database.ConnMaxLifetime,
		ConnMaxIdleTime: cfg.Database.ConnMaxLifetime, // Use same value for idle time
	}

	// Initialize database manager
	dbManager, err := database.NewManager(dbConfig, logger.Logger)
	if err != nil {
		logger.Fatalf("Failed to create database manager: %v", err)
	}
	defer dbManager.Close()

	// Initialize database (run migrations)
	if err := dbManager.Initialize(); err != nil {
		logger.Fatalf("Failed to initialize database: %v", err)
	}

	// Set Gin mode based on log level
	if cfg.Logging.Level == "debug" {
		gin.SetMode(gin.DebugMode)
	} else {
		gin.SetMode(gin.ReleaseMode)
	}

	// Create Gin router
	router := gin.New()

	// Add basic middleware
	router.Use(gin.Logger())
	router.Use(gin.Recovery())

	// Health check endpoint
	router.GET("/health", func(c *gin.Context) {
		// Check database health
		if err := dbManager.Health(c.Request.Context()); err != nil {
			c.JSON(http.StatusServiceUnavailable, gin.H{
				"status":    "unhealthy",
				"timestamp": time.Now().UTC().Format(time.RFC3339),
				"service":   "noumi-backend",
				"error":     "database connection failed",
			})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"status":    "healthy",
			"timestamp": time.Now().UTC().Format(time.RFC3339),
			"service":   "noumi-backend",
			"database":  "connected",
		})
	})

	// Basic API route group
	api := router.Group("/api/v1")
	{
		api.GET("/status", func(c *gin.Context) {
			// Get database stats
			dbStats := dbManager.Stats()

			// Get current migration version
			migrator := dbManager.GetMigrator()
			version, dirty, err := migrator.GetCurrentVersion()
			migrationInfo := gin.H{
				"version": version,
				"dirty":   dirty,
			}
			if err != nil {
				migrationInfo["error"] = err.Error()
			}

			c.JSON(http.StatusOK, gin.H{
				"message":   "Noumi Backend API is running",
				"version":   "1.0.0",
				"database":  dbStats,
				"migration": migrationInfo,
			})
		})
	}

	// Create HTTP server
	server := &http.Server{
		Addr:         cfg.GetServerAddress(),
		Handler:      router,
		ReadTimeout:  cfg.Server.ReadTimeout,
		WriteTimeout: cfg.Server.WriteTimeout,
	}

	// Start server in a goroutine
	go func() {
		logger.Infof("Server starting on %s", cfg.GetServerAddress())
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Fatalf("Failed to start server: %v", err)
		}
	}()

	// Wait for interrupt signal to gracefully shutdown the server
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	logger.Info("Shutting down server...")

	// Create a context with timeout for graceful shutdown
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// Shutdown server
	if err := server.Shutdown(ctx); err != nil {
		logger.Fatalf("Server forced to shutdown: %v", err)
	}

	logger.Info("Server exited")
}
