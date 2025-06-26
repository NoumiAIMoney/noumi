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
    name: str
    email: str
    created_at: str
    financial_goal: str  # e.g., 'GOAL_DEBT', 'GOAL_EFUND'
    impulse_triggers: List[str]  # e.g., ['Stress', 'FOMO', 'Boredom']
    budgeting_score: int  # 1 = sticks to budgets, 3 = budgets stress me out
    plaid_token: str  # Encrypted Plaid access token for bank connections


@dataclass
class Goal:
    goal_id: int
    user_id: int
    amount: float
    purpose: str  # e.g., 'Pay off credit card', 'Save for a move'
    deadline: str  # date
    created_at: str


@dataclass
class BankAccount:
    account_id: int
    user_id: int
    bank_name: str  # e.g., 'Chase', 'Bank of America'
    account_type: str  # e.g., 'Checking', 'Savings'


@dataclass
class Transaction:
    transaction_id: int
    account_id: int
    amount: float
    date: str
    merchant_name: str
    category: str  # e.g., 'Retail', 'Dining'
    description: str
    mcc: int  # Merchant Category Code for ML processing
    local_time_bucket: str  # e.g., 'Evening', for spending context
    rolling_spend_window: float  # Rolling spend window for ML enrichment
    day_of_week: str  # e.g., 'Monday', 'Tuesday'
    is_weekend: bool  # True if Saturday/Sunday
    rolling_spend_7d: float  # 7-day rolling spend for this user/category
    category_frequency: float  # Frequency of transactions in category
    category_variance: float  # Variance of spending in this category


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
        # Convert account_id to integer for proper type matching
        account_id_int = int(account_id)
        
        # Get user data with monthly income from goals table
        user_query = """
        SELECT u.user_id, COALESCE(g.net_monthly_income, 5000.0) as monthly_income 
        FROM users u 
        JOIN bank_accounts ba ON u.user_id = ba.user_id 
        LEFT JOIN goals g ON u.user_id = g.user_id
        WHERE ba.account_id = %s
        LIMIT 1
        """
        user_df = pd.read_sql_query(user_query, conn, 
                                   params=(account_id_int,))
        
        # Get suggested savings amount (from goals table)
        savings_query = """
        SELECT g.goal_amount as suggested_savings_amount 
        FROM goals g
        JOIN bank_accounts ba ON g.user_id = ba.user_id 
        WHERE ba.account_id = %s 
        ORDER BY g.created_at DESC LIMIT 1
        """
        savings_df = pd.read_sql_query(savings_query, conn, 
                                      params=(account_id_int,))
        
        # Calculate current balance from transactions
        balance_query = """
        SELECT COALESCE(SUM(amount), 0) as current_balance
        FROM transactions 
        WHERE account_id = %s
        """
        balance_df = pd.read_sql_query(balance_query, conn, 
                                      params=(account_id_int,))
        
        # Get transactions (last 30 days for rolling features)
        transactions_query = """
        SELECT amount, date, merchant_name, category, account_id
        FROM transactions 
        WHERE account_id = %s 
        AND date >= CURRENT_DATE - INTERVAL '30 days'
        ORDER BY date DESC
        """
        transactions_df = pd.read_sql_query(transactions_query, conn, 
                                          params=(account_id_int,))
        
        return {
            'monthly_income': (user_df['monthly_income'].iloc[0] 
                             if not user_df.empty else 5000.0),
            'suggested_savings': (
                savings_df['suggested_savings_amount'].iloc[0] 
                if not savings_df.empty else 1000.0),
            'current_balance': (balance_df['current_balance'].iloc[0] 
                              if not balance_df.empty else 0.0),
            'transactions': transactions_df
        }


