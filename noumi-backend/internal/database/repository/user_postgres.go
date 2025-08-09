package repository

import (
	"context"
	"database/sql"
	"fmt"

	"noumi-backend/internal/database/models"
)

// userPostgresRepository implements UserRepository for PostgreSQL
type userPostgresRepository struct {
	db *sql.DB
}

// NewUserRepository creates a new PostgreSQL user repository
func NewUserRepository(db *sql.DB) UserRepository {
	return &userPostgresRepository{
		db: db,
	}
}

// Create creates a new user in the database
func (r *userPostgresRepository) Create(ctx context.Context, user *models.User) error {
	query := `
		INSERT INTO users (email, password_hash, name, financial_goal, impulse_triggers, budgeting_score, plaid_token, created_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
		RETURNING user_id, created_at`

	err := r.db.QueryRowContext(
		ctx,
		query,
		user.Email,
		user.PasswordHash,
		user.Name,
		user.FinancialGoal,
		user.ImpulseTriggers,
		user.BudgetingScore,
		user.PlaidToken,
		user.CreatedAt,
	).Scan(&user.UserID, &user.CreatedAt)

	if err != nil {
		return fmt.Errorf("failed to create user: %w", err)
	}

	return nil
}

// GetByID retrieves a user by ID
func (r *userPostgresRepository) GetByID(ctx context.Context, userID int) (*models.User, error) {
	query := `
		SELECT user_id, email, password_hash, name, financial_goal, impulse_triggers, budgeting_score, plaid_token, created_at
		FROM users
		WHERE user_id = $1`

	user := &models.User{}
	err := r.db.QueryRowContext(ctx, query, userID).Scan(
		&user.UserID,
		&user.Email,
		&user.PasswordHash,
		&user.Name,
		&user.FinancialGoal,
		&user.ImpulseTriggers,
		&user.BudgetingScore,
		&user.PlaidToken,
		&user.CreatedAt,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, fmt.Errorf("user not found")
		}
		return nil, fmt.Errorf("failed to get user by ID: %w", err)
	}

	return user, nil
}

// GetByEmail retrieves a user by email address
func (r *userPostgresRepository) GetByEmail(ctx context.Context, email string) (*models.User, error) {
	query := `
		SELECT user_id, email, password_hash, name, financial_goal, impulse_triggers, budgeting_score, plaid_token, created_at
		FROM users
		WHERE email = $1`

	user := &models.User{}
	err := r.db.QueryRowContext(ctx, query, email).Scan(
		&user.UserID,
		&user.Email,
		&user.PasswordHash,
		&user.Name,
		&user.FinancialGoal,
		&user.ImpulseTriggers,
		&user.BudgetingScore,
		&user.PlaidToken,
		&user.CreatedAt,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, fmt.Errorf("user not found")
		}
		return nil, fmt.Errorf("failed to get user by email: %w", err)
	}

	return user, nil
}

// Update updates an existing user
func (r *userPostgresRepository) Update(ctx context.Context, user *models.User) error {
	query := `
		UPDATE users
		SET email = $2, password_hash = $3, name = $4, financial_goal = $5, 
		    impulse_triggers = $6, budgeting_score = $7, plaid_token = $8
		WHERE user_id = $1`

	result, err := r.db.ExecContext(
		ctx,
		query,
		user.UserID,
		user.Email,
		user.PasswordHash,
		user.Name,
		user.FinancialGoal,
		user.ImpulseTriggers,
		user.BudgetingScore,
		user.PlaidToken,
	)

	if err != nil {
		return fmt.Errorf("failed to update user: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rowsAffected == 0 {
		return fmt.Errorf("user not found")
	}

	return nil
}

// Delete deletes a user by ID
func (r *userPostgresRepository) Delete(ctx context.Context, userID int) error {
	query := `DELETE FROM users WHERE user_id = $1`

	result, err := r.db.ExecContext(ctx, query, userID)
	if err != nil {
		return fmt.Errorf("failed to delete user: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rowsAffected == 0 {
		return fmt.Errorf("user not found")
	}

	return nil
}
