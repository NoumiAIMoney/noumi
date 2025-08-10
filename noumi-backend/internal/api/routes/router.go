package routes

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"

	"noumi-backend/internal/api/handlers"
	"noumi-backend/internal/api/middleware"
	"noumi-backend/internal/config"
	"noumi-backend/internal/database"
	"noumi-backend/internal/database/repository"
)

// RouterConfig holds dependencies needed for router setup
type RouterConfig struct {
	Config    *config.Config
	Logger    *logrus.Logger
	DBManager *database.Manager
}

// SetupRouter configures and returns a Gin router with all middleware
func SetupRouter(cfg *RouterConfig) *gin.Engine {
	// Set Gin mode based on log level
	if cfg.Config.Logging.Level == "debug" {
		gin.SetMode(gin.DebugMode)
	} else {
		gin.SetMode(gin.ReleaseMode)
	}

	// Create Gin router
	router := gin.New()

	// Add middleware in the correct order
	setupMiddleware(router, cfg)

	// Setup routes
	setupRoutes(router, cfg)

	return router
}

// setupMiddleware configures all middleware for the router
func setupMiddleware(router *gin.Engine, cfg *RouterConfig) {
	// 1. Request ID middleware (must be first to generate request IDs)
	router.Use(middleware.RequestIDMiddleware())

	// 2. Recovery middleware (should be early to catch panics)
	router.Use(middleware.RecoveryMiddleware(cfg.Logger))

	// 3. CORS middleware (should be early for preflight requests)
	router.Use(middleware.CORSMiddleware())

	// 4. Structured logging middleware
	router.Use(middleware.LoggingMiddleware(cfg.Logger))

	// 5. Error handling middleware (should be last to catch all errors)
	router.Use(middleware.ErrorHandlerMiddleware(cfg.Logger))
}

