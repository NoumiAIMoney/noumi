-- Rollback script for initial schema migration

-- Drop views first
DROP VIEW IF EXISTS user_transaction_summary;
DROP VIEW IF EXISTS user_goals_summary;

-- Drop triggers
DROP TRIGGER IF EXISTS update_streak_data_updated_at ON streak_data;

-- Drop function
DROP FUNCTION IF EXISTS update_updated_at_column();

-- Drop tables in reverse order of dependencies
DROP TABLE IF EXISTS streak_data;
DROP TABLE IF EXISTS weekly_plans;
DROP TABLE IF EXISTS anomalies;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS plaid_accounts;
DROP TABLE IF EXISTS goals;
DROP TABLE IF EXISTS users;

-- Drop extensions if they were created by this migration
-- Note: Be careful with this in production as other databases might use these extensions
-- DROP EXTENSION IF EXISTS "uuid-ossp";