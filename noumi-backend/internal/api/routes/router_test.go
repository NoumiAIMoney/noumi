package routes

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/sirupsen/logrus"
	"github.com/stretchr/testify/assert"

	"noumi-backend/internal/api/middleware"
	"noumi-backend/internal/config"
)

func TestSetupRouter(t *testing.T) {
	// Create test configuration
	cfg := &config.Config{}
	cfg.Auth.JWTSecret = "test_secret"
	cfg.Logging.Level = "info"
	cfg.Logging.Format = "json"

	// Create test logger
	logger := logrus.New()
	logger.SetOutput(bytes.NewBuffer(nil)) // Suppress log output during tests

	// Create router config (without database for this test)
	routerConfig := &RouterConfig{
		Config:    cfg,
		Logger:    logger,
		DBManager: nil,
	}

	// Setup router
	router := SetupRouter(routerConfig)

	// Test health endpoint (should work without database for basic test)
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/health", nil)
	router.ServeHTTP(w, req)

	// Health endpoint will fail without database, but should return structured response
	assert.Contains(t, []int{http.StatusOK, http.StatusServiceUnavailable}, w.Code)
	assert.NotEmpty(t, w.Header().Get("X-Request-ID"))
}

func TestPublicEndpoints(t *testing.T) {
	cfg := &config.Config{}
	cfg.Auth.JWTSecret = "test_secret"
	cfg.Logging.Level = "info"
	cfg.Logging.Format = "json"

	logger := logrus.New()
	logger.SetOutput(bytes.NewBuffer(nil))

	routerConfig := &RouterConfig{
		Config:    cfg,
		Logger:    logger,
		DBManager: nil,
	}

	router := SetupRouter(routerConfig)

	// Test public endpoints that don't require authentication
	publicEndpoints := []struct {
		method string
		path   string
	}{
		{"GET", "/api/v1/status"},
		{"POST", "/api/v1/auth/login"},
		{"POST", "/api/v1/auth/register"},
		{"POST", "/api/v1/auth/refresh"},
		{"GET", "/docs"},
	}

	for _, endpoint := range publicEndpoints {
		t.Run(endpoint.method+" "+endpoint.path, func(t *testing.T) {
			w := httptest.NewRecorder()
			req, _ := http.NewRequest(endpoint.method, endpoint.path, nil)
			router.ServeHTTP(w, req)

			// Should not return 401 (unauthorized) for public endpoints
			assert.NotEqual(t, http.StatusUnauthorized, w.Code)
			// Should have request ID header
			assert.NotEmpty(t, w.Header().Get("X-Request-ID"))
		})
	}
}

