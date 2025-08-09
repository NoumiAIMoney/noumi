package repository

import (
	"context"
	"database/sql"
	"fmt"

	"noumi-backend/internal/database/models"
)

// plaidAccountPostgresRepository implements PlaidAccountRepository for PostgreSQL
type plaidAccountPostgresRepository struct {
	db *sql.DB
}

// NewPlaidAccountRepository creates a new PostgreSQL Plaid account repository
func NewPlaidAccountRepository(db *sql.DB) PlaidAccountRepository {
	return &plaidAccountPostgresRepository{
		db: db,
	}
}

// Create creates a new Plaid account in the database
func (r *plaidAccountPostgresRepository) Create(ctx context.Context, account *models.PlaidAccount) error {
	query := `
		INSERT INTO plaid_accounts (account_id, user_id, plaid_item_id, account_name, account_type, bank_name, is_active, created_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
		RETURNING created_at`

	err := r.db.QueryRowContext(
		ctx,
		query,
		account.AccountID,
		account.UserID,
		account.PlaidItemID,
		account.AccountName,
		account.AccountType,
		account.BankName,
		account.IsActive,
		account.CreatedAt,
	).Scan(&account.CreatedAt)

	if err != nil {
		return fmt.Errorf("failed to create Plaid account: %w", err)
	}

	return nil
}

// GetByID retrieves a Plaid account by ID
func (r *plaidAccountPostgresRepository) GetByID(ctx context.Context, accountID string) (*models.PlaidAccount, error) {
	query := `
		SELECT account_id, user_id, plaid_item_id, account_name, account_type, bank_name, is_active, created_at
		FROM plaid_accounts
		WHERE account_id = $1`

	account := &models.PlaidAccount{}
	err := r.db.QueryRowContext(ctx, query, accountID).Scan(
		&account.AccountID,
		&account.UserID,
		&account.PlaidItemID,
		&account.AccountName,
		&account.AccountType,
		&account.BankName,
		&account.IsActive,
		&account.CreatedAt,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, fmt.Errorf("Plaid account not found")
		}
		return nil, fmt.Errorf("failed to get Plaid account by ID: %w", err)
	}

	return account, nil
}

// GetByUserID retrieves all Plaid accounts for a user
func (r *plaidAccountPostgresRepository) GetByUserID(ctx context.Context, userID int) ([]*models.PlaidAccount, error) {
	query := `
		SELECT account_id, user_id, plaid_item_id, account_name, account_type, bank_name, is_active, created_at
		FROM plaid_accounts
		WHERE user_id = $1
		ORDER BY created_at DESC`

	rows, err := r.db.QueryContext(ctx, query, userID)
	if err != nil {
		return nil, fmt.Errorf("failed to get Plaid accounts by user ID: %w", err)
	}
	defer rows.Close()

	var accounts []*models.PlaidAccount
	for rows.Next() {
		account := &models.PlaidAccount{}
		err := rows.Scan(
			&account.AccountID,
			&account.UserID,
			&account.PlaidItemID,
			&account.AccountName,
			&account.AccountType,
			&account.BankName,
			&account.IsActive,
			&account.CreatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan Plaid account: %w", err)
		}
		accounts = append(accounts, account)
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("error iterating over Plaid accounts: %w", err)
	}

	return accounts, nil
}

// Update updates an existing Plaid account
func (r *plaidAccountPostgresRepository) Update(ctx context.Context, account *models.PlaidAccount) error {
	query := `
		UPDATE plaid_accounts
		SET user_id = $2, plaid_item_id = $3, account_name = $4, account_type = $5, bank_name = $6, is_active = $7
		WHERE account_id = $1`

	result, err := r.db.ExecContext(
		ctx,
		query,
		account.AccountID,
		account.UserID,
		account.PlaidItemID,
		account.AccountName,
		account.AccountType,
		account.BankName,
		account.IsActive,
	)

	if err != nil {
		return fmt.Errorf("failed to update Plaid account: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rowsAffected == 0 {
		return fmt.Errorf("Plaid account not found")
	}

	return nil
}

// Delete deletes a Plaid account by ID
func (r *plaidAccountPostgresRepository) Delete(ctx context.Context, accountID string) error {
	query := `DELETE FROM plaid_accounts WHERE account_id = $1`

	result, err := r.db.ExecContext(ctx, query, accountID)
	if err != nil {
		return fmt.Errorf("failed to delete Plaid account: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rowsAffected == 0 {
		return fmt.Errorf("Plaid account not found")
	}

	return nil
}
