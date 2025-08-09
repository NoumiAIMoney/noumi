// Package models contains all database models and related types for the Noumi backend
package models

// This file serves as the main entry point for all database models.
// Individual model definitions are in separate files for better organization.

// Model interfaces for common operations
type Model interface {
	TableName() string
}

// Ensure all models implement the Model interface
var (
	_ Model = (*User)(nil)
	_ Model = (*Goal)(nil)
	_ Model = (*Transaction)(nil)
	_ Model = (*Anomaly)(nil)
	_ Model = (*WeeklyPlan)(nil)
	_ Model = (*PlaidAccount)(nil)
	_ Model = (*StreakData)(nil)
)

// Common response types used across multiple endpoints
type HealthResponse struct {
	Status    string `json:"status"`
	Timestamp string `json:"timestamp"`
	Database  string `json:"database"`
}

type ErrorResponse struct {
	Error     APIError `json:"error"`
	RequestID string   `json:"request_id"`
	Timestamp string   `json:"timestamp"`
}

type APIError struct {
	Code    string `json:"code"`
	Message string `json:"message"`
	Details string `json:"details,omitempty"`
}

// Pagination types
type PaginationRequest struct {
	Page     int `json:"page" validate:"min=1"`
	PageSize int `json:"page_size" validate:"min=1,max=100"`
}

type PaginationResponse struct {
	Page       int `json:"page"`
	PageSize   int `json:"page_size"`
	TotalItems int `json:"total_items"`
	TotalPages int `json:"total_pages"`
}

// Common filter types
type DateRangeFilter struct {
	StartDate *string `json:"start_date" validate:"omitempty,datetime=2006-01-02"`
	EndDate   *string `json:"end_date" validate:"omitempty,datetime=2006-01-02"`
}

// Authentication types
type LoginRequest struct {
	Email    string `json:"email" validate:"required,email"`
	Password string `json:"password" validate:"required"`
}

type LoginResponse struct {
	Token        string        `json:"token"`
	RefreshToken string        `json:"refresh_token"`
	ExpiresIn    int           `json:"expires_in"`
	User         *UserResponse `json:"user"`
}

type RefreshTokenRequest struct {
	RefreshToken string `json:"refresh_token" validate:"required"`
}

// API versioning
const (
	APIVersion = "v1"
	APIPrefix  = "/api/" + APIVersion
)

// Database table names (constants for consistency)
const (
	TableUsers         = "users"
	TableGoals         = "goals"
	TableTransactions  = "transactions"
	TableAnomalies     = "anomalies"
	TableWeeklyPlans   = "weekly_plans"
	TablePlaidAccounts = "plaid_accounts"
	TableStreakData    = "streak_data"
)

// Common validation tags
const (
	ValidateRequired = "required"
	ValidateEmail    = "email"
	ValidateMin      = "min"
	ValidateMax      = "max"
	ValidateGT       = "gt"
	ValidateGTE      = "gte"
	ValidateLT       = "lt"
	ValidateLTE      = "lte"
)
