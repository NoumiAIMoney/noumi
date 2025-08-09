package models

import (
	"database/sql/driver"
	"encoding/json"
	"errors"
	"time"
)

// JSONMap is a custom type for handling JSON objects in PostgreSQL
type JSONMap map[string]interface{}

// Value implements the driver.Valuer interface for database storage
func (j JSONMap) Value() (driver.Value, error) {
	if j == nil {
		return nil, nil
	}
	return json.Marshal(j)
}

// Scan implements the sql.Scanner interface for database retrieval
func (j *JSONMap) Scan(value interface{}) error {
	if value == nil {
		*j = nil
		return nil
	}

	bytes, ok := value.([]byte)
	if !ok {
		return errors.New("cannot scan non-[]byte value into JSONMap")
	}

	return json.Unmarshal(bytes, j)
}

// WeeklyPlan represents a weekly financial plan
type WeeklyPlan struct {
	WeeklyPlanID  int       `json:"weekly_plan_id" db:"weekly_plan_id"`
	UserID        int       `json:"user_id" db:"user_id"`
	WeekStartDate time.Time `json:"week_start_date" db:"week_start_date"`
	WeekEndDate   time.Time `json:"week_end_date" db:"week_end_date"`
	PlanData      JSONMap   `json:"plan_data" db:"plan_data"`
	MLFeatures    JSONMap   `json:"ml_features" db:"ml_features"`
	IsActive      bool      `json:"is_active" db:"is_active"`
	CreatedAt     time.Time `json:"created_at" db:"created_at"`
}

// TableName returns the table name for the WeeklyPlan model
func (WeeklyPlan) TableName() string {
	return "weekly_plans"
}

// CreateWeeklyPlanRequest represents the request payload for creating a weekly plan
type CreateWeeklyPlanRequest struct {
	WeekStartDate time.Time              `json:"week_start_date" validate:"required"`
	WeekEndDate   time.Time              `json:"week_end_date" validate:"required"`
	PlanData      map[string]interface{} `json:"plan_data" validate:"required"`
	MLFeatures    map[string]interface{} `json:"ml_features"`
	IsActive      bool                   `json:"is_active"`
}

// WeeklyPlanResponse represents the response payload for weekly plan data
type WeeklyPlanResponse struct {
	WeeklyPlanID  int                    `json:"weekly_plan_id"`
	UserID        int                    `json:"user_id"`
	WeekStartDate time.Time              `json:"week_start_date"`
	WeekEndDate   time.Time              `json:"week_end_date"`
	PlanData      map[string]interface{} `json:"plan_data"`
	MLFeatures    map[string]interface{} `json:"ml_features"`
	IsActive      bool                   `json:"is_active"`
	CreatedAt     time.Time              `json:"created_at"`
}

// UserHabit represents a user habit derived from weekly plans
type UserHabit struct {
	HabitID           int    `json:"habit_id"`
	Description       string `json:"habit_description"`
	WeeklyOccurrences int    `json:"occurrences"`
	StreakCount       int    `json:"streak_count"`
	IsCompleted       bool   `json:"is_completed"`
}

// HabitsResponse represents the response for habits endpoint
type HabitsResponse struct {
	Habits        []UserHabit `json:"habits"`
	WeekStartDate time.Time   `json:"week_start_date"`
	WeekEndDate   time.Time   `json:"week_end_date"`
}

// WeeklyPlanRequest represents the request for generating a weekly plan
type WeeklyPlanRequest struct {
	UserID          int       `json:"user_id" validate:"required"`
	WeekStartDate   time.Time `json:"week_start_date" validate:"required"`
	ForceRegenerate bool      `json:"force_regenerate"`
}

// ToResponse converts a WeeklyPlan model to WeeklyPlanResponse
func (w *WeeklyPlan) ToResponse() *WeeklyPlanResponse {
	return &WeeklyPlanResponse{
		WeeklyPlanID:  w.WeeklyPlanID,
		UserID:        w.UserID,
		WeekStartDate: w.WeekStartDate,
		WeekEndDate:   w.WeekEndDate,
		PlanData:      map[string]interface{}(w.PlanData),
		MLFeatures:    map[string]interface{}(w.MLFeatures),
		IsActive:      w.IsActive,
		CreatedAt:     w.CreatedAt,
	}
}
