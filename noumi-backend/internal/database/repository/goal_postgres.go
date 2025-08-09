package repository

import (
	"context"
	"database/sql"
	"fmt"

	"noumi-backend/internal/database/models"
)

// goalPostgresRepository implements GoalRepository for PostgreSQL
type goalPostgresRepository struct {
	db *sql.DB
}

// NewGoalRepository creates a new PostgreSQL goal repository
func NewGoalRepository(db *sql.DB) GoalRepository {
	return &goalPostgresRepository{
		db: db,
	}
}

// Create creates a new goal in the database
func (r *goalPostgresRepository) Create(ctx context.Context, goal *models.Goal) error {
	query := `
		INSERT INTO goals (user_id, goal_name, goal_description, goal_amount, target_date, net_monthly_income, created_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7)
		RETURNING goal_id, created_at`

	err := r.db.QueryRowContext(
		ctx,
		query,
		goal.UserID,
		goal.GoalName,
		goal.GoalDescription,
		goal.GoalAmount,
		goal.TargetDate,
		goal.NetMonthlyIncome,
		goal.CreatedAt,
	).Scan(&goal.GoalID, &goal.CreatedAt)

	if err != nil {
		return fmt.Errorf("failed to create goal: %w", err)
	}

	return nil
}

// GetByID retrieves a goal by ID
func (r *goalPostgresRepository) GetByID(ctx context.Context, goalID int) (*models.Goal, error) {
	query := `
		SELECT goal_id, user_id, goal_name, goal_description, goal_amount, target_date, net_monthly_income, created_at
		FROM goals
		WHERE goal_id = $1`

	goal := &models.Goal{}
	err := r.db.QueryRowContext(ctx, query, goalID).Scan(
		&goal.GoalID,
		&goal.UserID,
		&goal.GoalName,
		&goal.GoalDescription,
		&goal.GoalAmount,
		&goal.TargetDate,
		&goal.NetMonthlyIncome,
		&goal.CreatedAt,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, fmt.Errorf("goal not found")
		}
		return nil, fmt.Errorf("failed to get goal by ID: %w", err)
	}

	return goal, nil
}

// GetByUserID retrieves all goals for a user
func (r *goalPostgresRepository) GetByUserID(ctx context.Context, userID int) ([]*models.Goal, error) {
	query := `
		SELECT goal_id, user_id, goal_name, goal_description, goal_amount, target_date, net_monthly_income, created_at
		FROM goals
		WHERE user_id = $1
		ORDER BY created_at DESC`

	rows, err := r.db.QueryContext(ctx, query, userID)
	if err != nil {
		return nil, fmt.Errorf("failed to get goals by user ID: %w", err)
	}
	defer rows.Close()

	var goals []*models.Goal
	for rows.Next() {
		goal := &models.Goal{}
		err := rows.Scan(
			&goal.GoalID,
			&goal.UserID,
			&goal.GoalName,
			&goal.GoalDescription,
			&goal.GoalAmount,
			&goal.TargetDate,
			&goal.NetMonthlyIncome,
			&goal.CreatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan goal: %w", err)
		}
		goals = append(goals, goal)
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("error iterating over goals: %w", err)
	}

	return goals, nil
}

// GetLatestByUserID retrieves the most recent goal for a user
func (r *goalPostgresRepository) GetLatestByUserID(ctx context.Context, userID int) (*models.Goal, error) {
	query := `
		SELECT goal_id, user_id, goal_name, goal_description, goal_amount, target_date, net_monthly_income, created_at
		FROM goals
		WHERE user_id = $1
		ORDER BY created_at DESC
		LIMIT 1`

	goal := &models.Goal{}
	err := r.db.QueryRowContext(ctx, query, userID).Scan(
		&goal.GoalID,
		&goal.UserID,
		&goal.GoalName,
		&goal.GoalDescription,
		&goal.GoalAmount,
		&goal.TargetDate,
		&goal.NetMonthlyIncome,
		&goal.CreatedAt,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, fmt.Errorf("no goals found for user")
		}
		return nil, fmt.Errorf("failed to get latest goal: %w", err)
	}

	return goal, nil
}

// Update updates an existing goal
func (r *goalPostgresRepository) Update(ctx context.Context, goal *models.Goal) error {
	query := `
		UPDATE goals
		SET goal_name = $2, goal_description = $3, goal_amount = $4, target_date = $5, net_monthly_income = $6
		WHERE goal_id = $1`

	result, err := r.db.ExecContext(
		ctx,
		query,
		goal.GoalID,
		goal.GoalName,
		goal.GoalDescription,
		goal.GoalAmount,
		goal.TargetDate,
		goal.NetMonthlyIncome,
	)

	if err != nil {
		return fmt.Errorf("failed to update goal: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rowsAffected == 0 {
		return fmt.Errorf("goal not found")
	}

	return nil
}

// Delete deletes a goal by ID
func (r *goalPostgresRepository) Delete(ctx context.Context, goalID int) error {
	query := `DELETE FROM goals WHERE goal_id = $1`

	result, err := r.db.ExecContext(ctx, query, goalID)
	if err != nil {
		return fmt.Errorf("failed to delete goal: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rowsAffected == 0 {
		return fmt.Errorf("goal not found")
	}

	return nil
}
