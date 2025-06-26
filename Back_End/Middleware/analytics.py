"""
Analytics and transaction analysis for Noumi API
Updated for MVP (P0) Database Schema
"""

import sqlite3
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any
from database import db


class TransactionAnalyzer:
    def __init__(self, user_id: int):
        """Initialize analyzer for a specific user (now uses integer ID)"""
        self.user_id = user_id
        self.db = db
    
    def detect_spending_anomalies(self) -> List[int]:
        """
        Detect spending anomalies with enhanced analysis using enriched data
        """
        try:
            # Get last 60 days of transaction data
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
            
            db_user_id = 1  # Default test user mapping
            transactions = self.db.get_user_transactions(db_user_id, start_date, end_date)
            
            anomalies = []
            
            # Calculate spending patterns by category
            category_stats = {}
            for txn in transactions:
                if txn.amount >= 0:  # Skip income/deposits
                    continue
                    
                category = txn.category
                amount = abs(txn.amount)
                
                if category not in category_stats:
                    category_stats[category] = []
                category_stats[category].append(amount)
            
            # Detect anomalies: transactions > 3x category average
            for txn in transactions:
                if txn.amount >= 0:  # Skip income/deposits
                    continue
                
                category = txn.category
                amount = abs(txn.amount)
                
                if category in category_stats and len(category_stats[category]) > 1:
                    category_amounts = category_stats[category]
                    avg_amount = sum(category_amounts) / len(category_amounts)
                    
                    # Flag as anomaly if > 3x average for that category
                    if amount > (avg_amount * 3):
                        anomalies.append(txn.transaction_id)
            
            return anomalies
            
        except Exception as e:
            print(f"Error detecting anomalies: {e}")
            return []
    
    def analyze_spending_trends(self) -> List[Dict[str, str]]:
        """
        Analyze spending patterns and return insights
        """
        try:
            # Get recent transactions (last 30 days)
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            
            transactions = self.db.get_user_transactions(
                self.user_id, start_date, end_date
            )
            
            if not transactions:
                return [{"icon": "📊", "trend": "No transaction data available"}]
            
            trends = []
            
            # Analyze spending by day of week
            day_spending = {}
            for txn in transactions:
                if txn.amount < 0:  # Only spending
                    day = txn.day_of_week
                    if day not in day_spending:
                        day_spending[day] = 0
                    day_spending[day] += abs(txn.amount)
            
            if day_spending:
                highest_day = max(day_spending, key=day_spending.get)
                highest_amount = day_spending[highest_day]
                trends.append({
                    "icon": "📅",
                    "trend": f"{highest_day} is highest spending day with ${highest_amount:.2f}"
                })
            
            # Analyze merchant patterns
            merchant_spending = {}
            for txn in transactions:
                if txn.amount < 0 and txn.merchant_name:
                    merchant = txn.merchant_name
                    if merchant not in merchant_spending:
                        merchant_spending[merchant] = 0
                    merchant_spending[merchant] += abs(txn.amount)
            
            if merchant_spending:
                top_merchant = max(merchant_spending, key=merchant_spending.get)
                top_amount = merchant_spending[top_merchant]
                trends.append({
                    "icon": "🏪",
                    "trend": f"{top_merchant} top merchant with ${top_amount:.2f}"
                })
            
            # Category analysis
            category_counts = {}
            for txn in transactions:
                if txn.amount < 0:
                    category = txn.category or "Other"
                    category_counts[category] = category_counts.get(category, 0) + 1
            
            if category_counts:
                most_frequent_category = max(category_counts, key=category_counts.get)
                count = category_counts[most_frequent_category]
                trends.append({
                    "icon": "🛍️",
                    "trend": f"{most_frequent_category} most frequent category with {count} transactions"
                })
            
            return trends if trends else [{"icon": "📊", "trend": "Analyzing your spending patterns"}]
            
        except Exception as e:
            print(f"Error analyzing trends: {e}")
            return [{"icon": "❌", "trend": "Unable to analyze spending trends"}]
    
    def get_spending_categories_with_history(self) -> List[Dict[str, Any]]:
        """
        Get spending by category with month-over-month comparison
        """
        try:
            current_month = datetime.now().strftime("%Y-%m")
            
            # Use integer user_id for database queries (compatibility mapping)
            db_user_id = 1  # Default test user mapping
            
            # Get current month spending
            current_spending = self.db.get_spending_by_category(
                db_user_id, f"{current_month}-01"
            )
            
            categories = []
            for category, amount in current_spending.items():
                categories.append({
                    "category_name": category,
                    "amount": amount,
                    "month": current_month
                })
            
            return categories
            
        except Exception as e:
            print(f"Error getting spending categories: {e}")
            raise Exception(f"Error getting spending categories: {e}")
    
    def calculate_weekly_streak(self) -> List[int]:
        """
        Calculate weekly streak based on consistent financial habits and spending control
        """
        try:
            # Get last 8 weeks of data for streak calculation
            weeks_data = []
            
            for week_offset in range(8):
                week_start = datetime.now() - timedelta(days=(week_offset * 7))
                week_start = week_start - timedelta(days=week_start.weekday())  # Get Monday
                week_end = week_start + timedelta(days=6)  # Get Sunday
                
                start_date = week_start.strftime("%Y-%m-%d")
                end_date = week_end.strftime("%Y-%m-%d")
                
                db_user_id = 1  # Default test user mapping
                transactions = self.db.get_user_transactions(db_user_id, start_date, end_date)
                
                if not transactions:
                    weeks_data.append(0)  # No data = no streak
                    continue
                
                # Check for good financial behavior this week
                anomaly_count = 0
                savings_transfers = 0
                daily_spending = {}
                
                for txn in transactions:
                    # Count anomalies (unusually high spending)
                    if txn.amount < 0:  # Expense
                        avg_for_category = 50  # Base average
                        if abs(txn.amount) > (avg_for_category * 3):  # 3x normal = anomaly
                            anomaly_count += 1
                    
                    # Count savings transfers
                    if txn.category == "Transfer" and txn.amount < 0:
                        savings_transfers += 1
                    
                    # Track daily spending for consistency
                    day = txn.date
                    if day not in daily_spending:
                        daily_spending[day] = 0
                    if txn.amount < 0:
                        daily_spending[day] += abs(txn.amount)
                
                # Calculate streak score for this week (1 = good week, 0 = bad week)
                streak_score = 1
                
                # Deduct for anomalies
                if anomaly_count > 2:  # More than 2 anomalies = bad week
                    streak_score = 0
                
                # Deduct for no savings
                if savings_transfers == 0 and week_offset < 4:  # Recent weeks should have savings
                    streak_score = 0
                
                # Deduct for inconsistent spending (very high variance)
                if daily_spending:
                    spending_values = list(daily_spending.values())
                    if len(spending_values) > 1:
                        avg_spending = sum(spending_values) / len(spending_values)
                        if avg_spending > 200:  # Very high daily average
                            streak_score = 0
                
                weeks_data.append(streak_score)
            
            return weeks_data[::-1]  # Return in chronological order
            
        except Exception as e:
            print(f"Error calculating weekly streak: {e}")
            return [0, 0, 0, 0, 0, 0, 0, 0]  # Return 8 weeks of zeros
    
    def calculate_spending_status(self) -> Dict[str, float]:
        """
        Calculate income vs expenses with safety buffer using enriched data
        """
        try:
            # Get user's actual income from quiz responses
            quiz_data = self.db.get_user_quiz_responses(str(self.user_id))
            monthly_income = quiz_data.get("net_monthly_income", 0.0) if quiz_data else 0.0
            
            # If no income data, calculate from actual income transactions
            if monthly_income <= 0:
                # Look for income transactions in the last 30 days
                end_date = datetime.now().strftime("%Y-%m-%d")
                start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
                
                # Get integer user_id for database queries
                db_user_id = 1  # Default test user mapping
                transactions = self.db.get_user_transactions(db_user_id, start_date, end_date)
                
                # Calculate income from positive transactions
                income_transactions = [t for t in transactions if t.amount > 0 and t.category == "Income"]
                if income_transactions:
                    total_monthly_income = sum(t.amount for t in income_transactions)
                    monthly_income = total_monthly_income
                else:
                    # No income found, return zeros
                    return {
                        "income": 0.0,
                        "expenses": 0.0,
                        "amount_safe_to_spend": 0.0
                    }
            
            # Calculate monthly expenses from actual spending
            current_month = datetime.now().strftime("%Y-%m")
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")
            
            # Get integer user_id for database queries
            db_user_id = 1  # Default test user mapping
            transactions = self.db.get_user_transactions(db_user_id, start_date, end_date)
            
            # Calculate expenses (negative amounts, excluding transfers)
            expense_transactions = [t for t in transactions if t.amount < 0 and t.category != "Transfer"]
            monthly_expenses = sum(abs(t.amount) for t in expense_transactions)
            
            # Calculate safe spending amount (income - expenses - 20% safety buffer)
            safety_buffer = monthly_income * 0.2
            amount_safe_to_spend = max(0, monthly_income - monthly_expenses - safety_buffer)
            
            return {
                "income": monthly_income,
                "expenses": monthly_expenses,
                "amount_safe_to_spend": amount_safe_to_spend
            }
            
        except Exception as e:
            print(f"Error calculating spending status: {e}")
            return {
                "income": 0.0,
                "expenses": 0.0,
                "amount_safe_to_spend": 0.0
            }
    
    def calculate_weekly_savings(self) -> Dict[str, float]:
        """
        Calculate actual vs suggested weekly savings using enriched data
        """
        try:
            # Get user's actual income from quiz responses or transactions
            quiz_data = self.db.get_user_quiz_responses(str(self.user_id))
            monthly_income = quiz_data.get("net_monthly_income", 0.0) if quiz_data else 0.0
            
            # If no income data, get from actual income transactions
            if monthly_income <= 0:
                end_date = datetime.now().strftime("%Y-%m-%d")
                start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
                
                db_user_id = 1  # Default test user mapping
                transactions = self.db.get_user_transactions(db_user_id, start_date, end_date)
                
                income_transactions = [t for t in transactions if t.amount > 0 and t.category == "Income"]
                if income_transactions:
                    monthly_income = sum(t.amount for t in income_transactions)
                else:
                    return {
                        "actual_savings": 0.0,
                        "suggested_savings_amount_weekly": 0.0
                    }
            
            # Calculate actual savings from Transfer transactions (last 7 days)
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            
            db_user_id = 1  # Default test user mapping
            transactions = self.db.get_user_transactions(db_user_id, start_date, end_date)
            
            # Look for savings transfers
            savings_transactions = [t for t in transactions if t.category == "Transfer" and t.amount < 0]
            actual_weekly_savings = sum(abs(t.amount) for t in savings_transactions)
            
            # Calculate suggested weekly savings (15% of monthly income / 4 weeks)
            suggested_weekly_savings = (monthly_income * 0.15) / 4
            
            return {
                "actual_savings": actual_weekly_savings,
                "suggested_savings_amount_weekly": suggested_weekly_savings
            }
            
        except Exception as e:
            print(f"Error calculating weekly savings: {e}")
            return {
                "actual_savings": 0.0,
                "suggested_savings_amount_weekly": 0.0
            }
    
    def calculate_longest_streak(self) -> int:
        """
        Calculate longest streak of good financial behavior
        """
        try:
            weekly_streak = self.calculate_weekly_streak()
            
            # Find longest consecutive sequence of 1s
            longest = 0
            current = 0
            
            for week_score in weekly_streak:
                if week_score == 1:
                    current += 1
                    longest = max(longest, current)
                else:
                    current = 0
            
            return longest
            
        except Exception as e:
            print(f"Error calculating longest streak: {e}")
            return 0
    
    def calculate_total_spent_ytd(self) -> float:
        """
        Calculate total amount spent year-to-date
        """
        try:
            current_year = datetime.now().year
            start_date = f"{current_year}-01-01"
            end_date = datetime.now().strftime("%Y-%m-%d")
            
            # Use integer user_id for database queries (compatibility mapping)
            db_user_id = 1  # Default test user mapping
            
            transactions = self.db.get_user_transactions(
                db_user_id, start_date, end_date
            )
            
            total = sum(abs(txn.amount) for txn in transactions if txn.amount < 0)
            return total
            
        except Exception as e:
            print(f"Error calculating total spent: {e}")
            raise Exception(f"Error calculating total spent: {e}")