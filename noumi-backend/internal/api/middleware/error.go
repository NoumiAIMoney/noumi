package middleware

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
)

// APIError represents a structured API error
type APIError struct {
	Code    string `json:"code" example:"VALIDATION_ERROR"`
	Message string `json:"message" example:"Validation failed"`
	Details string `json:"details,omitempty" example:"goal_name is required"`
}

// ErrorResponse represents the standard error response format
type ErrorResponse struct {
	Error     APIError `json:"error"`
	RequestID string   `json:"request_id" example:"123e4567-e89b-12d3-a456-426614174000"`
	Timestamp string   `json:"timestamp" example:"2025-08-10T16:00:00Z"`
}

// Custom error types
type ValidationError struct {
	Message string
	Details string
}

func (e *ValidationError) Error() string {
	return e.Message
}

type DatabaseError struct {
	Message string
	Details string
}

func (e *DatabaseError) Error() string {
	return e.Message
}

type AuthenticationError struct {
	Message string
	Details string
}

func (e *AuthenticationError) Error() string {
	return e.Message
}

type AuthorizationError struct {
	Message string
	Details string
}

func (e *AuthorizationError) Error() string {
	return e.Message
}

type NotFoundError struct {
	Message string
	Details string
}

func (e *NotFoundError) Error() string {
	return e.Message
}

type ExternalAPIError struct {
	Message string
	Details string
}

func (e *ExternalAPIError) Error() string {
	return e.Message
}

// ErrorHandlerMiddleware handles errors and returns structured error responses
func ErrorHandlerMiddleware(logger *logrus.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Next()

		// Check if there are any errors
		if len(c.Errors) > 0 {
			err := c.Errors.Last()
			requestID := GetRequestID(c)
			timestamp := time.Now().UTC().Format(time.RFC3339)

			// Log the error with context
			logger.WithFields(logrus.Fields{
				"request_id": requestID,
				"method":     c.Request.Method,
				"path":       c.Request.URL.Path,
				"error":      err.Error(),
				"error_type": err.Type,
			}).Error("Request failed with error")

			var apiErr APIError
			var statusCode int

			// Handle different error types
			switch e := err.Err.(type) {
			case *ValidationError:
				apiErr = APIError{
					Code:    "VALIDATION_ERROR",
					Message: e.Message,
					Details: e.Details,
				}
				statusCode = http.StatusBadRequest

			case *AuthenticationError:
				apiErr = APIError{
					Code:    "AUTHENTICATION_ERROR",
					Message: e.Message,
					Details: e.Details,
				}
				statusCode = http.StatusUnauthorized

			case *AuthorizationError:
				apiErr = APIError{
					Code:    "AUTHORIZATION_ERROR",
					Message: e.Message,
					Details: e.Details,
				}
				statusCode = http.StatusForbidden

			case *NotFoundError:
				apiErr = APIError{
					Code:    "NOT_FOUND_ERROR",
					Message: e.Message,
					Details: e.Details,
				}
				statusCode = http.StatusNotFound

			case *DatabaseError:
				apiErr = APIError{
					Code:    "DATABASE_ERROR",
					Message: "Internal server error",
					Details: "Database operation failed",
				}
				statusCode = http.StatusInternalServerError

			case *ExternalAPIError:
				apiErr = APIError{
					Code:    "EXTERNAL_API_ERROR",
					Message: "External service unavailable",
					Details: e.Details,
				}
				statusCode = http.StatusServiceUnavailable

			default:
				// Generic error handling
				apiErr = APIError{
					Code:    "INTERNAL_ERROR",
					Message: "Internal server error",
					Details: "An unexpected error occurred",
				}
				statusCode = http.StatusInternalServerError
			}

			// Return structured error response
			c.JSON(statusCode, ErrorResponse{
				Error:     apiErr,
				RequestID: requestID,
				Timestamp: timestamp,
			})

			// Abort to prevent further processing
			c.Abort()
		}
	}
}

// RecoveryMiddleware handles panics and converts them to structured errors
func RecoveryMiddleware(logger *logrus.Logger) gin.HandlerFunc {
	return gin.CustomRecovery(func(c *gin.Context, recovered interface{}) {
		requestID := GetRequestID(c)

		logger.WithFields(logrus.Fields{
			"request_id": requestID,
			"method":     c.Request.Method,
			"path":       c.Request.URL.Path,
			"panic":      recovered,
		}).Error("Request panicked")

		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error: APIError{
				Code:    "INTERNAL_ERROR",
				Message: "Internal server error",
				Details: "An unexpected error occurred",
			},
			RequestID: requestID,
			Timestamp: time.Now().UTC().Format(time.RFC3339),
		})

		c.Abort()
	})
}
