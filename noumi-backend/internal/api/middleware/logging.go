package middleware

import (
	"bytes"
	"io"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
)

// responseWriter wraps gin.ResponseWriter to capture response body
type responseWriter struct {
	gin.ResponseWriter
	body *bytes.Buffer
}

func (w responseWriter) Write(b []byte) (int, error) {
	w.body.Write(b)
	return w.ResponseWriter.Write(b)
}

// LoggingMiddleware creates a structured logging middleware
func LoggingMiddleware(logger *logrus.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		// Start timer
		start := time.Now()

		// Get request ID
		requestID := GetRequestID(c)

		// Capture request body for logging (only for non-GET requests)
		var requestBody []byte
		if c.Request.Method != "GET" && c.Request.Method != "HEAD" {
			if c.Request.Body != nil {
				requestBody, _ = io.ReadAll(c.Request.Body)
				// Restore the request body for further processing
				c.Request.Body = io.NopCloser(bytes.NewBuffer(requestBody))
			}
		}

		// Create response writer wrapper to capture response
		responseWriter := &responseWriter{
			ResponseWriter: c.Writer,
			body:           bytes.NewBufferString(""),
		}
		c.Writer = responseWriter

		// Process request
		c.Next()

		// Calculate latency
		latency := time.Since(start)

		// Create log entry with structured fields
		entry := logger.WithFields(logrus.Fields{
			"request_id":     requestID,
			"method":         c.Request.Method,
			"path":           c.Request.URL.Path,
			"query":          c.Request.URL.RawQuery,
			"status":         c.Writer.Status(),
			"latency_ms":     latency.Milliseconds(),
			"client_ip":      c.ClientIP(),
			"user_agent":     c.Request.UserAgent(),
			"content_length": c.Request.ContentLength,
			"response_size":  c.Writer.Size(),
		})

		// Add request body to logs for non-GET requests (be careful with sensitive data)
		if len(requestBody) > 0 && len(requestBody) < 1024 { // Only log small request bodies
			entry = entry.WithField("request_body", string(requestBody))
		}

		// Add response body for error responses (for debugging)
		if c.Writer.Status() >= 400 && responseWriter.body.Len() < 1024 {
			entry = entry.WithField("response_body", responseWriter.body.String())
		}

		// Log based on status code
		switch {
		case c.Writer.Status() >= 500:
			entry.Error("Server error")
		case c.Writer.Status() >= 400:
			entry.Warn("Client error")
		case c.Writer.Status() >= 300:
			entry.Info("Redirect")
		default:
			entry.Info("Request completed")
		}
	}
}

// LoggerMiddleware creates a simple request logger (alternative to structured logging)
func LoggerMiddleware(logger *logrus.Logger) gin.HandlerFunc {
	return gin.LoggerWithFormatter(func(param gin.LogFormatterParams) string {
		entry := logger.WithFields(logrus.Fields{
			"timestamp":  param.TimeStamp.Format(time.RFC3339),
			"method":     param.Method,
			"path":       param.Path,
			"status":     param.StatusCode,
			"latency":    param.Latency,
			"client_ip":  param.ClientIP,
			"user_agent": param.Request.UserAgent(),
		})

		if param.StatusCode >= 400 {
			entry.Error("Request completed with error")
		} else {
			entry.Info("Request completed")
		}

		return ""
	})
}
