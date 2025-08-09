package models

import (
	"time"
)

// Anomaly represents an anomaly detection result
type Anomaly struct {
	AnomalyID     int       `json:"anomaly_id" db:"anomaly_id"`
	UserID        int       `json:"user_id" db:"user_id"`
	TransactionID string    `json:"transaction_id" db:"transaction_id"`
	Date          time.Time `json:"date" db:"date"`
	IsAnomaly     bool      `json:"is_anomaly" db:"is_anomaly"`
	AnomalyScore  *float64  `json:"anomaly_score" db:"anomaly_score"`
	CreatedAt     time.Time `json:"created_at" db:"created_at"`
}

// TableName returns the table name for the Anomaly model
func (Anomaly) TableName() string {
	return "anomalies"
}

// CreateAnomalyRequest represents the request payload for creating an anomaly record
type CreateAnomalyRequest struct {
	TransactionID string    `json:"transaction_id" validate:"required"`
	Date          time.Time `json:"date" validate:"required"`
	IsAnomaly     bool      `json:"is_anomaly"`
	AnomalyScore  *float64  `json:"anomaly_score"`
}

// AnomalyResponse represents the response payload for anomaly data
type AnomalyResponse struct {
	AnomalyID     int       `json:"anomaly_id"`
	UserID        int       `json:"user_id"`
	TransactionID string    `json:"transaction_id"`
	Date          time.Time `json:"date"`
	IsAnomaly     bool      `json:"is_anomaly"`
	AnomalyScore  *float64  `json:"anomaly_score"`
	CreatedAt     time.Time `json:"created_at"`
}

// AnomalyDetectionRequest represents the request for anomaly detection
type AnomalyDetectionRequest struct {
	AccountID string `json:"account_id" validate:"required"`
}

// AnomalyDetectionResponse represents the response for anomaly detection
type AnomalyDetectionResponse struct {
	AnomalyScore float64            `json:"anomaly_score"`
	IsAnomaly    bool               `json:"is_anomaly"`
	Features     map[string]float64 `json:"features"`
}

// YearlyAnomaliesResponse represents the yearly anomaly counts
type YearlyAnomaliesResponse struct {
	Year             int            `json:"year"`
	TotalCount       int            `json:"total_count"`
	MonthlyBreakdown map[string]int `json:"monthly_breakdown"`
	AnomalyDates     []string       `json:"anomaly_dates"`
}

// ToResponse converts an Anomaly model to AnomalyResponse
func (a *Anomaly) ToResponse() *AnomalyResponse {
	return &AnomalyResponse{
		AnomalyID:     a.AnomalyID,
		UserID:        a.UserID,
		TransactionID: a.TransactionID,
		Date:          a.Date,
		IsAnomaly:     a.IsAnomaly,
		AnomalyScore:  a.AnomalyScore,
		CreatedAt:     a.CreatedAt,
	}
}