// setupRoutes configures all routes for the application
func setupRoutes(router *gin.Engine, cfg *RouterConfig) {
	// Health check endpoint (no authentication required)
	router.GET("/health", healthCheckHandler(cfg.DBManager))

	// API version 1 routes
	v1 := router.Group("/api/v1")
	{
		// Public endpoints (no authentication required)
		setupPublicRoutes(v1, cfg)

		// Protected endpoints (authentication required)
		setupProtectedRoutes(v1, cfg)
	}

	// Swagger documentation endpoints (no authentication required)
	router.GET("/docs/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))
	router.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

	// Legacy docs endpoint for backward compatibility
	router.GET("/docs", func(c *gin.Context) {
		c.Redirect(http.StatusMovedPermanently, "/docs/index.html")
	})
}

// setupPublicRoutes configures routes that don't require authentication
func setupPublicRoutes(rg *gin.RouterGroup, cfg *RouterConfig) {
	// Status endpoint
	rg.GET("/status", statusHandler(cfg.DBManager))

	// Authentication endpoints (will be implemented in future tasks)
	auth := rg.Group("/auth")
	{
		auth.POST("/login", func(c *gin.Context) {
			c.JSON(http.StatusNotImplemented, gin.H{
				"message": "Login endpoint not yet implemented",
			})
		})
		auth.POST("/register", func(c *gin.Context) {
			c.JSON(http.StatusNotImplemented, gin.H{
				"message": "Register endpoint not yet implemented",
			})
		})
		auth.POST("/refresh", func(c *gin.Context) {
			c.JSON(http.StatusNotImplemented, gin.H{
				"message": "Token refresh endpoint not yet implemented",
			})
		})
	}
}

// setupProtectedRoutes configures routes that require authentication
func setupProtectedRoutes(rg *gin.RouterGroup, cfg *RouterConfig) {
	// Apply authentication middleware to protected routes
	protected := rg.Group("")
	protected.Use(middleware.AuthMiddleware(cfg.Config.Auth.JWTSecret, cfg.Logger))

	// Initialize repositories
	repo := repository.NewRepository(cfg.DBManager.GetDB().DB)

	// Initialize handlers
	quizHandler := handlers.NewQuizHandler(repo.Goal, cfg.Logger)

	// Quiz endpoint
	protected.POST("/quiz", quizHandler.SubmitQuiz)

	// Plaid endpoints
	plaid := protected.Group("/plaid")
	{
		plaid.POST("/connect", func(c *gin.Context) {
			c.JSON(http.StatusNotImplemented, gin.H{
				"message": "Plaid connect endpoint not yet implemented",
			})
		})
	}

	// Analytics endpoints
	analytics := protected.Group("")
	{
		analytics.GET("/anomalies/yearly", func(c *gin.Context) {
			c.JSON(http.StatusNotImplemented, gin.H{
				"message": "Yearly anomalies endpoint not yet implemented",
			})
		})
		analytics.POST("/transactions/:id/anomaly", func(c *gin.Context) {
			c.JSON(http.StatusNotImplemented, gin.H{
				"message": "Transaction anomaly detection endpoint not yet implemented",
			})
		})
	}

	// Spending endpoints
	spending := protected.Group("/spending")
	{
		spending.GET("/categories", func(c *gin.Context) {
			c.JSON(http.StatusNotImplemented, gin.H{
				"message": "Spending categories endpoint not yet implemented",
			})
		})
		spending.GET("/status", func(c *gin.Context) {
			c.JSON(http.StatusNotImplemented, gin.H{
				"message": "Spending status endpoint not yet implemented",
			})
		})
		spending.GET("/total", func(c *gin.Context) {
			c.JSON(http.StatusNotImplemented, gin.H{
				"message": "Total spending endpoint not yet implemented",
			})
		})
	}

	// Trends endpoint
	protected.GET("/trends", func(c *gin.Context) {
		c.JSON(http.StatusNotImplemented, gin.H{
			"message": "Trends endpoint not yet implemented",
		})
	})

	// Goal endpoints
	goal := protected.Group("/goal")
	{
		goal.GET("/computed", func(c *gin.Context) {
			c.JSON(http.StatusNotImplemented, gin.H{
				"message": "Computed goal endpoint not yet implemented",
			})
		})
	}

	// Habits endpoint
	protected.GET("/habits", func(c *gin.Context) {
		c.JSON(http.StatusNotImplemented, gin.H{
			"message": "Habits endpoint not yet implemented",
		})
	})

	// Savings endpoints
	savings := protected.Group("/savings")
	{
		savings.GET("/weekly", func(c *gin.Context) {
			c.JSON(http.StatusNotImplemented, gin.H{
				"message": "Weekly savings endpoint not yet implemented",
			})
		})
	}

	// Streak endpoints
	streak := protected.Group("/streak")
	{
		streak.GET("/longest", func(c *gin.Context) {
			c.JSON(http.StatusNotImplemented, gin.H{
				"message": "Longest streak endpoint not yet implemented",
			})
		})
		streak.GET("/weekly", func(c *gin.Context) {
			c.JSON(http.StatusNotImplemented, gin.H{
				"message": "Weekly streak endpoint not yet implemented",
			})
		})
	}
}

// healthCheckHandler handles the health check endpoint
func healthCheckHandler(dbManager *database.Manager) gin.HandlerFunc {
	return func(c *gin.Context) {
		// Handle case where dbManager is nil (for testing)
		if dbManager == nil {
			c.JSON(http.StatusServiceUnavailable, gin.H{
				"status":    "unhealthy",
				"timestamp": time.Now().UTC().Format(time.RFC3339),
				"service":   "noumi-backend",
				"error":     "database manager not initialized",
			})
			return
		}

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
	}
}

// statusHandler handles the status endpoint
func statusHandler(dbManager *database.Manager) gin.HandlerFunc {
	return func(c *gin.Context) {
		response := gin.H{
			"message": "Noumi Backend API is running",
			"version": "1.0.0",
		}

		// Handle case where dbManager is nil (for testing)
		if dbManager == nil {
			response["database"] = "not initialized"
			response["migration"] = gin.H{"error": "database manager not available"}
			c.JSON(http.StatusOK, response)
			return
		}

		// Get database stats
		dbStats := dbManager.Stats()
		response["database"] = dbStats

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
		response["migration"] = migrationInfo

		c.JSON(http.StatusOK, response)
	}
}
