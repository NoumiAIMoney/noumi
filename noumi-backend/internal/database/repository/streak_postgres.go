package repository

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	"noumi-backend/internal/database/models"
)

// streakPostgresRepository implements StreakRepository for PostgreSQL
type streakPostgresRepository struct {
	db *sql.DB
}

// NewStreakRepository creates a new PostgreSQL streak repository
func NewStreakRepository(db *sql.DB) StreakRepository {
	return &streakPostgresRepository{
		db: db,
	}
}

// Create creates a new streak record in the database
func (r *streakPostgresRepository) Create(ctx context.Context, streak *models.StreakData) error {
	query := `
		INSERT INTO streak_data (user_id, streak_type, current_streak, longest_streak, last_activity, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7)
		RETURNING created_at, updated_at`

	err := r.db.QueryRowContext(
		ctx,
		query,
		streak.UserID,
		streak.StreakType,
		streak.CurrentStreak,
		streak.LongestStreak,
		streak.LastActivity,
		streak.CreatedAt,
		streak.UpdatedAt,
	).Scan(&streak.CreatedAt, &streak.UpdatedAt)

	if err != nil {
		return fmt.Errorf("failed to create streak: %w", err)
	}

	return nil
}

// GetByUserID retrieves streak data for a user by streak type
func (r *streakPostgresRepository) GetByUserID(ctx context.Context, userID int, streakType string) (*models.StreakData, error) {
	query := `
		SELECT user_id, streak_type, current_streak, longest_streak, last_activity, created_at, updated_at
		FROM streak_data
		WHERE user_id = $1 AND streak_type = $2`

	streak := &models.StreakData{}
	err := r.db.QueryRowContext(ctx, query, userID, streakType).Scan(
		&streak.UserID,
		&streak.StreakType,
		&streak.CurrentStreak,
		&streak.LongestStreak,
		&streak.LastActivity,
		&streak.CreatedAt,
		&streak.UpdatedAt,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, fmt.Errorf("streak not found")
		}
		return nil, fmt.Errorf("failed to get streak by user ID: %w", err)
	}

	return streak, nil
}

// GetLongestByUserID retrieves the longest streak for a user across all types
func (r *streakPostgresRepository) GetLongestByUserID(ctx context.Context, userID int) (*models.StreakData, error) {
	query := `
		SELECT user_id, streak_type, current_streak, longest_streak, last_activity, created_at, updated_at
		FROM streak_data
		WHERE user_id = $1
		ORDER BY longest_streak DESC
		LIMIT 1`

	streak := &models.StreakData{}
	err := r.db.QueryRowContext(ctx, query, userID).Scan(
		&streak.UserID,
		&streak.StreakType,
		&streak.CurrentStreak,
		&streak.LongestStreak,
		&streak.LastActivity,
		&streak.CreatedAt,
		&streak.UpdatedAt,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, fmt.Errorf("no streaks found for user")
		}
		return nil, fmt.Errorf("failed to get longest streak: %w", err)
	}

	return streak, nil
}

// UpdateStreak updates or creates a streak record
func (r *streakPostgresRepository) UpdateStreak(ctx context.Context, userID int, streakType string, increment bool) error {
	// First, try to get existing streak
	existing, err := r.GetByUserID(ctx, userID, streakType)
	if err != nil && err.Error() != "streak not found" {
		return fmt.Errorf("failed to check existing streak: %w", err)
	}

	now := time.Now()

	if existing == nil {
		// Create new streak
		newStreak := &models.StreakData{
			UserID:        userID,
			StreakType:    streakType,
			CurrentStreak: 1,
			LongestStreak: 1,
			LastActivity:  now,
			CreatedAt:     now,
			UpdatedAt:     now,
		}
		return r.Create(ctx, newStreak)
	}

	// Update existing streak
	if increment {
		existing.CurrentStreak++
		if existing.CurrentStreak > existing.LongestStreak {
			existing.LongestStreak = existing.CurrentStreak
		}
	} else {
		existing.CurrentStreak = 0
	}

	existing.LastActivity = now
	existing.UpdatedAt = now

	return r.Update(ctx, existing)
}

// GetWeeklyProgress retrieves daily progress for a week
func (r *streakPostgresRepository) GetWeeklyProgress(ctx context.Context, userID int, weekStart, weekEnd time.Time) (map[string]bool, error) {
	// This is a simplified implementation - in a real system, you might have a separate table for daily activities
	query := `
		SELECT DATE(last_activity) as activity_date, COUNT(*) > 0 as has_activity
		FROM streak_data
		WHERE user_id = $1 AND last_activity >= $2 AND last_activity <= $3
		GROUP BY DATE(last_activity)
		ORDER BY activity_date`

	rows, err := r.db.QueryContext(ctx, query, userID, weekStart, weekEnd)
	if err != nil {
		return nil, fmt.Errorf("failed to get weekly progress: %w", err)
	}
	defer rows.Close()

	progress := make(map[string]bool)
	for rows.Next() {
		var activityDate time.Time
		var hasActivity bool
		err := rows.Scan(&activityDate, &hasActivity)
		if err != nil {
			return nil, fmt.Errorf("failed to scan weekly progress: %w", err)
		}
		progress[activityDate.Format("2006-01-02")] = hasActivity
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("error iterating over weekly progress: %w", err)
	}

	return progress, nil
}

// Update updates an existing streak
func (r *streakPostgresRepository) Update(ctx context.Context, streak *models.StreakData) error {
	query := `
		UPDATE streak_data
		SET current_streak = $3, longest_streak = $4, last_activity = $5, updated_at = $6
		WHERE user_id = $1 AND streak_type = $2`

	result, err := r.db.ExecContext(
		ctx,
		query,
		streak.UserID,
		streak.StreakType,
		streak.CurrentStreak,
		streak.LongestStreak,
		streak.LastActivity,
		streak.UpdatedAt,
	)

	if err != nil {
		return fmt.Errorf("failed to update streak: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rowsAffected == 0 {
		return fmt.Errorf("streak not found")
	}

	return nil
}

// Delete deletes a streak by user ID and type
func (r *streakPostgresRepository) Delete(ctx context.Context, userID int, streakType string) error {
	query := `DELETE FROM streak_data WHERE user_id = $1 AND streak_type = $2`

	result, err := r.db.ExecContext(ctx, query, userID, streakType)
	if err != nil {
		return fmt.Errorf("failed to delete streak: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rowsAffected == 0 {
		return fmt.Errorf("streak not found")
	}

	return nil
}
