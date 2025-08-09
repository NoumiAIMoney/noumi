package repository

import (
	"context"
	"database/sql"
	"fmt"
	"strings"

	"noumi-backend/internal/database/models"
)

// anomalyPostgresRepository implements AnomalyRepository for PostgreSQL
type anomalyPostgresRepository struct {
	db *sql.DB
}

// NewAnomalyRepository creates a new PostgreSQL anomaly repository
func NewAnomalyRepository(db *sql.DB) AnomalyRepository {
	return &anomalyPostgresRepository{
		db: db,
	}
}

// Create creates a new anomaly record in the database
func (r *anomalyPostgresRepository) Create(ctx context.Context, anomaly *models.Anomaly) error {
	query := `
		INSERT INTO anomalies (user_id, transaction_id, date, is_anomaly, anomaly_score, created_at)
		VALUES ($1, $2, $3, $4, $5, $6)
		RETURNING anomaly_id, created_at`

	err := r.db.QueryRowContext(
		ctx,
		query,
		anomaly.UserID,
		anomaly.TransactionID,
		anomaly.Date,
		anomaly.IsAnomaly,
		anomaly.AnomalyScore,
		anomaly.CreatedAt,
	).Scan(&anomaly.AnomalyID, &anomaly.CreatedAt)

	if err != nil {
		return fmt.Errorf("failed to create anomaly: %w", err)
	}

	return nil
}

// GetByID retrieves an anomaly by ID
func (r *anomalyPostgresRepository) GetByID(ctx context.Context, anomalyID int) (*models.Anomaly, error) {
	query := `
		SELECT anomaly_id, user_id, transaction_id, date, is_anomaly, anomaly_score, created_at
		FROM anomalies
		WHERE anomaly_id = $1`

	anomaly := &models.Anomaly{}
	err := r.db.QueryRowContext(ctx, query, anomalyID).Scan(
		&anomaly.AnomalyID,
		&anomaly.UserID,
		&anomaly.TransactionID,
		&anomaly.Date,
		&anomaly.IsAnomaly,
		&anomaly.AnomalyScore,
		&anomaly.CreatedAt,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, fmt.Errorf("anomaly not found")
		}
		return nil, fmt.Errorf("failed to get anomaly by ID: %w", err)
	}

	return anomaly, nil
}

// GetByUserID retrieves anomalies for a user within a date range
func (r *anomalyPostgresRepository) GetByUserID(ctx context.Context, userID int, dateRange DateRange) ([]*models.Anomaly, error) {
	query := `
		SELECT anomaly_id, user_id, transaction_id, date, is_anomaly, anomaly_score, created_at
		FROM anomalies
		WHERE user_id = $1 AND date >= $2 AND date <= $3
		ORDER BY date DESC`

	rows, err := r.db.QueryContext(ctx, query, userID, dateRange.StartDate, dateRange.EndDate)
	if err != nil {
		return nil, fmt.Errorf("failed to get anomalies by user ID: %w", err)
	}
	defer rows.Close()

	var anomalies []*models.Anomaly
	for rows.Next() {
		anomaly := &models.Anomaly{}
		err := rows.Scan(
			&anomaly.AnomalyID,
			&anomaly.UserID,
			&anomaly.TransactionID,
			&anomaly.Date,
			&anomaly.IsAnomaly,
			&anomaly.AnomalyScore,
			&anomaly.CreatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan anomaly: %w", err)
		}
		anomalies = append(anomalies, anomaly)
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("error iterating over anomalies: %w", err)
	}

	return anomalies, nil
}

// GetByTransactionID retrieves an anomaly by transaction ID
func (r *anomalyPostgresRepository) GetByTransactionID(ctx context.Context, transactionID string) (*models.Anomaly, error) {
	query := `
		SELECT anomaly_id, user_id, transaction_id, date, is_anomaly, anomaly_score, created_at
		FROM anomalies
		WHERE transaction_id = $1`

	anomaly := &models.Anomaly{}
	err := r.db.QueryRowContext(ctx, query, transactionID).Scan(
		&anomaly.AnomalyID,
		&anomaly.UserID,
		&anomaly.TransactionID,
		&anomaly.Date,
		&anomaly.IsAnomaly,
		&anomaly.AnomalyScore,
		&anomaly.CreatedAt,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, fmt.Errorf("anomaly not found for transaction")
		}
		return nil, fmt.Errorf("failed to get anomaly by transaction ID: %w", err)
	}

	return anomaly, nil
}

// GetYearlyCount retrieves the count of anomalies for a user in a specific year
func (r *anomalyPostgresRepository) GetYearlyCount(ctx context.Context, userID int, year int) (int, error) {
	query := `
		SELECT COUNT(*)
		FROM anomalies
		WHERE user_id = $1 AND is_anomaly = true 
		AND EXTRACT(YEAR FROM date) = $2`

	var count int
	err := r.db.QueryRowContext(ctx, query, userID, year).Scan(&count)
	if err != nil {
		return 0, fmt.Errorf("failed to get yearly anomaly count: %w", err)
	}

	return count, nil
}

// GetYearlyBreakdown retrieves monthly breakdown of anomalies for a user in a specific year
func (r *anomalyPostgresRepository) GetYearlyBreakdown(ctx context.Context, userID int, year int) (map[string]int, error) {
	query := `
		SELECT TO_CHAR(date, 'Month') as month, COUNT(*) as count
		FROM anomalies
		WHERE user_id = $1 AND is_anomaly = true 
		AND EXTRACT(YEAR FROM date) = $2
		GROUP BY EXTRACT(MONTH FROM date), TO_CHAR(date, 'Month')
		ORDER BY EXTRACT(MONTH FROM date)`

	rows, err := r.db.QueryContext(ctx, query, userID, year)
	if err != nil {
		return nil, fmt.Errorf("failed to get yearly anomaly breakdown: %w", err)
	}
	defer rows.Close()

	result := make(map[string]int)
	for rows.Next() {
		var month string
		var count int
		err := rows.Scan(&month, &count)
		if err != nil {
			return nil, fmt.Errorf("failed to scan anomaly breakdown: %w", err)
		}
		// Trim whitespace from month name (PostgreSQL TO_CHAR pads with spaces)
		result[strings.TrimSpace(month)] = count
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("error iterating over anomaly breakdown: %w", err)
	}

	return result, nil
}

// Update updates an existing anomaly
func (r *anomalyPostgresRepository) Update(ctx context.Context, anomaly *models.Anomaly) error {
	query := `
		UPDATE anomalies
		SET user_id = $2, transaction_id = $3, date = $4, is_anomaly = $5, anomaly_score = $6
		WHERE anomaly_id = $1`

	result, err := r.db.ExecContext(
		ctx,
		query,
		anomaly.AnomalyID,
		anomaly.UserID,
		anomaly.TransactionID,
		anomaly.Date,
		anomaly.IsAnomaly,
		anomaly.AnomalyScore,
	)

	if err != nil {
		return fmt.Errorf("failed to update anomaly: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rowsAffected == 0 {
		return fmt.Errorf("anomaly not found")
	}

	return nil
}

// Delete deletes an anomaly by ID
func (r *anomalyPostgresRepository) Delete(ctx context.Context, anomalyID int) error {
	query := `DELETE FROM anomalies WHERE anomaly_id = $1`

	result, err := r.db.ExecContext(ctx, query, anomalyID)
	if err != nil {
		return fmt.Errorf("failed to delete anomaly: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rowsAffected == 0 {
		return fmt.Errorf("anomaly not found")
	}

	return nil
}
