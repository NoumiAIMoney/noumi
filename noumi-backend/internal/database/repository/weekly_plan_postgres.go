package repository

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	"noumi-backend/internal/database/models"
)

// weeklyPlanPostgresRepository implements WeeklyPlanRepository for PostgreSQL
type weeklyPlanPostgresRepository struct {
	db *sql.DB
}

// NewWeeklyPlanRepository creates a new PostgreSQL weekly plan repository
func NewWeeklyPlanRepository(db *sql.DB) WeeklyPlanRepository {
	return &weeklyPlanPostgresRepository{
		db: db,
	}
}

// Create creates a new weekly plan in the database
func (r *weeklyPlanPostgresRepository) Create(ctx context.Context, plan *models.WeeklyPlan) error {
	query := `
		INSERT INTO weekly_plans (user_id, week_start_date, week_end_date, plan_data, ml_features, is_active, created_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7)
		RETURNING weekly_plan_id, created_at`

	err := r.db.QueryRowContext(
		ctx,
		query,
		plan.UserID,
		plan.WeekStartDate,
		plan.WeekEndDate,
		plan.PlanData,
		plan.MLFeatures,
		plan.IsActive,
		plan.CreatedAt,
	).Scan(&plan.WeeklyPlanID, &plan.CreatedAt)

	if err != nil {
		return fmt.Errorf("failed to create weekly plan: %w", err)
	}

	return nil
}

// GetByID retrieves a weekly plan by ID
func (r *weeklyPlanPostgresRepository) GetByID(ctx context.Context, planID int) (*models.WeeklyPlan, error) {
	query := `
		SELECT weekly_plan_id, user_id, week_start_date, week_end_date, plan_data, ml_features, is_active, created_at
		FROM weekly_plans
		WHERE weekly_plan_id = $1`

	plan := &models.WeeklyPlan{}
	err := r.db.QueryRowContext(ctx, query, planID).Scan(
		&plan.WeeklyPlanID,
		&plan.UserID,
		&plan.WeekStartDate,
		&plan.WeekEndDate,
		&plan.PlanData,
		&plan.MLFeatures,
		&plan.IsActive,
		&plan.CreatedAt,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, fmt.Errorf("weekly plan not found")
		}
		return nil, fmt.Errorf("failed to get weekly plan by ID: %w", err)
	}

	return plan, nil
}

// GetByUserID retrieves all weekly plans for a user
func (r *weeklyPlanPostgresRepository) GetByUserID(ctx context.Context, userID int) ([]*models.WeeklyPlan, error) {
	query := `
		SELECT weekly_plan_id, user_id, week_start_date, week_end_date, plan_data, ml_features, is_active, created_at
		FROM weekly_plans
		WHERE user_id = $1
		ORDER BY week_start_date DESC`

	rows, err := r.db.QueryContext(ctx, query, userID)
	if err != nil {
		return nil, fmt.Errorf("failed to get weekly plans by user ID: %w", err)
	}
	defer rows.Close()

	var plans []*models.WeeklyPlan
	for rows.Next() {
		plan := &models.WeeklyPlan{}
		err := rows.Scan(
			&plan.WeeklyPlanID,
			&plan.UserID,
			&plan.WeekStartDate,
			&plan.WeekEndDate,
			&plan.PlanData,
			&plan.MLFeatures,
			&plan.IsActive,
			&plan.CreatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan weekly plan: %w", err)
		}
		plans = append(plans, plan)
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("error iterating over weekly plans: %w", err)
	}

	return plans, nil
}

// GetCurrentByUserID retrieves the current active weekly plan for a user
func (r *weeklyPlanPostgresRepository) GetCurrentByUserID(ctx context.Context, userID int, currentDate time.Time) (*models.WeeklyPlan, error) {
	query := `
		SELECT weekly_plan_id, user_id, week_start_date, week_end_date, plan_data, ml_features, is_active, created_at
		FROM weekly_plans
		WHERE user_id = $1 AND is_active = true 
		AND $2 BETWEEN week_start_date AND week_end_date
		ORDER BY created_at DESC
		LIMIT 1`

	plan := &models.WeeklyPlan{}
	err := r.db.QueryRowContext(ctx, query, userID, currentDate).Scan(
		&plan.WeeklyPlanID,
		&plan.UserID,
		&plan.WeekStartDate,
		&plan.WeekEndDate,
		&plan.PlanData,
		&plan.MLFeatures,
		&plan.IsActive,
		&plan.CreatedAt,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, fmt.Errorf("no current weekly plan found")
		}
		return nil, fmt.Errorf("failed to get current weekly plan: %w", err)
	}

	return plan, nil
}

// GetByWeekStart retrieves a weekly plan by week start date
func (r *weeklyPlanPostgresRepository) GetByWeekStart(ctx context.Context, userID int, weekStart time.Time) (*models.WeeklyPlan, error) {
	query := `
		SELECT weekly_plan_id, user_id, week_start_date, week_end_date, plan_data, ml_features, is_active, created_at
		FROM weekly_plans
		WHERE user_id = $1 AND week_start_date = $2
		ORDER BY created_at DESC
		LIMIT 1`

	plan := &models.WeeklyPlan{}
	err := r.db.QueryRowContext(ctx, query, userID, weekStart).Scan(
		&plan.WeeklyPlanID,
		&plan.UserID,
		&plan.WeekStartDate,
		&plan.WeekEndDate,
		&plan.PlanData,
		&plan.MLFeatures,
		&plan.IsActive,
		&plan.CreatedAt,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, fmt.Errorf("weekly plan not found for week")
		}
		return nil, fmt.Errorf("failed to get weekly plan by week start: %w", err)
	}

	return plan, nil
}

// DeactivateOldPlans deactivates old weekly plans for a user
func (r *weeklyPlanPostgresRepository) DeactivateOldPlans(ctx context.Context, userID int, newWeekStart time.Time) error {
	query := `
		UPDATE weekly_plans
		SET is_active = false
		WHERE user_id = $1 AND week_start_date != $2`

	result, err := r.db.ExecContext(ctx, query, userID, newWeekStart)
	if err != nil {
		return fmt.Errorf("failed to deactivate old plans: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	// It's okay if no rows were affected (no old plans to deactivate)
	_ = rowsAffected

	return nil
}

// Update updates an existing weekly plan
func (r *weeklyPlanPostgresRepository) Update(ctx context.Context, plan *models.WeeklyPlan) error {
	query := `
		UPDATE weekly_plans
		SET week_start_date = $2, week_end_date = $3, plan_data = $4, ml_features = $5, is_active = $6
		WHERE weekly_plan_id = $1`

	result, err := r.db.ExecContext(
		ctx,
		query,
		plan.WeeklyPlanID,
		plan.WeekStartDate,
		plan.WeekEndDate,
		plan.PlanData,
		plan.MLFeatures,
		plan.IsActive,
	)

	if err != nil {
		return fmt.Errorf("failed to update weekly plan: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rowsAffected == 0 {
		return fmt.Errorf("weekly plan not found")
	}

	return nil
}

// Delete deletes a weekly plan by ID
func (r *weeklyPlanPostgresRepository) Delete(ctx context.Context, planID int) error {
	query := `DELETE FROM weekly_plans WHERE weekly_plan_id = $1`

	result, err := r.db.ExecContext(ctx, query, planID)
	if err != nil {
		return fmt.Errorf("failed to delete weekly plan: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rowsAffected == 0 {
		return fmt.Errorf("weekly plan not found")
	}

	return nil
}
