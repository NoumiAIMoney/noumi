package models

import (
	"database/sql/driver"
	"encoding/json"
	"errors"
	"time"
)

// StringSlice is a custom type for handling JSON arrays in PostgreSQL
type StringSlice []string

// Value implements the driver.Valuer interface for database storage
func (s StringSlice) Value() (driver.Value, error) {
	if s == nil {
		return nil, nil
	}
	return json.Marshal(s)
}

// Scan implements the sql.Scanner interface for database retrieval
func (s *StringSlice) Scan(value interface{}) error {
	if value == nil {
		*s = nil
		return nil
	}

	bytes, ok := value.([]byte)
	if !ok {
		return errors.New("cannot scan non-[]byte value into StringSlice")
	}

	return json.Unmarshal(bytes, s)
}

// User represents a user in the system
type User struct {
	UserID          int         `json:"user_id" db:"user_id"`
	Email           string      `json:"email" db:"email" validate:"required,email"`
	PasswordHash    string      `json:"-" db:"password_hash"`
	Name            string      `json:"name" db:"name" validate:"required"`
	FinancialGoal   string      `json:"financial_goal" db:"financial_goal"`
	ImpulseTriggers StringSlice `json:"impulse_triggers" db:"impulse_triggers"`
	BudgetingScore  int         `json:"budgeting_score" db:"budgeting_score"`
	PlaidToken      string      `json:"-" db:"plaid_token"`
	CreatedAt       time.Time   `json:"created_at" db:"created_at"`
}

// TableName returns the table name for the User model
func (User) TableName() string {
	return "users"
}

// CreateUserRequest represents the request payload for creating a user
type CreateUserRequest struct {
	Email           string   `json:"email" validate:"required,email"`
	Password        string   `json:"password" validate:"required,min=8"`
	Name            string   `json:"name" validate:"required"`
	FinancialGoal   string   `json:"financial_goal"`
	ImpulseTriggers []string `json:"impulse_triggers"`
	BudgetingScore  int      `json:"budgeting_score"`
}

// UserResponse represents the response payload for user data
type UserResponse struct {
	UserID          int       `json:"user_id"`
	Email           string    `json:"email"`
	Name            string    `json:"name"`
	FinancialGoal   string    `json:"financial_goal"`
	ImpulseTriggers []string  `json:"impulse_triggers"`
	BudgetingScore  int       `json:"budgeting_score"`
	CreatedAt       time.Time `json:"created_at"`
}

// ToResponse converts a User model to UserResponse
func (u *User) ToResponse() *UserResponse {
	return &UserResponse{
		UserID:          u.UserID,
		Email:           u.Email,
		Name:            u.Name,
		FinancialGoal:   u.FinancialGoal,
		ImpulseTriggers: []string(u.ImpulseTriggers),
		BudgetingScore:  u.BudgetingScore,
		CreatedAt:       u.CreatedAt,
	}
}
