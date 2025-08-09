package models

import (
	"time"
)

// Transaction represents a financial transaction
type Transaction struct {
	TransactionID string    `json:"transaction_id" db:"transaction_id"`
	AccountID     string    `json:"account_id" db:"account_id"`
	UserID        int       `json:"user_id" db:"user_id"`
	Amount        float64   `json:"amount" db:"amount"`
	Date          time.Time `json:"date" db:"date"`
	MerchantName  string    `json:"merchant_name" db:"merchant_name"`
	Category      string    `json:"category" db:"category"`
	MCC           int       `json:"mcc" db:"mcc"`
	CreatedAt     time.Time `json:"created_at" db:"created_at"`
}

// TableName returns the table name for the Transaction model
func (Transaction) TableName() string {
	return "transactions"
}

// CreateTransactionRequest represents the request payload for creating a transaction
type CreateTransactionRequest struct {
	TransactionID string    `json:"transaction_id" validate:"required"`
	AccountID     string    `json:"account_id" validate:"required"`
	Amount        float64   `json:"amount" validate:"required"`
	Date          time.Time `json:"date" validate:"required"`
	MerchantName  string    `json:"merchant_name"`
	Category      string    `json:"category"`
	MCC           int       `json:"mcc"`
}

// TransactionResponse represents the response payload for transaction data
type TransactionResponse struct {
	TransactionID string    `json:"transaction_id"`
	AccountID     string    `json:"account_id"`
	UserID        int       `json:"user_id"`
	Amount        float64   `json:"amount"`
	Date          time.Time `json:"date"`
	MerchantName  string    `json:"merchant_name"`
	Category      string    `json:"category"`
	MCC           int       `json:"mcc"`
	CreatedAt     time.Time `json:"created_at"`
}

// TransactionFilters represents filters for querying transactions
type TransactionFilters struct {
	StartDate *time.Time `json:"start_date"`
	EndDate   *time.Time `json:"end_date"`
	Category  *string    `json:"category"`
	MinAmount *float64   `json:"min_amount"`
	MaxAmount *float64   `json:"max_amount"`
	Limit     *int       `json:"limit"`
	Offset    *int       `json:"offset"`
}

// SpendingCategory represents spending data grouped by category
type SpendingCategory struct {
	CategoryName string  `json:"category_name"`
	Amount       float64 `json:"amount"`
	Month        string  `json:"month"`
}

// SpendingTrend represents a spending trend analysis
type SpendingTrend struct {
	Icon  string `json:"icon"`
	Trend string `json:"trend"`
}

// SpendingStatus represents the current spending status
type SpendingStatus struct {
	SafeToSpend     bool    `json:"safe_to_spend"`
	RemainingBudget float64 `json:"remaining_budget"`
	DaysUntilPayday int     `json:"days_until_payday"`
	Message         string  `json:"message"`
}

// TotalSpendingResponse represents the total spending response
type TotalSpendingResponse struct {
	TotalSpent        float64            `json:"total_spent"`
	Period            string             `json:"period"`
	StartDate         string             `json:"start_date"`
	EndDate           string             `json:"end_date"`
	CategoryBreakdown map[string]float64 `json:"category_breakdown"`
}

// ToResponse converts a Transaction model to TransactionResponse
func (t *Transaction) ToResponse() *TransactionResponse {
	return &TransactionResponse{
		TransactionID: t.TransactionID,
		AccountID:     t.AccountID,
		UserID:        t.UserID,
		Amount:        t.Amount,
		Date:          t.Date,
		MerchantName:  t.MerchantName,
		Category:      t.Category,
		MCC:           t.MCC,
		CreatedAt:     t.CreatedAt,
	}
}