def preprocess_features(base_data):
    """Transform base features into the format expected by the model."""
    transactions = base_data['transactions']
    
    if transactions.empty:
        # Return default features if no transactions
        return {
            'amount': 0.0,
            'days_since_txn': 0,
            'merchant_category': 0,  # Encoded
            'is_income': 0,
            'total_spent_30d': 0.0,
            'total_income_30d': 0.0,
            'txn_count_30d': 0,
            'avg_txn_amt_30d': 0.0,
            'std_txn_amt_30d': 0.0,
            'net_cash_flow_30d': 0.0,
            'monthly_income': base_data['monthly_income'],
            'suggested_savings': base_data['suggested_savings'],
            'balance_at_txn_time': base_data['current_balance'],
            'savings_delta': (base_data['current_balance'] - 
                            base_data['suggested_savings'])
        }
    
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
            
            cursor.execute('SELECT * FROM users WHERE user_id = %s', 
                         (user_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return User(
                    user_id=row[0],
                    name=row[1],
                    email=row[2],
                    created_at=row[3],
                    financial_goal=row[4],
                    impulse_triggers=json.loads(row[5]) if row[5] else [],
                    budgeting_score=row[6],
                    plaid_token=row[7]
                )
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
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
            
            # Map Goal dataclass fields to actual PostgreSQL column names
            cursor.execute('''
                INSERT INTO goals (user_id, goal_amount, goal_name, target_date, 
                                 created_at)
                VALUES (%s, %s, %s, %s, %s) RETURNING goal_id
            ''', (
                goal.user_id, goal.amount, goal.purpose, goal.deadline, 
                goal.created_at
            ))
            
            goal_id = cursor.fetchone()[0]
            conn.commit()
            conn.close()
            return goal_id
        except Exception as e:
            print(f"Error creating goal: {e}")
            return None
    
    def get_user_goals(self, user_id: int) -> List[Goal]:
        """Get all goals for a user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT goal_id, user_id, goal_amount, goal_name, target_date, created_at 
                FROM goals 
                WHERE user_id = %s 
                ORDER BY created_at DESC
            ''', (user_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            goals = []
            for row in rows:
                goals.append(Goal(
                    goal_id=row[0],
                    user_id=row[1],
                    amount=row[2],      # goal_amount -> amount
                    purpose=row[3],     # goal_name -> purpose
                    deadline=row[4],    # target_date -> deadline
                    created_at=row[5]
                ))
            return goals
        except Exception as e:
            print(f"Error getting goals: {e}")
            return []
    
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
                JOIN bank_accounts ba ON t.account_id = ba.account_id
                WHERE ba.user_id = %s
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
            
            transactions = []
            for row in rows:
                transactions.append(Transaction(
                    transaction_id=row[0],
                    account_id=row[1],
                    amount=row[2],
                    date=row[3],
                    merchant_name=row[4],
                    category=row[5],
                    description=row[6],
                    mcc=row[7],
                    local_time_bucket=row[8],
                    rolling_spend_window=row[9],
                    day_of_week=row[10],
                    is_weekend=bool(row[11]),
                    rolling_spend_7d=row[12],
                    category_frequency=row[13],
                    category_variance=row[14]
                ))
            
            return transactions
        except Exception as e:
            print(f"Error getting transactions: {e}")
            return []
    
    def get_spending_by_category(self, user_id: int, 
                               start_date: str = None) -> Dict[str, float]:
        """Get spending grouped by category"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = '''
                SELECT t.category, SUM(ABS(t.amount)) as total
                FROM transactions t
                JOIN bank_accounts ba ON t.account_id = ba.account_id
                WHERE ba.user_id = %s AND t.amount < 0
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
                user_id=1,  # Default user for migration
                amount=goal_data.goal_amount,
                purpose=goal_data.goal_name,
                deadline=goal_data.target_date,
                created_at=goal_data.created_at
            )
            goal_id = self.create_goal(new_goal)
            return goal_id is not None
        except Exception as e:
            print(f"Error in legacy save_user_goal: {e}")
            return False
    
    def get_user_goal(self, user_id_str: str):
        """Legacy compatibility method"""
        try:
            goals = self.get_user_goals(1)
            if goals:
                goal = goals[0]
                from types import SimpleNamespace
                return SimpleNamespace(
                    goal_name=goal.purpose,
                    goal_amount=goal.amount,
                    target_date=goal.deadline,
                    net_monthly_income=5000.0
                )
            return None
        except Exception as e:
            print(f"Error in legacy get_user_goal: {e}")
            return None

    def get_user_quiz_responses(self, user_id_str: str) -> Optional[Dict]:
        """Get user's quiz responses for AI agents"""
        try:
            user_id = 1  # Default user for testing
            
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
                        "goal_name": goal.purpose,
                        "goal_amount": goal.amount,
                        "target_date": goal.deadline,
                        "goal_description": goal.purpose
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
                "email": "test@example.com"
            }
            
        except Exception as e:
            print(f"Error getting user quiz responses: {e}")
            return {
                "financial_goal": "GOAL_SAVINGS",
                "impulse_triggers": ["Stress", "FOMO"],
                "budgeting_score": 2,
                "goal_name": "Emergency Fund",
                "goal_amount": 5000.0,
                "target_date": "2025-12-31",
                "goal_description": "Build emergency savings",
                "name": "Test User",
                "email": "test@example.com"
            }


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