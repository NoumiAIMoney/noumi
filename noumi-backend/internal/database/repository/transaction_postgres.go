package repository

import (
	"context"
	"database/sql"
	"fmt"

	"noumi-backend/internal/database/models"
)

// transactionPostgresRepository implements TransactionRepository for PostgreSQL
type transactionPostgresRepository struct {
	db *sql.DB
}

// NewTransactionRepository creates a new PostgreSQL transaction repository
func NewTransactionRepository(db *sql.DB) TransactionRepository {
	return &transactionPostgresRepository{
		db: db,
	}
}

// Create creates a new transaction in the database
func (r *transactionPostgresRepository) Create(ctx context.Context, transaction *models.Transaction) error {
	query := `
		INSERT INTO transactions (transaction_id, account_id, user_id, amount, date, merchant_name, category, mcc, created_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
		RETURNING created_at`

	err := r.db.QueryRowContext(
		ctx,
		query,
		transaction.TransactionID,
		transaction.AccountID,
		transaction.UserID,
		transaction.Amount,
		transaction.Date,
		transaction.MerchantName,
		transaction.Category,
		transaction.MCC,
		transaction.CreatedAt,
	).Scan(&transaction.CreatedAt)

	if err != nil {
		return fmt.Errorf("failed to create transaction: %w", err)
	}

	return nil
}

// GetByID retrieves a transaction by ID
func (r *transactionPostgresRepository) GetByID(ctx context.Context, transactionID string) (*models.Transaction, error) {
	query := `
		SELECT transaction_id, account_id, user_id, amount, date, merchant_name, category, mcc, created_at
		FROM transactions
		WHERE transaction_id = $1`

	transaction := &models.Transaction{}
	err := r.db.QueryRowContext(ctx, query, transactionID).Scan(
		&transaction.TransactionID,
		&transaction.AccountID,
		&transaction.UserID,
		&transaction.Amount,
		&transaction.Date,
		&transaction.MerchantName,
		&transaction.Category,
		&transaction.MCC,
		&transaction.CreatedAt,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, fmt.Errorf("transaction not found")
		}
		return nil, fmt.Errorf("failed to get transaction by ID: %w", err)
	}

	return transaction, nil
}

// GetByUserID retrieves transactions for a user with filters
func (r *transactionPostgresRepository) GetByUserID(ctx context.Context, userID int, filters models.TransactionFilters) ([]*models.Transaction, error) {
	query := `
		SELECT transaction_id, account_id, user_id, amount, date, merchant_name, category, mcc, created_at
		FROM transactions
		WHERE user_id = $1`

	args := []interface{}{userID}
	argIndex := 2

	// Apply filters
	if filters.StartDate != nil {
		query += fmt.Sprintf(" AND date >= $%d", argIndex)
		args = append(args, *filters.StartDate)
		argIndex++
	}

	if filters.EndDate != nil {
		query += fmt.Sprintf(" AND date <= $%d", argIndex)
		args = append(args, *filters.EndDate)
		argIndex++
	}

	if filters.Category != nil {
		query += fmt.Sprintf(" AND category = $%d", argIndex)
		args = append(args, *filters.Category)
		argIndex++
	}

	if filters.MinAmount != nil {
		query += fmt.Sprintf(" AND amount >= $%d", argIndex)
		args = append(args, *filters.MinAmount)
		argIndex++
	}

	if filters.MaxAmount != nil {
		query += fmt.Sprintf(" AND amount <= $%d", argIndex)
		args = append(args, *filters.MaxAmount)
		argIndex++
	}

	query += " ORDER BY date DESC"

	if filters.Limit != nil {
		query += fmt.Sprintf(" LIMIT $%d", argIndex)
		args = append(args, *filters.Limit)
		argIndex++
	}

	if filters.Offset != nil {
		query += fmt.Sprintf(" OFFSET $%d", argIndex)
		args = append(args, *filters.Offset)
	}

	rows, err := r.db.QueryContext(ctx, query, args...)
	if err != nil {
		return nil, fmt.Errorf("failed to get transactions by user ID: %w", err)
	}
	defer rows.Close()

	var transactions []*models.Transaction
	for rows.Next() {
		transaction := &models.Transaction{}
		err := rows.Scan(
			&transaction.TransactionID,
			&transaction.AccountID,
			&transaction.UserID,
			&transaction.Amount,
			&transaction.Date,
			&transaction.MerchantName,
			&transaction.Category,
			&transaction.MCC,
			&transaction.CreatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan transaction: %w", err)
		}
		transactions = append(transactions, transaction)
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("error iterating over transactions: %w", err)
	}

	return transactions, nil
}