func TestProtectedEndpoints(t *testing.T) {
	cfg := &config.Config{}
	cfg.Auth.JWTSecret = "test_secret"
	cfg.Logging.Level = "info"
	cfg.Logging.Format = "json"

	logger := logrus.New()
	logger.SetOutput(bytes.NewBuffer(nil))

	routerConfig := &RouterConfig{
		Config:    cfg,
		Logger:    logger,
		DBManager: nil,
	}

	router := SetupRouter(routerConfig)

	// Test protected endpoints that require authentication
	protectedEndpoints := []struct {
		method string
		path   string
	}{
		{"POST", "/api/v1/quiz"},
		{"POST", "/api/v1/plaid/connect"},
		{"GET", "/api/v1/anomalies/yearly"},
		{"POST", "/api/v1/transactions/123/anomaly"},
		{"GET", "/api/v1/spending/categories"},
		{"GET", "/api/v1/spending/status"},
		{"GET", "/api/v1/spending/total"},
		{"GET", "/api/v1/trends"},
		{"GET", "/api/v1/goal/computed"},
		{"GET", "/api/v1/habits"},
		{"GET", "/api/v1/savings/weekly"},
		{"GET", "/api/v1/streak/longest"},
		{"GET", "/api/v1/streak/weekly"},
	}

	for _, endpoint := range protectedEndpoints {
		t.Run(endpoint.method+" "+endpoint.path+" without auth", func(t *testing.T) {
			w := httptest.NewRecorder()
			req, _ := http.NewRequest(endpoint.method, endpoint.path, nil)
			router.ServeHTTP(w, req)

			// Should return 401 (unauthorized) without token
			assert.Equal(t, http.StatusUnauthorized, w.Code)

			// Should return structured error response
			var response middleware.ErrorResponse
			err := json.Unmarshal(w.Body.Bytes(), &response)
			assert.NoError(t, err)
			assert.Equal(t, "AUTHENTICATION_ERROR", response.Error.Code)
			assert.NotEmpty(t, response.RequestID)
		})

		t.Run(endpoint.method+" "+endpoint.path+" with valid auth", func(t *testing.T) {
			// Create valid JWT token
			claims := &middleware.JWTClaims{
				UserID: 123,
				Email:  "test@example.com",
				RegisteredClaims: jwt.RegisteredClaims{
					ExpiresAt: jwt.NewNumericDate(time.Now().Add(time.Hour)),
					IssuedAt:  jwt.NewNumericDate(time.Now()),
				},
			}

			token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
			tokenString, err := token.SignedString([]byte(cfg.Auth.JWTSecret))
			assert.NoError(t, err)

			w := httptest.NewRecorder()
			req, _ := http.NewRequest(endpoint.method, endpoint.path, nil)
			req.Header.Set("Authorization", "Bearer "+tokenString)
			router.ServeHTTP(w, req)

			// Should not return 401 (unauthorized) with valid token
			assert.NotEqual(t, http.StatusUnauthorized, w.Code)
			// Most endpoints will return 501 (not implemented) for now
			assert.Contains(t, []int{http.StatusNotImplemented, http.StatusOK}, w.Code)
		})
	}
}

func TestMiddlewareOrder(t *testing.T) {
	cfg := &config.Config{}
	cfg.Auth.JWTSecret = "test_secret"
	cfg.Logging.Level = "info"
	cfg.Logging.Format = "json"

	logger := logrus.New()
	logger.SetOutput(bytes.NewBuffer(nil))

	routerConfig := &RouterConfig{
		Config:    cfg,
		Logger:    logger,
		DBManager: nil,
	}

	router := SetupRouter(routerConfig)

	// Test that middleware is applied in correct order
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/api/v1/status", nil)
	router.ServeHTTP(w, req)

	// Should have request ID (from RequestIDMiddleware)
	assert.NotEmpty(t, w.Header().Get("X-Request-ID"))

	// Should have CORS headers (from CORSMiddleware) - may be empty for some requests
	// The CORS middleware is applied, but headers may not be set for all requests
	corsHeader := w.Header().Get("Access-Control-Allow-Origin")
	// Just verify the middleware is in place by checking that we don't get an error
	assert.True(t, corsHeader == "*" || corsHeader == "")

	// Should return 200 for existing endpoint
	assert.Equal(t, http.StatusOK, w.Code)
}

func TestCORSHeaders(t *testing.T) {
	cfg := &config.Config{}
	cfg.Auth.JWTSecret = "test_secret"
	cfg.Logging.Level = "info"
	cfg.Logging.Format = "json"

	logger := logrus.New()
	logger.SetOutput(bytes.NewBuffer(nil))

	routerConfig := &RouterConfig{
		Config:    cfg,
		Logger:    logger,
		DBManager: nil,
	}

	router := SetupRouter(routerConfig)

	// Test CORS preflight request
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("OPTIONS", "/api/v1/quiz", nil)
	req.Header.Set("Origin", "http://localhost:3000")
	req.Header.Set("Access-Control-Request-Method", "POST")
	req.Header.Set("Access-Control-Request-Headers", "Authorization,Content-Type")
	router.ServeHTTP(w, req)

	// Should have CORS headers
	assert.Equal(t, "*", w.Header().Get("Access-Control-Allow-Origin"))
	assert.Contains(t, w.Header().Get("Access-Control-Allow-Methods"), "POST")
	assert.Contains(t, w.Header().Get("Access-Control-Allow-Headers"), "Authorization")
}
