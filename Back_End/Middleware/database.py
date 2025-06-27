"""
Database utilities and models for Noumi API
MVP (P0) Database Schema - PostgreSQL version with Anomaly Detection
"""

import psycopg2
import psycopg2.extras
import json
import pandas as pd
import numpy as np
import pickle
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from contextlib import contextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# PostgreSQL connection configuration
DB_CONFIG = {
    "host": "localhost",
    "port": "5433",
    "database": "noumidb",
    "user": "administrator",
    "password": "Xum07jlY0E5320NQn0hN"
}

# FastAPI app for anomaly detection
app = FastAPI(title="Noumi API with Anomaly Detection", version="1.0.0")


# Request/Response models for anomaly detection
class AnomalyRequest(BaseModel):
    account_id: str
    

class AnomalyResponse(BaseModel):
    anomaly_score: float
    is_anomaly: bool
    features: dict


# Configuration for model
MODEL_PATH = "model.pkl"  # Update this path as needed


@dataclass
class User:
    user_id: int
    email: str
    password_hash: str
    created_at: str
    name: str
    financial_goal: str  # e.g., 'GOAL_DEBT', 'GOAL_EFUND'
    impulse_triggers: List[str]  # e.g., ['Stress', 'FOMO', 'Boredom']
    budgeting_score: int  # 1 = sticks to budgets, 3 = budgets stress me out
    plaid_token: str  # Encrypted Plaid access token for bank connections


@dataclass
class Goal:
    goal_id: int
    user_id: int
    goal_amount: float
    goal_name: str
    goal_description: str
    target_date: str  # date
    net_monthly_income: Optional[float] = None
    created_at: str = None


@dataclass
class BankAccount:
    account_id: int
    user_id: int
    bank_name: str  # e.g., 'Chase', 'Bank of America'
    account_type: str  # e.g., 'Checking', 'Savings'


@dataclass
class Transaction:
    transaction_id: str  # TEXT in actual schema
    account_id: str  # TEXT in actual schema
    user_id: int
    amount: float
    date: str
    merchant_name: str
    category: str
    mcc: int
    description: str = ""  # Not in current schema but kept for compatibility
    local_time_bucket: str = ""  # Not in current schema
    rolling_spend_window: float = 0.0  # Not in current schema
    day_of_week: str = ""  # Not in current schema
    is_weekend: bool = False  # Not in current schema
    rolling_spend_7d: float = 0.0  # Not in current schema
    category_frequency: float = 0.0  # Not in current schema
    category_variance: float = 0.0  # Not in current schema


@dataclass
class SavingsPlan:
    plan_id: int
    goal_id: int
    weekly_recommendation: str  # LLM-generated savings strategy
    generated_at: str


@dataclass
class HabitCompletion:
    completion_id: int
    user_id: int
    habit_type: str  # e.g., 'Check balance', 'Transfer $10', 'Avoid impulse'
    completed_at: str
    streak_count: int  # Current streak length for this habit type
    milestone_achieved: str  # e.g., 'First 5 days', '30-day streak'


@dataclass
class Notification:
    notification_id: int
    user_id: int
    type: str  # e.g., 'Goal nudge', 'Habit streak', 'Weekly wrap-up'
    message: str  # e.g., 'You're 50% to your goal!', 'Keep your streak alive!'
    sent_at: str
    recap_id: Optional[int] = None  # FK → weekly_recaps.recap_id


@dataclass
class EmotionalSpendingFlag:
    flag_id: int
    transaction_id: int
    is_emotional: bool  # true if flagged as emotional
    emotional_type: str  # e.g., 'Stress', 'FOMO', 'Unnecessary'
    impulse_probability: float  # ML confidence score for emotional spending
    spike: bool  # True if flagged as anomaly by LSTM


@dataclass
class WeeklyRecap:
    recap_id: int
    user_id: int
    week_start_date: str  # date
    summary: str
    outlier_transactions: List[int]  # FK → transactions.transaction_id
    goal_progress: Optional[str] = None
    habit_streak_summary: Optional[str] = None
    created_at: str = None


@dataclass
class WeeklyPlan:
    weekly_plan_id: int
    user_id: int
    week_start_date: str  # Monday of the week this plan covers (YYYY-MM-DD)
    week_end_date: str    # Sunday of the week this plan covers (YYYY-MM-DD) 
    plan_data: str        # JSON string of the complete weekly plan
    ml_features: str      # JSON string of ML features
    created_at: str       # When this plan was generated
    is_active: bool       # Whether this plan is currently active


