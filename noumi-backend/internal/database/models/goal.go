package models

import (
	"time"
)

// Goal represents a financial goal
type Goal struct {
	GoalID           int       `json:"goal_id" db:"goal_id"`
	UserID           int       `json:"user_id" db:"user_id"`
	GoalName         string    `json:"goal_name" db:"goal_name" validate:"required"`
	GoalDescription  string    `json:"goal_description" db:"goal_description"`
	GoalAmount       float64   `json:"goal_amount" db:"goal_amount" validate:"required,gt=0"`
	TargetDate       time.Time `json:"target_date" db:"target_date" validate:"required"`
	NetMonthlyIncome *float64  `json:"net_monthly_income" db:"net_monthly_income"`
	CreatedAt        time.Time `json:"created_at" db:"created_at"`
}

// TableName returns the table name for the Goal model
func (Goal) TableName() string {
	return "goals"
}

// CreateGoalRequest represents the request payload for creating a goal
type CreateGoalRequest struct {
	GoalName         string    `json:"goal_name" validate:"required"`
	GoalDescription  string    `json:"goal_description" validate:"required"`
	GoalAmount       float64   `json:"goal_amount" validate:"required,gt=0"`
	TargetDate       time.Time `json:"target_date" validate:"required"`
	NetMonthlyIncome *float64  `json:"net_monthly_income" validate:"omitempty,gt=0"`
}

// QuizSubmission represents the quiz submission payload (legacy compatibility)
type QuizSubmission struct {
	GoalName         string    `json:"goal_name" validate:"required" example:"Emergency Fund"`
	GoalDescription  string    `json:"goal_description" validate:"required" example:"Build an emergency fund for unexpected expenses"`
	GoalAmount       float64   `json:"goal_amount" validate:"required,gt=0" example:"10000.00"`
	TargetDate       time.Time `json:"target_date" validate:"required" example:"2025-12-31T00:00:00Z"`
	NetMonthlyIncome float64   `json:"net_monthly_income" validate:"required,gt=0" example:"5000.00"`
}

// GoalResponse represents the response payload for goal data
type GoalResponse struct {
	GoalID           int       `json:"goal_id" example:"1"`
	UserID           int       `json:"user_id" example:"123"`
	GoalName         string    `json:"goal_name" example:"Emergency Fund"`
	GoalDescription  string    `json:"goal_description" example:"Build an emergency fund for unexpected expenses"`
	GoalAmount       float64   `json:"goal_amount" example:"10000.00"`
	TargetDate       time.Time `json:"target_date" example:"2025-12-31T00:00:00Z"`
	NetMonthlyIncome *float64  `json:"net_monthly_income" example:"5000.00"`
	CreatedAt        time.Time `json:"created_at" example:"2025-08-10T16:00:00Z"`
}

// ComputedGoalResponse represents the computed goal data with progress
type ComputedGoalResponse struct {
	GoalName         string    `json:"goal_name"`
	GoalAmount       float64   `json:"goal_amount"`
	TargetDate       time.Time `json:"target_date"`
	NetMonthlyIncome *float64  `json:"net_monthly_income"`
	AmountSaved      float64   `json:"amount_saved"`
	ProgressPercent  float64   `json:"progress_percent"`
	DaysRemaining    int       `json:"days_remaining"`
	MonthlyRequired  float64   `json:"monthly_required"`
}

// ToResponse converts a Goal model to GoalResponse
func (g *Goal) ToResponse() *GoalResponse {
	return &GoalResponse{
		GoalID:           g.GoalID,
		UserID:           g.UserID,
		GoalName:         g.GoalName,
		GoalDescription:  g.GoalDescription,
		GoalAmount:       g.GoalAmount,
		TargetDate:       g.TargetDate,
		NetMonthlyIncome: g.NetMonthlyIncome,
		CreatedAt:        g.CreatedAt,
	}
}

// ToCreateGoalRequest converts QuizSubmission to CreateGoalRequest
func (q *QuizSubmission) ToCreateGoalRequest() *CreateGoalRequest {
	return &CreateGoalRequest{
		GoalName:         q.GoalName,
		GoalDescription:  q.GoalDescription,
		GoalAmount:       q.GoalAmount,
		TargetDate:       q.TargetDate,
		NetMonthlyIncome: &q.NetMonthlyIncome,
	}
}
