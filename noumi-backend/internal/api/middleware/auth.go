package middleware

import (
	"fmt"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"github.com/sirupsen/logrus"
)

const (
	UserIDKey    = "user_id"
	UserEmailKey = "user_email"
)

// JWTClaims represents the JWT token claims
type JWTClaims struct {
	UserID int    `json:"user_id"`
	Email  string `json:"email"`
	jwt.RegisteredClaims
}

// AuthMiddleware creates JWT authentication middleware
func AuthMiddleware(jwtSecret string, logger *logrus.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		// Get the Authorization header
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			logger.WithField("request_id", GetRequestID(c)).Warn("Missing Authorization header")
			c.Error(&AuthenticationError{
				Message: "Authorization header is required",
				Details: "Please provide a valid JWT token in the Authorization header",
			})
			c.Abort()
			return
		}

		// Check if the header starts with "Bearer "
		if !strings.HasPrefix(authHeader, "Bearer ") {
			logger.WithField("request_id", GetRequestID(c)).Warn("Invalid Authorization header format")
			c.Error(&AuthenticationError{
				Message: "Invalid authorization header format",
				Details: "Authorization header must start with 'Bearer '",
			})
			c.Abort()
			return
		}

		// Extract the token
		tokenString := strings.TrimPrefix(authHeader, "Bearer ")
		if tokenString == "" {
			logger.WithField("request_id", GetRequestID(c)).Warn("Empty JWT token")
			c.Error(&AuthenticationError{
				Message: "JWT token is required",
				Details: "Please provide a valid JWT token",
			})
			c.Abort()
			return
		}

		// Parse and validate the token
		token, err := jwt.ParseWithClaims(tokenString, &JWTClaims{}, func(token *jwt.Token) (interface{}, error) {
			// Validate the signing method
			if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
				return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
			}
			return []byte(jwtSecret), nil
		})

		if err != nil {
			logger.WithFields(logrus.Fields{
				"request_id": GetRequestID(c),
				"error":      err.Error(),
			}).Warn("JWT token validation failed")

			c.Error(&AuthenticationError{
				Message: "Invalid JWT token",
				Details: "Token validation failed",
			})
			c.Abort()
			return
		}

		// Check if token is valid and extract claims
		if claims, ok := token.Claims.(*JWTClaims); ok && token.Valid {
			// Check if token is expired
			if claims.ExpiresAt != nil && claims.ExpiresAt.Time.Before(time.Now()) {
				logger.WithField("request_id", GetRequestID(c)).Warn("JWT token expired")
				c.Error(&AuthenticationError{
					Message: "JWT token expired",
					Details: "Please obtain a new token",
				})
				c.Abort()
				return
			}

			// Set user information in context
			c.Set(UserIDKey, claims.UserID)
			c.Set(UserEmailKey, claims.Email)

			logger.WithFields(logrus.Fields{
				"request_id": GetRequestID(c),
				"user_id":    claims.UserID,
				"email":      claims.Email,
			}).Debug("JWT token validated successfully")

			c.Next()
		} else {
			logger.WithField("request_id", GetRequestID(c)).Warn("Invalid JWT token claims")
			c.Error(&AuthenticationError{
				Message: "Invalid JWT token",
				Details: "Token claims are invalid",
			})
			c.Abort()
			return
		}
	}
}

// OptionalAuthMiddleware creates optional JWT authentication middleware
// This middleware will extract user info if a valid token is provided, but won't fail if no token is present
func OptionalAuthMiddleware(jwtSecret string, logger *logrus.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			// No auth header, continue without authentication
			c.Next()
			return
		}

		if !strings.HasPrefix(authHeader, "Bearer ") {
			// Invalid format, continue without authentication
			c.Next()
			return
		}

		tokenString := strings.TrimPrefix(authHeader, "Bearer ")
		if tokenString == "" {
			// Empty token, continue without authentication
			c.Next()
			return
		}

		// Try to parse and validate the token
		token, err := jwt.ParseWithClaims(tokenString, &JWTClaims{}, func(token *jwt.Token) (interface{}, error) {
			if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
				return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
			}
			return []byte(jwtSecret), nil
		})

		if err == nil {
			if claims, ok := token.Claims.(*JWTClaims); ok && token.Valid {
				// Check if token is not expired
				if claims.ExpiresAt == nil || claims.ExpiresAt.Time.After(time.Now()) {
					// Set user information in context
					c.Set(UserIDKey, claims.UserID)
					c.Set(UserEmailKey, claims.Email)
				}
			}
		}

		c.Next()
	}
}

// GetUserID retrieves the user ID from the context
func GetUserID(c *gin.Context) (int, bool) {
	if userID, exists := c.Get(UserIDKey); exists {
		return userID.(int), true
	}
	return 0, false
}

// GetUserEmail retrieves the user email from the context
func GetUserEmail(c *gin.Context) (string, bool) {
	if email, exists := c.Get(UserEmailKey); exists {
		return email.(string), true
	}
	return "", false
}

// RequireAuth ensures that the user is authenticated
func RequireAuth() gin.HandlerFunc {
	return func(c *gin.Context) {
		if _, exists := GetUserID(c); !exists {
			c.Error(&AuthenticationError{
				Message: "Authentication required",
				Details: "This endpoint requires authentication",
			})
			c.Abort()
			return
		}
		c.Next()
	}
}