@contextmanager
def get_db_connection():
    """PostgreSQL database connection context manager"""
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()


def load_model():
    """Load the trained anomaly detection model."""
    with open(MODEL_PATH, 'rb') as f:
        return pickle.load(f)


def get_base_features(account_id: str):
    """Retrieve base features from PostgreSQL database."""
    with get_db_connection() as conn:
        # account_id is already text, no conversion needed
        
        # Get user data with monthly income from goals table
        user_query = """
        SELECT u.user_id, g.net_monthly_income 
        FROM users u 
        JOIN plaid_accounts pa ON u.user_id = pa.user_id 
        LEFT JOIN goals g ON u.user_id = g.user_id
        WHERE pa.account_id = %s
        LIMIT 1
        """
        user_df = pd.read_sql_query(user_query, conn, params=(account_id,))
        
        if user_df.empty:
            raise HTTPException(status_code=404, detail="Account not found")
        
        monthly_income = user_df['net_monthly_income'].iloc[0]
        if pd.isna(monthly_income):
            raise HTTPException(status_code=404, detail="Monthly income not found")
        
        # Get suggested savings amount (from goals table)
        savings_query = """
        SELECT g.goal_amount 
        FROM goals g
        JOIN plaid_accounts pa ON g.user_id = pa.user_id 
        WHERE pa.account_id = %s 
        ORDER BY g.created_at DESC LIMIT 1
        """
        savings_df = pd.read_sql_query(savings_query, conn, params=(account_id,))
        
        if savings_df.empty:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        # Calculate current balance from transactions
        balance_query = """
        SELECT SUM(amount) as current_balance
        FROM transactions 
        WHERE account_id = %s
        """
        balance_df = pd.read_sql_query(balance_query, conn, params=(account_id,))
        
        if balance_df.empty or pd.isna(balance_df['current_balance'].iloc[0]):
            raise HTTPException(status_code=404, detail="No transaction history found")
        
        # Get transactions (last 30 days for rolling features)
        transactions_query = """
        SELECT amount, date, merchant_name, category, account_id
        FROM transactions 
        WHERE account_id = %s 
        AND date >= CURRENT_DATE - INTERVAL '30 days'
        ORDER BY date DESC
        """
        transactions_df = pd.read_sql_query(transactions_query, conn, params=(account_id,))
        
        if transactions_df.empty:
            raise HTTPException(status_code=404, detail="No recent transactions found")
        
        return {
            'monthly_income': float(monthly_income),
            'suggested_savings': float(savings_df['goal_amount'].iloc[0]),
            'current_balance': float(balance_df['current_balance'].iloc[0]),
            'transactions': transactions_df
        }


def preprocess_features(base_data):
    """Transform base features into the format expected by the model."""
    transactions = base_data['transactions']
    
    if transactions.empty:
        raise HTTPException(status_code=404, detail="No transactions for feature extraction")
    
    # Convert date column and sort
    transactions['date'] = pd.to_datetime(transactions['date'])
    transactions = transactions.sort_values('date', ascending=False)
    
    # Get most recent transaction for current features
    latest_txn = transactions.iloc[0]
    
    # Calculate features
    features = {}
    
    # Basic transaction features
    features['amount'] = float(latest_txn['amount'])
    features['days_since_txn'] = (datetime.now() - latest_txn['date']).days
    features['is_income'] = 1 if latest_txn['amount'] > 0 else 0
    
    # Encode merchant category (simplified encoding)
    category_map = {
        'groceries': 1, 'restaurants': 2, 'gas': 3, 'shopping': 4,
        'entertainment': 5, 'bills': 6, 'transfer': 7, 'food & dining': 2,
        'transportation': 3, 'retail': 4
    }
    category = (latest_txn['category'] if pd.notna(latest_txn['category']) 
                else 'other')
    features['merchant_category'] = category_map.get(category.lower(), 0)
    
    # 30-day rolling features
    amounts = transactions['amount'].astype(float)
    
    features['total_spent_30d'] = float(amounts[amounts < 0].sum() * -1)
    features['total_income_30d'] = float(amounts[amounts > 0].sum())
    features['txn_count_30d'] = len(transactions)
    features['avg_txn_amt_30d'] = float(amounts.mean())
    features['std_txn_amt_30d'] = (float(amounts.std()) 
                                 if len(amounts) > 1 else 0.0)
    features['net_cash_flow_30d'] = (features['total_income_30d'] - 
                                   features['total_spent_30d'])
    
    # User profile features
    features['monthly_income'] = float(base_data['monthly_income'])
    features['suggested_savings'] = float(base_data['suggested_savings'])
    features['balance_at_txn_time'] = float(base_data['current_balance'])
    features['savings_delta'] = (features['balance_at_txn_time'] - 
                               features['suggested_savings'])
    
    # Handle any NaN values
    for key, value in features.items():
        if pd.isna(value):
            features[key] = 0.0
    
    return features


