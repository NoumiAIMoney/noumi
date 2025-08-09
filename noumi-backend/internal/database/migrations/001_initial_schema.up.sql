-- Initial database schema for Noumi backend
-- PostgreSQL version with proper indexes and constraints

-- Enable UUID extension for generating UUIDs if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    financial_goal VARCHAR(100),
    impulse_triggers JSONB,
    budgeting_score INTEGER DEFAULT 2 CHECK (budgeting_score >= 1 AND budgeting_score <= 5),
    plaid_token TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for users table
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Goals table
CREATE TABLE goals (
    goal_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    goal_name VARCHAR(255) NOT NULL,
    goal_description TEXT,
    goal_amount DECIMAL(12,2) NOT NULL CHECK (goal_amount > 0),
    target_date DATE NOT NULL,
    net_monthly_income DECIMAL(12,2) CHECK (net_monthly_income > 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for goals table
CREATE INDEX idx_goals_user_id ON goals(user_id);
CREATE INDEX idx_goals_created_at ON goals(created_at);
CREATE INDEX idx_goals_target_date ON goals(target_date);

-- Plaid accounts table
CREATE TABLE plaid_accounts (
    account_id VARCHAR(255) PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    plaid_item_id VARCHAR(255) NOT NULL,
    account_name VARCHAR(255),
    account_type VARCHAR(100),
    bank_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for plaid_accounts table
CREATE INDEX idx_plaid_accounts_user_id ON plaid_accounts(user_id);
CREATE INDEX idx_plaid_accounts_plaid_item_id ON plaid_accounts(plaid_item_id);
CREATE INDEX idx_plaid_accounts_is_active ON plaid_accounts(is_active);

-- Transactions table
CREATE TABLE transactions (
    transaction_id VARCHAR(255) PRIMARY KEY,
    account_id VARCHAR(255) NOT NULL REFERENCES plaid_accounts(account_id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    amount DECIMAL(12,2) NOT NULL,
    date DATE NOT NULL,
    merchant_name VARCHAR(255),
    category VARCHAR(100),
    mcc INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for transactions table
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_account_id ON transactions(account_id);
CREATE INDEX idx_transactions_date ON transactions(date);
CREATE INDEX idx_transactions_category ON transactions(category);
CREATE INDEX idx_transactions_amount ON transactions(amount);
CREATE INDEX idx_transactions_user_date ON transactions(user_id, date);

-- Anomalies table
CREATE TABLE anomalies (
    anomaly_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    transaction_id VARCHAR(255) NOT NULL REFERENCES transactions(transaction_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    is_anomaly BOOLEAN NOT NULL DEFAULT false,
    anomaly_score DECIMAL(8,4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for anomalies table
CREATE INDEX idx_anomalies_user_id ON anomalies(user_id);
CREATE INDEX idx_anomalies_transaction_id ON anomalies(transaction_id);
CREATE INDEX idx_anomalies_date ON anomalies(date);
CREATE INDEX idx_anomalies_is_anomaly ON anomalies(is_anomaly);
CREATE INDEX idx_anomalies_user_date ON anomalies(user_id, date);

-- Weekly plans table
CREATE TABLE weekly_plans (
    weekly_plan_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    week_start_date DATE NOT NULL,
    week_end_date DATE NOT NULL,
    plan_data JSONB NOT NULL,
    ml_features JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_week_dates CHECK (week_end_date > week_start_date)
);

-- Create indexes for weekly_plans table
CREATE INDEX idx_weekly_plans_user_id ON weekly_plans(user_id);
CREATE INDEX idx_weekly_plans_week_start ON weekly_plans(week_start_date);
CREATE INDEX idx_weekly_plans_is_active ON weekly_plans(is_active);
CREATE INDEX idx_weekly_plans_user_week ON weekly_plans(user_id, week_start_date);

-- Streak data table
CREATE TABLE streak_data (
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    streak_type VARCHAR(100) NOT NULL,
    current_streak INTEGER DEFAULT 0 CHECK (current_streak >= 0),
    longest_streak INTEGER DEFAULT 0 CHECK (longest_streak >= 0),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, streak_type)
);

-- Create indexes for streak_data table
CREATE INDEX idx_streak_data_user_id ON streak_data(user_id);
CREATE INDEX idx_streak_data_streak_type ON streak_data(streak_type);
CREATE INDEX idx_streak_data_last_activity ON streak_data(last_activity);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at in streak_data
CREATE TRIGGER update_streak_data_updated_at 
    BEFORE UPDATE ON streak_data 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Insert some default streak types
INSERT INTO streak_data (user_id, streak_type, current_streak, longest_streak) 
SELECT 1, 'anomaly_free', 0, 0 
WHERE NOT EXISTS (SELECT 1 FROM streak_data WHERE user_id = 1 AND streak_type = 'anomaly_free');

-- Create views for common queries
CREATE VIEW user_goals_summary AS
SELECT 
    u.user_id,
    u.name,
    u.email,
    COUNT(g.goal_id) as total_goals,
    SUM(g.goal_amount) as total_goal_amount,
    MAX(g.created_at) as latest_goal_date
FROM users u
LEFT JOIN goals g ON u.user_id = g.user_id
GROUP BY u.user_id, u.name, u.email;

CREATE VIEW user_transaction_summary AS
SELECT 
    u.user_id,
    u.name,
    COUNT(t.transaction_id) as total_transactions,
    SUM(CASE WHEN t.amount < 0 THEN ABS(t.amount) ELSE 0 END) as total_spending,
    SUM(CASE WHEN t.amount > 0 THEN t.amount ELSE 0 END) as total_income,
    MIN(t.date) as first_transaction_date,
    MAX(t.date) as last_transaction_date
FROM users u
LEFT JOIN transactions t ON u.user_id = t.user_id
GROUP BY u.user_id, u.name;

-- Add comments for documentation
COMMENT ON TABLE users IS 'User accounts and profile information';
COMMENT ON TABLE goals IS 'Financial goals set by users';
COMMENT ON TABLE plaid_accounts IS 'Bank accounts connected via Plaid';
COMMENT ON TABLE transactions IS 'Financial transactions from connected accounts';
COMMENT ON TABLE anomalies IS 'Anomaly detection results for transactions';
COMMENT ON TABLE weekly_plans IS 'AI-generated weekly financial plans';
COMMENT ON TABLE streak_data IS 'User streak tracking for various activities';

COMMENT ON COLUMN users.impulse_triggers IS 'JSON array of user impulse triggers';
COMMENT ON COLUMN users.budgeting_score IS 'User budgeting comfort level (1-5)';
COMMENT ON COLUMN weekly_plans.plan_data IS 'JSON object containing the complete weekly plan';
COMMENT ON COLUMN weekly_plans.ml_features IS 'JSON object containing ML features used for plan generation';