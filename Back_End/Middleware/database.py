"""
Database utilities and models for Noumi API
Handles user data, transactions, goals, and analytics
"""

import sqlite3
import json
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import os

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), "noumi.db")

@dataclass
class User:
    id: str
    email: str
    name: str
    created_at: str
    preferences: Dict[str, Any] = None

@dataclass
class UserGoal:
    user_id: str
    goal_name: str
    goal_description: str
    goal_amount: float
    target_date: str
    net_monthly_income: float
    created_at: str

@dataclass
class Transaction:
    transaction_id: str
    user_id: str
    account_id: str
    amount: float
    date: str
    description: str
    category: str
    merchant_name: str
    created_at: str

@dataclass
class PlaidConnection:
    user_id: str
    access_token: str
    accounts: List[Dict[str, Any]]
    connected_at: str

class DatabaseManager:
    def __init__(self):
        self.db_path = DB_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                preferences TEXT DEFAULT '{}'
            )
        ''')
        
        # User goals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_goals (
                user_id TEXT NOT NULL,
                goal_name TEXT NOT NULL,
                goal_description TEXT,
                goal_amount REAL NOT NULL,
                target_date TEXT NOT NULL,
                net_monthly_income REAL NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (user_id, goal_name),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                account_id TEXT NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                merchant_name TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Plaid connections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plaid_connections (
                user_id TEXT PRIMARY KEY,
                access_token TEXT NOT NULL,
                accounts TEXT NOT NULL,
                connected_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Weekly plans table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weekly_plans (
                user_id TEXT NOT NULL,
                week_start TEXT NOT NULL,
                plan_data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (user_id, week_start),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Weekly recaps table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weekly_recaps (
                user_id TEXT NOT NULL,
                week_start TEXT NOT NULL,
                recap_data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (user_id, week_start),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    # User operations
    def create_user(self, user: User) -> bool:
        """Create a new user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (id, email, name, created_at, preferences)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                user.id, user.email, user.name, user.created_at,
                json.dumps(user.preferences or {})
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return User(
                    id=row[0],
                    email=row[1],
                    name=row[2],
                    created_at=row[3],
                    preferences=json.loads(row[4]) if row[4] else {}
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
            
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return User(
                    id=row[0],
                    email=row[1],
                    name=row[2],
                    created_at=row[3],
                    preferences=json.loads(row[4]) if row[4] else {}
                )
            return None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    # Goal operations
    def save_user_goal(self, goal: UserGoal) -> bool:
        """Save or update user goal"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_goals 
                (user_id, goal_name, goal_description, goal_amount, target_date, 
                 net_monthly_income, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                goal.user_id, goal.goal_name, goal.goal_description,
                goal.goal_amount, goal.target_date, goal.net_monthly_income,
                goal.created_at
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving goal: {e}")
            return False
    
    def get_user_goal(self, user_id: str) -> Optional[UserGoal]:
        """Get most recent user goal"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM user_goals 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT 1
            ''', (user_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return UserGoal(
                    user_id=row[0],
                    goal_name=row[1],
                    goal_description=row[2],
                    goal_amount=row[3],
                    target_date=row[4],
                    net_monthly_income=row[5],
                    created_at=row[6]
                )
            return None
        except Exception as e:
            print(f"Error getting goal: {e}")
            return None
    
    # Transaction operations
    def save_transactions(self, transactions: List[Transaction]) -> bool:
        """Save multiple transactions"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            for txn in transactions:
                cursor.execute('''
                    INSERT OR REPLACE INTO transactions 
                    (transaction_id, user_id, account_id, amount, date, 
                     description, category, merchant_name, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    txn.transaction_id, txn.user_id, txn.account_id,
                    txn.amount, txn.date, txn.description, txn.category,
                    txn.merchant_name, txn.created_at
                ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving transactions: {e}")
            return False
    
    def get_user_transactions(self, user_id: str, start_date: str = None, 
                            end_date: str = None) -> List[Transaction]:
        """Get user transactions within date range"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = 'SELECT * FROM transactions WHERE user_id = ?'
            params = [user_id]
            
            if start_date:
                query += ' AND date >= ?'
                params.append(start_date)
            
            if end_date:
                query += ' AND date <= ?'
                params.append(end_date)
            
            query += ' ORDER BY date DESC'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            transactions = []
            for row in rows:
                transactions.append(Transaction(
                    transaction_id=row[0],
                    user_id=row[1],
                    account_id=row[2],
                    amount=row[3],
                    date=row[4],
                    description=row[5],
                    category=row[6],
                    merchant_name=row[7],
                    created_at=row[8]
                ))
            
            return transactions
        except Exception as e:
            print(f"Error getting transactions: {e}")
            return []
    
    def get_spending_by_category(self, user_id: str, 
                               start_date: str = None) -> Dict[str, float]:
        """Get spending grouped by category"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = '''
                SELECT category, SUM(ABS(amount)) as total
                FROM transactions 
                WHERE user_id = ? AND amount < 0
            '''
            params = [user_id]
            
            if start_date:
                query += ' AND date >= ?'
                params.append(start_date)
            
            query += ' GROUP BY category ORDER BY total DESC'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            return {row[0]: row[1] for row in rows}
        except Exception as e:
            print(f"Error getting spending by category: {e}")
            return {}
    
    # Plaid operations
    def save_plaid_connection(self, connection: PlaidConnection) -> bool:
        """Save Plaid connection data"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO plaid_connections 
                (user_id, access_token, accounts, connected_at)
                VALUES (?, ?, ?, ?)
            ''', (
                connection.user_id, connection.access_token,
                json.dumps(connection.accounts), connection.connected_at
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving Plaid connection: {e}")
            return False


# Global database instance
db = DatabaseManager() 