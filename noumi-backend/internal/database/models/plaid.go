package models

import (
	"time"
)

// PlaidAccount represents a Plaid-connected bank account
type PlaidAccount struct {
	AccountID   string    `json:"account_id" db:"account_id"`
	UserID      int       `json:"user_id" db:"user_id"`
	PlaidItemID string    `json:"plaid_item_id" db:"plaid_item_id"`
	AccountName string    `json:"account_name" db:"account_name"`
	AccountType string    `json:"account_type" db:"account_type"`
	BankName    string    `json:"bank_name" db:"bank_name"`
	IsActive    bool      `json:"is_active" db:"is_active"`
	CreatedAt   time.Time `json:"created_at" db:"created_at"`
}

// TableName returns the table name for the PlaidAccount model
func (PlaidAccount) TableName() string {
	return "plaid_accounts"
}

// PlaidConnectionRequest represents the request for connecting a Plaid account
type PlaidConnectionRequest struct {
	PublicToken string `json:"public_token" validate:"required"`
	AccountID   string `json:"account_id" validate:"required"`
}

// PlaidConnectionResponse represents the response for Plaid connection
type PlaidConnectionResponse struct {
	Success   bool   `json:"success"`
	AccountID string `json:"account_id"`
	Message   string `json:"message"`
}

// BankAccount represents a bank account (legacy compatibility)
type BankAccount struct {
	AccountID   int    `json:"account_id" db:"account_id"`
	UserID      int    `json:"user_id" db:"user_id"`
	BankName    string `json:"bank_name" db:"bank_name"`
	AccountType string `json:"account_type" db:"account_type"`
}

// ToResponse converts a PlaidAccount model to response format
func (p *PlaidAccount) ToResponse() map[string]interface{} {
	return map[string]interface{}{
		"account_id":    p.AccountID,
		"user_id":       p.UserID,
		"plaid_item_id": p.PlaidItemID,
		"account_name":  p.AccountName,
		"account_type":  p.AccountType,
		"bank_name":     p.BankName,
		"is_active":     p.IsActive,
		"created_at":    p.CreatedAt,
	}
}