// GetByAccountID retrieves transactions for an account with filters
func (r *transactionPostgresRepository) GetByAccountID(ctx context.Context, accountID string, filters models.TransactionFilters) ([]*models.Transaction, error) {
	query := `
		SELECT transaction_id, account_id, user_id, amount, date, merchant_name, category, mcc, created_at
		FROM transactions
		WHERE account_id = $1`

	args := []interface{}{accountID}
	argIndex := 2

	// Apply filters (similar to GetByUserID)
	if filters.StartDate != nil {
		query += fmt.Sprintf(" AND date >= $%d", argIndex)
		args = append(args, *filters.StartDate)
		argIndex++
	}

	if filters.EndDate != nil {
		query += fmt.Sprintf(" AND date <= $%d", argIndex)
		args = append(args, *filters.EndDate)
		argIndex++
	}

	query += " ORDER BY date DESC"

	if filters.Limit != nil {
		query += fmt.Sprintf(" LIMIT $%d", argIndex)
		args = append(args, *filters.Limit)
	}

	rows, err := r.db.QueryContext(ctx, query, args...)
	if err != nil {
		return nil, fmt.Errorf("failed to get transactions by account ID: %w", err)
	}
	defer rows.Close()

	var transactions []*models.Transaction
	for rows.Next() {
		transaction := &models.Transaction{}
		err := rows.Scan(
			&transaction.TransactionID,
			&transaction.AccountID,
			&transaction.UserID,
			&transaction.Amount,
			&transaction.Date,
			&transaction.MerchantName,
			&transaction.Category,
			&transaction.MCC,
			&transaction.CreatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan transaction: %w", err)
		}
		transactions = append(transactions, transaction)
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("error iterating over transactions: %w", err)
	}

	return transactions, nil
}

// GetSpendingByCategory retrieves spending grouped by category
func (r *transactionPostgresRepository) GetSpendingByCategory(ctx context.Context, userID int, dateRange DateRange) (map[string]float64, error) {
	query := `
		SELECT category, SUM(ABS(amount)) as total
		FROM transactions
		WHERE user_id = $1 AND amount < 0 AND date >= $2 AND date <= $3
		GROUP BY category
		ORDER BY total DESC`

	rows, err := r.db.QueryContext(ctx, query, userID, dateRange.StartDate, dateRange.EndDate)
	if err != nil {
		return nil, fmt.Errorf("failed to get spending by category: %w", err)
	}
	defer rows.Close()

	result := make(map[string]float64)
	for rows.Next() {
		var category string
		var total float64
		err := rows.Scan(&category, &total)
		if err != nil {
			return nil, fmt.Errorf("failed to scan spending category: %w", err)
		}
		result[category] = total
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("error iterating over spending categories: %w", err)
	}

	return result, nil
}

// GetTotalSpending retrieves total spending for a user in a date range
func (r *transactionPostgresRepository) GetTotalSpending(ctx context.Context, userID int, dateRange DateRange) (float64, error) {
	query := `
		SELECT COALESCE(SUM(ABS(amount)), 0) as total
		FROM transactions
		WHERE user_id = $1 AND amount < 0 AND date >= $2 AND date <= $3`

	var total float64
	err := r.db.QueryRowContext(ctx, query, userID, dateRange.StartDate, dateRange.EndDate).Scan(&total)
	if err != nil {
		return 0, fmt.Errorf("failed to get total spending: %w", err)
	}

	return total, nil
}

// Update updates an existing transaction
func (r *transactionPostgresRepository) Update(ctx context.Context, transaction *models.Transaction) error {
	query := `
		UPDATE transactions
		SET account_id = $2, user_id = $3, amount = $4, date = $5, merchant_name = $6, category = $7, mcc = $8
		WHERE transaction_id = $1`

	result, err := r.db.ExecContext(
		ctx,
		query,
		transaction.TransactionID,
		transaction.AccountID,
		transaction.UserID,
		transaction.Amount,
		transaction.Date,
		transaction.MerchantName,
		transaction.Category,
		transaction.MCC,
	)

	if err != nil {
		return fmt.Errorf("failed to update transaction: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rowsAffected == 0 {
		return fmt.Errorf("transaction not found")
	}

	return nil
}

// Delete deletes a transaction by ID
func (r *transactionPostgresRepository) Delete(ctx context.Context, transactionID string) error {
	query := `DELETE FROM transactions WHERE transaction_id = $1`

	result, err := r.db.ExecContext(ctx, query, transactionID)
	if err != nil {
		return fmt.Errorf("failed to delete transaction: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rowsAffected == 0 {
		return fmt.Errorf("transaction not found")
	}

	return nil
}
