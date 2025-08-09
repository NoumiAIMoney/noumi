package repository

import (
	"context"
	"database/sql"
	"time"

	"noumi-backend/internal/database/models"
)

// UserRepository defines the interface for user data operations
type UserRepository interface {
	Create(ctx context.Context, user *models.User) error
	GetByID(ctx context.Context, userID int) (*models.User, error)
	GetByEmail(ctx context.Context, email string) (*models.User, error)
	Update(ctx context.Context, user *models.User) error
	Delete(ctx context.Context, userID int) error
}

// GoalRepository defines the interface for goal data operations
type GoalRepository interface {
	Create(ctx context.Context, goal *models.Goal) error
	GetByID(ctx context.Context, goalID int) (*models.Goal, error)
	GetByUserID(ctx context.Context, userID int) ([]*models.Goal, error)
	GetLatestByUserID(ctx context.Context, userID int) (*models.Goal, error)
	Update(ctx context.Context, goal *models.Goal) error
	Delete(ctx context.Context, goalID int) error
}

// TransactionRepository defines the interface for transaction data operations
type TransactionRepository interface {
	Create(ctx context.Context, transaction *models.Transaction) error
	GetByID(ctx context.Context, transactionID string) (*models.Transaction, error)
	GetByUserID(ctx context.Context, userID int, filters models.TransactionFilters) ([]*models.Transaction, error)
	GetByAccountID(ctx context.Context, accountID string, filters models.TransactionFilters) ([]*models.Transaction, error)
	GetSpendingByCategory(ctx context.Context, userID int, dateRange DateRange) (map[string]float64, error)
	GetTotalSpending(ctx context.Context, userID int, dateRange DateRange) (float64, error)
	Update(ctx context.Context, transaction *models.Transaction) error
	Delete(ctx context.Context, transactionID string) error
}

// AnomalyRepository defines the interface for anomaly data operations
type AnomalyRepository interface {
	Create(ctx context.Context, anomaly *models.Anomaly) error
	GetByID(ctx context.Context, anomalyID int) (*models.Anomaly, error)
	GetByUserID(ctx context.Context, userID int, dateRange DateRange) ([]*models.Anomaly, error)
	GetByTransactionID(ctx context.Context, transactionID string) (*models.Anomaly, error)
	GetYearlyCount(ctx context.Context, userID int, year int) (int, error)
	GetYearlyBreakdown(ctx context.Context, userID int, year int) (map[string]int, error)
	Update(ctx context.Context, anomaly *models.Anomaly) error
	Delete(ctx context.Context, anomalyID int) error
}

// WeeklyPlanRepository defines the interface for weekly plan data operations
type WeeklyPlanRepository interface {
	Create(ctx context.Context, plan *models.WeeklyPlan) error
	GetByID(ctx context.Context, planID int) (*models.WeeklyPlan, error)
	GetByUserID(ctx context.Context, userID int) ([]*models.WeeklyPlan, error)
	GetCurrentByUserID(ctx context.Context, userID int, currentDate time.Time) (*models.WeeklyPlan, error)
	GetByWeekStart(ctx context.Context, userID int, weekStart time.Time) (*models.WeeklyPlan, error)
	DeactivateOldPlans(ctx context.Context, userID int, newWeekStart time.Time) error
	Update(ctx context.Context, plan *models.WeeklyPlan) error
	Delete(ctx context.Context, planID int) error
}

// PlaidAccountRepository defines the interface for Plaid account data operations
type PlaidAccountRepository interface {
	Create(ctx context.Context, account *models.PlaidAccount) error
	GetByID(ctx context.Context, accountID string) (*models.PlaidAccount, error)
	GetByUserID(ctx context.Context, userID int) ([]*models.PlaidAccount, error)
	Update(ctx context.Context, account *models.PlaidAccount) error
	Delete(ctx context.Context, accountID string) error
}

// StreakRepository defines the interface for streak data operations
type StreakRepository interface {
	Create(ctx context.Context, streak *models.StreakData) error
	GetByUserID(ctx context.Context, userID int, streakType string) (*models.StreakData, error)
	GetLongestByUserID(ctx context.Context, userID int) (*models.StreakData, error)
	UpdateStreak(ctx context.Context, userID int, streakType string, increment bool) error
	GetWeeklyProgress(ctx context.Context, userID int, weekStart, weekEnd time.Time) (map[string]bool, error)
	Update(ctx context.Context, streak *models.StreakData) error
	Delete(ctx context.Context, userID int, streakType string) error
}

// DateRange represents a date range for queries
type DateRange struct {
	StartDate time.Time
	EndDate   time.Time
}

// Repository aggregates all repository interfaces
type Repository struct {
	User         UserRepository
	Goal         GoalRepository
	Transaction  TransactionRepository
	Anomaly      AnomalyRepository
	WeeklyPlan   WeeklyPlanRepository
	PlaidAccount PlaidAccountRepository
	Streak       StreakRepository
}

// NewRepository creates a new repository instance with all sub-repositories
func NewRepository(db *sql.DB) *Repository {
	return &Repository{
		User:         NewUserRepository(db),
		Goal:         NewGoalRepository(db),
		Transaction:  NewTransactionRepository(db),
		Anomaly:      NewAnomalyRepository(db),
		WeeklyPlan:   NewWeeklyPlanRepository(db),
		PlaidAccount: NewPlaidAccountRepository(db),
		Streak:       NewStreakRepository(db),
	}
}
