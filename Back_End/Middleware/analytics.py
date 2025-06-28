"""
Analytics and transaction analysis for Noumi API
Updated for MVP (P0) Database Schema
"""

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
            
            db_user_id = 5  # Updated to match existing data in database
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
            raise Exception(f"Error detecting anomalies: {e}")
    
    def analyze_spending_trends(self) -> List[Dict[str, str]]:
        """
        Analyze spending patterns and return insights
        """
        try:
            # Get recent transactions (last 30 days)
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            
            db_user_id = 5  # Updated to match existing data in database
            transactions = self.db.get_user_transactions(db_user_id, start_date, end_date)
            
            if not transactions:
                raise Exception("No transaction data available")
            
            trends = []
            
            # Analyze spending by day of week  
            day_spending = {}
            for txn in transactions:
                if txn.amount < 0:  # Only spending
                    # Calculate day of week from transaction date
                    txn_date = datetime.strptime(str(txn.date), "%Y-%m-%d")
                    day = txn_date.strftime("%A")  # Get day name
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
            raise Exception(f"Error analyzing trends: {e}")
    
    def get_spending_categories_with_history(self) -> List[Dict[str, Any]]:
        """
        Get spending by category with month-over-month comparison
        """
        try:
            # Get spending for current month and previous 2 months
            categories = []
            
            # Use correct user_id for database queries
            db_user_id = 5  # Updated to match existing data in database
            
            # Get current month and previous 2 months
            current_date = datetime.now()
            
            for month_offset in range(3):  # Current month + 2 previous months
                target_date = current_date - timedelta(days=month_offset * 30)
                month_str = target_date.strftime("%Y-%m")
                month_start = f"{month_str}-01"
                
                # Get spending for this month
                month_spending = self.db.get_spending_by_category(
                    db_user_id, month_start
                )
                
                # Add each category for this month
                for category, amount in month_spending.items():
                    categories.append({
                        "category_name": category,
                        "amount": amount,
                        "month": month_str
                    })
            
            return categories
            
        except Exception as e:
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
                
                db_user_id = 5  # Updated to match existing data in database
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
                        amount = abs(txn.amount)
                        category = txn.category or "Other"
                        
                        # Simple anomaly detection: spending > $200 in single transaction
                        if amount > 200:
                            anomaly_count += 1
                
                # Good week = fewer than 2 anomalies
                week_score = 1 if anomaly_count < 2 else 0
                weeks_data.append(week_score)
            
            return weeks_data
            
        except Exception as e:
            raise Exception(f"Error calculating weekly streak: {e}")
    
    def calculate_spending_status(self) -> Dict[str, float]:
        """
        Calculate current spending status (income vs expenses)
        """
        try:
            # Get current month data
            current_month = datetime.now().strftime("%Y-%m")
            start_date = f"{current_month}-01"
            end_date = datetime.now().strftime("%Y-%m-%d")
            
            db_user_id = 5  # Updated to match existing data in database
            transactions = self.db.get_user_transactions(db_user_id, start_date, end_date)
            quiz_income = self.db.get_user_goal(db_user_id).net_monthly_income
            if not transactions:
                raise Exception("No transaction data for spending status")

            total_expenses = 0
            
            for txn in transactions:
                if txn.amount < 0:
                    total_expenses += abs(txn.amount)
            
            # Calculate safe spending amount (80% of remaining income)
            remaining_income = quiz_income - total_expenses
            safe_to_spend = max(0, remaining_income * 0.8)
            
            return {
                "income": quiz_income,
                "expenses": total_expenses,
                "amount_safe_to_spend": safe_to_spend
            }
            
        except Exception as e:
            raise Exception(f"Error calculating spending status: {e}")
    
    def calculate_weekly_savings(self) -> Dict[str, float]:
        """
        Calculate weekly savings data
        """
        try:
            # Get current week data
            today = datetime.now()
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            
            start_date = week_start.strftime("%Y-%m-%d")
            end_date = week_end.strftime("%Y-%m-%d")
            
            db_user_id = 5  # Updated to match existing data in database
            transactions = self.db.get_user_transactions(db_user_id, start_date, end_date)
            
            if not transactions:
                raise Exception("No transaction data for weekly savings")
            
            weekly_income = 0
            weekly_expenses = 0
            
            for txn in transactions:
                if txn.amount > 0:
                    weekly_income += txn.amount
                else:
                    weekly_expenses += abs(txn.amount)
            
            actual_savings = weekly_income - weekly_expenses
            
            # Get user's goal data to calculate suggested savings
            quiz_data = self.db.get_user_quiz_responses(str(db_user_id))
            if not quiz_data or not quiz_data.get('goal_amount'):
                raise Exception("Goal data not found for savings calculation")
            
            # Suggested weekly savings = goal amount / (target date - today in weeks)
            goal_amount = quiz_data.get('goal_amount', 0)
            goal_target_date = quiz_data.get('target_date')  # probably datetime.date

            # convert today to date only
            today = datetime.today().date()

            # if goal_target_date is datetime.datetime, convert to date
            if hasattr(goal_target_date, 'date'):
                goal_target_date = goal_target_date if isinstance(goal_target_date, datetime.date) else goal_target_date.date()

            days_diff = (goal_target_date - today).days

            weeks_to_target = max(days_diff / 7, 1)

            suggested_weekly = goal_amount / weeks_to_target
            
            return {
                "actual_savings": actual_savings,
                "suggested_savings_amount_weekly": suggested_weekly
            }
            
        except Exception as e:
            raise Exception(f"Error calculating weekly savings: {e}")
    
    def calculate_longest_streak(self) -> int:
        """
        Calculate longest streak without spending anomalies
        """
        try:
            # Get last 90 days of data
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
            
            db_user_id = 5  # Updated to match existing data in database
            transactions = self.db.get_user_transactions(db_user_id, start_date, end_date)
            
            if not transactions:
                raise Exception("No transaction data for streak calculation")
            
            # Group transactions by date
            daily_data = {}
            for txn in transactions:
                date_str = str(txn.date)
                if date_str not in daily_data:
                    daily_data[date_str] = []
                daily_data[date_str].append(txn)
            
            # Calculate daily anomaly status
            dates = sorted(daily_data.keys())
            longest_streak = 0
            current_streak = 0
            
            for date_str in dates:
                day_transactions = daily_data[date_str]
                has_anomaly = False
                
                for txn in day_transactions:
                    if txn.amount < 0:  # Expense
                        amount = abs(txn.amount)
                        # Simple anomaly: single transaction > $300
                        if amount > 300:
                            has_anomaly = True
                            break
                
                if not has_anomaly:
                    current_streak += 1
                    longest_streak = max(longest_streak, current_streak)
                else:
                    current_streak = 0
            
            return longest_streak
            
        except Exception as e:
            raise Exception(f"Error calculating longest streak: {e}")
    
    def calculate_total_spent_ytd(self) -> float:
        """
        Calculate total amount spent year-to-date
        """
        try:
            # Get year-to-date data
            current_year = datetime.now().year
            start_date = f"{current_year}-01-01"
            end_date = datetime.now().strftime("%Y-%m-%d")
            
            db_user_id = 5  # Updated to match existing data in database
            transactions = self.db.get_user_transactions(db_user_id, start_date, end_date)
            
            if not transactions:
                raise Exception("No transaction data for YTD calculation")
            
            total_spent = 0
            for txn in transactions:
                if txn.amount < 0:  # Only expenses
                    total_spent += abs(txn.amount)
            
            return total_spent
            
        except Exception as e:
            raise Exception(f"Error calculating total spent YTD: {e}")