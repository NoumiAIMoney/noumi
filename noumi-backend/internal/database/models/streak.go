package models

import (
	"time"
)

// StreakData represents streak tracking data
type StreakData struct {
	UserID        int       `json:"user_id" db:"user_id"`
	StreakType    string    `json:"streak_type" db:"streak_type"`
	CurrentStreak int       `json:"current_streak" db:"current_streak"`
	LongestStreak int       `json:"longest_streak" db:"longest_streak"`
	LastActivity  time.Time `json:"last_activity" db:"last_activity"`
	CreatedAt     time.Time `json:"created_at" db:"created_at"`
	UpdatedAt     time.Time `json:"updated_at" db:"updated_at"`
}

// TableName returns the table name for the StreakData model
func (StreakData) TableName() string {
	return "streak_data"
}

// WeeklyStreakResponse represents the weekly streak response
type WeeklyStreakResponse struct {
	CurrentWeekStreak int                 `json:"current_week_streak"`
	WeekStartDate     time.Time           `json:"week_start_date"`
	WeekEndDate       time.Time           `json:"week_end_date"`
	DailyProgress     map[string]bool     `json:"daily_progress"`
	StreakType        string              `json:"streak_type"`
	Achievements      []StreakAchievement `json:"achievements"`
}

// LongestStreakResponse represents the longest streak response
type LongestStreakResponse struct {
	LongestStreak   int       `json:"longest_streak"`
	StreakType      string    `json:"streak_type"`
	StartDate       time.Time `json:"start_date"`
	EndDate         time.Time `json:"end_date"`
	CurrentStreak   int       `json:"current_streak"`
	IsCurrentActive bool      `json:"is_current_active"`
}

// StreakAchievement represents a streak milestone achievement
type StreakAchievement struct {
	AchievementID  int       `json:"achievement_id"`
	Title          string    `json:"title"`
	Description    string    `json:"description"`
	StreakRequired int       `json:"streak_required"`
	UnlockedAt     time.Time `json:"unlocked_at"`
	IsUnlocked     bool      `json:"is_unlocked"`
}

// WeeklySavingsResponse represents the weekly savings response
type WeeklySavingsResponse struct {
	WeekStartDate   time.Time `json:"week_start_date"`
	WeekEndDate     time.Time `json:"week_end_date"`
	TargetSavings   float64   `json:"target_savings"`
	ActualSavings   float64   `json:"actual_savings"`
	SavingsProgress float64   `json:"savings_progress"`
	GoalMet         bool      `json:"goal_met"`
	RemainingToSave float64   `json:"remaining_to_save"`
	DaysRemaining   int       `json:"days_remaining"`
}

// ToWeeklyStreakResponse converts streak data to weekly streak response
func (s *StreakData) ToWeeklyStreakResponse(weekStart, weekEnd time.Time) *WeeklyStreakResponse {
	return &WeeklyStreakResponse{
		CurrentWeekStreak: s.CurrentStreak,
		WeekStartDate:     weekStart,
		WeekEndDate:       weekEnd,
		DailyProgress:     make(map[string]bool),
		StreakType:        s.StreakType,
		Achievements:      []StreakAchievement{},
	}
}

// ToLongestStreakResponse converts streak data to longest streak response
func (s *StreakData) ToLongestStreakResponse() *LongestStreakResponse {
	return &LongestStreakResponse{
		LongestStreak:   s.LongestStreak,
		StreakType:      s.StreakType,
		StartDate:       s.CreatedAt,
		EndDate:         s.LastActivity,
		CurrentStreak:   s.CurrentStreak,
		IsCurrentActive: time.Since(s.LastActivity) < 48*time.Hour,
	}
}