def features_to_array(features):
    """Convert features dict to numpy array for model input."""
    # Order should match your training data
    feature_order = [
        'amount', 'days_since_txn', 'merchant_category', 'is_income',
        'total_spent_30d', 'total_income_30d', 'txn_count_30d',
        'avg_txn_amt_30d', 'std_txn_amt_30d', 'net_cash_flow_30d',
        'monthly_income', 'suggested_savings', 'balance_at_txn_time',
        'savings_delta'
    ]
    
    return np.array([features[key] for key in feature_order]).reshape(1, -1)


class DatabaseManager:
    def __init__(self):
        self.db_config = DB_CONFIG
    
    def get_connection(self):
        """Get database connection"""
        conn = psycopg2.connect(**self.db_config)
        return conn
    
    # User operations
    def create_user(self, user: User) -> int:
        """Create a new user and return user_id"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (name, email, created_at, financial_goal, 
                                 impulse_triggers, budgeting_score, plaid_token)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING user_id
            ''', (
                user.name, user.email, user.created_at, user.financial_goal,
                json.dumps(user.impulse_triggers), user.budgeting_score, 
                user.plaid_token
            ))
            
            user_id = cursor.fetchone()[0]
            conn.commit()
            conn.close()
            return user_id
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return User(
                    user_id=row[0],
                    email=row[1],
                    password_hash=row[2],
                    created_at=str(row[3]),
                    name=row[4],
                    financial_goal=row[5],
                    impulse_triggers=json.loads(row[6]) if row[6] else [],
                    budgeting_score=row[7],
                    plaid_token=row[8] or ""
                )
            else:
                raise HTTPException(status_code=404, detail="User not found")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting user: {e}")
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                # Handle impulse_triggers JSON parsing safely
                impulse_triggers = []
                if row[5]:  # impulse_triggers column
                    try:
                        impulse_triggers = json.loads(row[5])
                    except (json.JSONDecodeError, TypeError):
                        # Handle case where impulse_triggers is not valid JSON
                        impulse_triggers = []
                
                return User(
                    user_id=row[0],
                    name=row[1] or "Unknown User",
                    email=row[2],
                    created_at=row[3],
                    financial_goal=row[4] or "GOAL_SAVINGS",
                    impulse_triggers=impulse_triggers,
                    budgeting_score=row[6] or 2,
                    plaid_token=row[7] or ""
                )
            return None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    # Goal operations
    def create_goal(self, goal: Goal) -> int:
        """Create a new goal and return goal_id"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO goals (user_id, goal_name, goal_description, goal_amount, target_date, net_monthly_income, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING goal_id
            ''', (
                goal.user_id, goal.goal_name, goal.goal_description, goal.goal_amount, goal.target_date, 
                goal.net_monthly_income, goal.created_at
            ))
            
            goal_id = cursor.fetchone()[0]
            conn.commit()
            conn.close()
            return goal_id
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating goal: {e}")
    
    def get_user_goals(self, user_id: int) -> List[Goal]:
        """Get all goals for a user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM goals WHERE user_id = %s', (user_id,))
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                raise HTTPException(status_code=404, detail="No goals found for user")
            
            goals = []
            for row in rows:
                goals.append(Goal(
                    goal_id=row[0],
                    user_id=row[1],
                    goal_name=row[2],
                    goal_description=row[3],
                    goal_amount=row[4],
                    target_date=row[5],
                    net_monthly_income=row[6],
                    created_at=row[7]
                ))
            return goals
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting goals: {e}")
    
    # Bank Account operations
    def create_bank_account(self, account: BankAccount) -> int:
        """Create a new bank account and return account_id"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO bank_accounts (user_id, bank_name, account_type)
                VALUES (%s, %s, %s) RETURNING account_id
            ''', (account.user_id, account.bank_name, account.account_type))
            
            account_id = cursor.fetchone()[0]
            conn.commit()
            conn.close()
            return account_id
        except Exception as e:
            print(f"Error creating bank account: {e}")
            return None
    
    def get_user_bank_accounts(self, user_id: int) -> List[BankAccount]:
        """Get all bank accounts for a user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM bank_accounts WHERE user_id = %s', 
                         (user_id,))
            rows = cursor.fetchall()
            conn.close()
            
            accounts = []
            for row in rows:
                accounts.append(BankAccount(
                    account_id=row[0],
                    user_id=row[1],
                    bank_name=row[2],
                    account_type=row[3]
                ))
            return accounts
        except Exception as e:
            print(f"Error getting bank accounts: {e}")
            return []
    
    # Transaction operations
    def create_transaction(self, transaction: Transaction) -> int:
        """Create a new transaction and return transaction_id"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO transactions (
                    account_id, amount, date, merchant_name, category, 
                    description, mcc, local_time_bucket, rolling_spend_window, 
                    day_of_week, is_weekend, rolling_spend_7d, 
                    category_frequency, category_variance
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                         %s, %s) RETURNING transaction_id
            ''', (
                transaction.account_id, transaction.amount, transaction.date,
                transaction.merchant_name, transaction.category, 
                transaction.description, transaction.mcc, 
                transaction.local_time_bucket, transaction.rolling_spend_window,
                transaction.day_of_week, transaction.is_weekend, 
                transaction.rolling_spend_7d, transaction.category_frequency, 
                transaction.category_variance
            ))
            
            transaction_id = cursor.fetchone()[0]
            conn.commit()
            conn.close()
            return transaction_id
        except Exception as e:
            print(f"Error creating transaction: {e}")
            return None
    
    def get_user_transactions(self, user_id: int, start_date: str = None, 
                            end_date: str = None, 
                            limit: int = None) -> List[Transaction]:
        """Get user transactions within date range"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = '''
                SELECT t.* FROM transactions t
                WHERE t.user_id = %s
            '''
            params = [user_id]
            
            if start_date:
                query += ' AND t.date >= %s'
                params.append(start_date)
            
            if end_date:
                query += ' AND t.date <= %s'
                params.append(end_date)
            
            query += ' ORDER BY t.date DESC'
            
            if limit:
                query += ' LIMIT %s'
                params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                raise HTTPException(status_code=404, detail="No transactions found")
            
            transactions = []
            for row in rows:
                transactions.append(Transaction(
                    transaction_id=row[0],
                    account_id=row[1],
                    user_id=row[2],
                    amount=row[3],
                    date=row[4],
                    merchant_name=row[5],
                    category=row[6],
                    mcc=row[7]
                    # row[8] is created_at, not needed for Transaction object
                ))
            
            return transactions
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting transactions: {e}")
    
    def get_spending_by_category(self, user_id: int, 
                               start_date: str = None) -> Dict[str, float]:
        """Get spending grouped by category"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = '''
                SELECT t.category, SUM(ABS(t.amount)) as total
                FROM transactions t
                WHERE t.user_id = %s AND t.amount < 0
            '''
            params = [user_id]
            
            if start_date:
                query += ' AND t.date >= %s'
                params.append(start_date)
            
            query += ' GROUP BY t.category ORDER BY total DESC'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            return {row[0]: row[1] for row in rows}
        except Exception as e:
            print(f"Error getting spending by category: {e}")
            return {}
    
    # Legacy compatibility methods
    def save_user_goal(self, goal_data) -> bool:
        """Legacy compatibility method"""
        try:
            new_goal = Goal(
                goal_id=0,  # Will be auto-generated
                user_id=5,  # Updated to match existing data
                goal_amount=goal_data.goal_amount,
                goal_name=goal_data.goal_name,
                goal_description=goal_data.goal_description,
                target_date=goal_data.target_date,
                net_monthly_income=goal_data.net_monthly_income,
                created_at=goal_data.created_at
            )
            goal_id = self.create_goal(new_goal)
            return goal_id is not None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in save_user_goal: {e}")
    
    def get_user_goal(self, user_id_str: str):
        """Legacy compatibility method"""
        try:
            goals = self.get_user_goals(5)  # Updated to match existing data
            if goals:
                goal = goals[0]
                from types import SimpleNamespace
                return SimpleNamespace(
                    goal_name=goal.goal_name,
                    goal_amount=goal.goal_amount,
                    target_date=goal.target_date,
                    net_monthly_income=goal.net_monthly_income
                )
            else:
                raise HTTPException(status_code=404, detail="No goals found")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in get_user_goal: {e}")

    def get_user_quiz_responses(self, user_id_str: str) -> Optional[Dict]:
        """Get user's quiz responses for AI agents"""
        try:
            user_id = 5  # Updated to match existing data in database
            
            user = self.get_user(user_id)
            if user:
                quiz_responses = {
                    "financial_goal": user.financial_goal,
                    "impulse_triggers": user.impulse_triggers,
                    "budgeting_score": user.budgeting_score,
                    "name": user.name,
                    "email": user.email
                }
                
                goals = self.get_user_goals(user_id)
                if goals:
                    goal = goals[0]
                    quiz_responses.update({
                        "goal_name": goal.goal_name,
                        "goal_amount": goal.goal_amount,
                        "target_date": goal.target_date,
                        "goal_description": goal.goal_description,
                        "net_monthly_income": goal.net_monthly_income or 6000.0
                    })
                
                return quiz_responses
            
            return {
                "financial_goal": "GOAL_SAVINGS",
                "impulse_triggers": ["Stress", "FOMO"],
                "budgeting_score": 2,
                "goal_name": "Emergency Fund",
                "goal_amount": 5000.0,
                "target_date": "2025-12-31",
                "goal_description": "Build emergency savings",
                "name": "Test User",
                "email": "test@example.com",
                "net_monthly_income": 5000.0
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting user quiz responses: {e}") 

    def create_weekly_plan(self, weekly_plan: WeeklyPlan) -> int:
        """Create a new weekly plan and return weekly_plan_id"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO weekly_plans (
                    user_id, week_start_date, week_end_date, plan_data, 
                    ml_features, created_at, is_active
                ) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING weekly_plan_id
            ''', (
                weekly_plan.user_id, weekly_plan.week_start_date, 
                weekly_plan.week_end_date, weekly_plan.plan_data,
                weekly_plan.ml_features, weekly_plan.created_at, 
                weekly_plan.is_active
            ))
            
            weekly_plan_id = cursor.fetchone()[0]
            conn.commit()
            conn.close()
            return weekly_plan_id
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating weekly plan: {e}")
    
    def get_current_weekly_plan(self, user_id: int, current_date: str):
        """Get current active weekly plan for user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM weekly_plans 
                WHERE user_id = %s 
                AND is_active = true 
                AND %s BETWEEN week_start_date AND week_end_date
                ORDER BY created_at DESC LIMIT 1
            ''', (user_id, current_date))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return WeeklyPlan(
                    weekly_plan_id=row[0],
                    user_id=row[1],
                    week_start_date=str(row[2]),
                    week_end_date=str(row[3]),
                    plan_data=row[4],
                    ml_features=row[5],
                    created_at=str(row[6]),
                    is_active=row[7]
                )
            return None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting current weekly plan: {e}")
    
    def get_weekly_plan_by_week(self, user_id: int, week_start: str):
        """Get weekly plan by week start date"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM weekly_plans 
                WHERE user_id = %s AND week_start_date = %s
                ORDER BY created_at DESC LIMIT 1
            ''', (user_id, week_start))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return WeeklyPlan(
                    weekly_plan_id=row[0],
                    user_id=row[1],
                    week_start_date=str(row[2]),
                    week_end_date=str(row[3]),
                    plan_data=row[4],
                    ml_features=row[5],
                    created_at=str(row[6]),
                    is_active=row[7]
                )
            return None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting weekly plan by week: {e}")
    
    def deactivate_old_weekly_plans(self, user_id: int, new_week_start: str):
        """Deactivate old weekly plans for user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE weekly_plans 
                SET is_active = false 
                WHERE user_id = %s AND week_start_date != %s
            ''', (user_id, new_week_start))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deactivating old plans: {e}")


# FastAPI endpoints for anomaly detection
@app.post("/predict_anomaly", response_model=AnomalyResponse)
async def predict_anomaly(request: AnomalyRequest):
    """Predict anomaly for given account."""
    try:
        # Load model
        model = load_model()
        
        # Get base features from database
        base_data = get_base_features(request.account_id)
        
        # Preprocess into model features
        features = preprocess_features(base_data)
        
        # Convert to array for model
        X = features_to_array(features)
        
        # Get predictions
        anomaly_score = float(model.decision_function(X)[0])
        prediction = model.predict(X)[0]
        is_anomaly = bool(prediction == -1)  # Isolation Forest: -1 = anomaly
        
        return AnomalyResponse(
            anomaly_score=anomaly_score,
            is_anomaly=is_anomaly,
            features=features
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, 
                          detail=f"Prediction failed: {str(e)}")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "postgresql"}


# Global database instance
db = DatabaseManager()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 