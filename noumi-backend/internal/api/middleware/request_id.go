package middleware

import (
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

const RequestIDKey = "request_id"

// RequestIDMiddleware generates a unique request ID for each request
func RequestIDMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		// Check if request ID is already set in headers
		requestID := c.GetHeader("X-Request-ID")
		if requestID == "" {
			// Generate a new UUID for the request
			requestID = uuid.New().String()
		}

		// Set the request ID in the context
		c.Set(RequestIDKey, requestID)

		// Set the request ID in the response header
		c.Header("X-Request-ID", requestID)

		c.Next()
	}
}

// GetRequestID retrieves the request ID from the context
func GetRequestID(c *gin.Context) string {
	if requestID, exists := c.Get(RequestIDKey); exists {
		return requestID.(string)
	}
	return ""
}
