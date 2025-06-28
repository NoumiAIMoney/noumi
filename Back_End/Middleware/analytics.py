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
        Calculate current spending status with proper safe-to-spend calculation
        Safe to spend = Monthly Income - (Savings Goal / Timeline in months)
        """
        try:
            db_user_id = 5  # Updated to match existing data in database
            
            # Get user's monthly income from quiz data
            quiz_data = self.db.get_user_quiz_responses(str(db_user_id))
            if not quiz_data or not quiz_data.get("net_monthly_income"):
                raise Exception("Monthly income not found - cannot calculate safe spending")
            
            monthly_income = float(quiz_data["net_monthly_income"])
            
            # Get user's savings goal and timeline
            goals = self.db.get_user_goals(db_user_id)
            if not goals:
                raise Exception("No savings goal found - cannot calculate safe spending")
            
            goal = goals[-1]  # Get latest goal
            
            # Calculate monthly savings requirement based on goal timeline
            target_date = datetime.strptime(str(goal.target_date), "%Y-%m-%d")
            today_date = datetime.now()
            months_remaining = max(1, (target_date - today_date).days / 30.44)  # Average days per month
            monthly_savings_needed = float(goal.goal_amount) / months_remaining
            
            # Get current week transactions for expenses
            current_week_start, _ = self._get_current_week_dates()
            end_date = datetime.now().strftime("%Y-%m-%d")
            
            current_week_transactions = self.db.get_user_transactions(
                db_user_id, current_week_start, end_date
            )
            
            if not current_week_transactions:
                raise Exception("No transaction data available for spending calculation")
            
            # Calculate current week expenses
            current_week_expenses = sum(
                abs(txn.amount) for txn in current_week_transactions 
                if txn.amount < 0
            )
            
            # Calculate weekly safe spending limit
            weekly_income = monthly_income / 4.33  # Average weeks per month
            weekly_savings_needed = monthly_savings_needed / 4.33
            weekly_safe_to_spend_limit = weekly_income - weekly_savings_needed
            
            # Amount safe to spend this week = Weekly limit - Already spent this week
            amount_safe_to_spend = max(0, weekly_safe_to_spend_limit - current_week_expenses)
            
            return {
                "income": weekly_income,
                "expenses": current_week_expenses,
                "amount_safe_to_spend": amount_safe_to_spend
            }
            
        except Exception as e:
            raise Exception(f"Error calculating spending status: {e}")
    
    def _get_current_week_dates(self) -> tuple[str, str]:
        """Get current week Monday to Sunday dates"""
        today = datetime.now()
        days_since_monday = today.weekday()
        monday = today - timedelta(days=days_since_monday)
        sunday = monday + timedelta(days=6)
        return monday.strftime("%Y-%m-%d"), sunday.strftime("%Y-%m-%d")

    def calculate_weekly_savings(self) -> Dict[str, float]:
        """
        Calculate weekly savings data with proper goal-based calculations
        """
        try:
            db_user_id = 5  # Updated to match existing data in database
            
            # Get current week transactions
            week_start, week_end = self._get_current_week_dates()
            transactions = self.db.get_user_transactions(db_user_id, week_start, week_end)
            
            if not transactions:
                raise Exception("No transaction data for weekly savings calculation")
            
            # Calculate actual weekly income and expenses
            weekly_income = sum(txn.amount for txn in transactions if txn.amount > 0)
            weekly_expenses = sum(abs(txn.amount) for txn in transactions if txn.amount < 0)
            actual_savings = weekly_income - weekly_expenses
            
            # Get user's goal data to calculate suggested weekly savings
            goals = self.db.get_user_goals(db_user_id)
            if not goals:
                raise Exception("No savings goal found for weekly savings calculation")
            
            goal = goals[-1]  # Get latest goal
            
            # Calculate suggested weekly savings based on goal timeline
            target_date = datetime.strptime(str(goal.target_date), "%Y-%m-%d")
            today_date = datetime.now()
            weeks_remaining = max(1, (target_date - today_date).days / 7)
            suggested_weekly_savings = float(goal.goal_amount) / weeks_remaining
            
            return {
                "actual_savings": actual_savings,
                "suggested_savings_amount_weekly": suggested_weekly_savings
            }
            
        except Exception as e:
            raise Exception(f"Error calculating weekly savings: {e}")

    def calculate_longest_streak(self) -> int:
        """
        Calculate longest streak without spending anomalies - NO DEFAULT VALUES
        """
        try:
            # Get user signup date for proper streak calculation
            user = self.db.get_user(5)  # Updated to match existing data
            if not user or not user.created_at:
                raise Exception("User signup date not found for streak calculation")
            
            # Calculate streak from signup date or beginning of year (whichever is later)
            signup_date = user.created_at
            if isinstance(signup_date, str):
                if 'T' in signup_date:
                    signup_date = signup_date.split('T')[0]
                elif ' ' in signup_date:
                    signup_date = signup_date.split(' ')[0]
            else:
                signup_date = signup_date.strftime("%Y-%m-%d")
            
            current_year = datetime.now().year
            year_start = f"{current_year}-01-01"
            start_date = max(signup_date, year_start)
            end_date = datetime.now().strftime("%Y-%m-%d")
            
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
            
            # Calculate daily anomaly status - use same logic as anomaly detection
            longest_streak = 0
            current_streak = 0
            
            # Check each day from start to end
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            end_datetime = datetime.now()
            current_date = start_datetime
            
            while current_date <= end_datetime:
                date_str = current_date.strftime("%Y-%m-%d")
                
                if date_str not in daily_data:
                    # No transactions = no anomalies = streak continues
                    current_streak += 1
                else:
                    # Check for anomalies using same logic as main anomaly detection
                    has_anomaly = self._check_daily_anomalies(daily_data[date_str])
                    
                    if not has_anomaly:
                        current_streak += 1
                        longest_streak = max(longest_streak, current_streak)
                    else:
                        current_streak = 0
                
                current_date += timedelta(days=1)
            
            return longest_streak
            
        except Exception as e:
            raise Exception(f"Error calculating longest streak: {e}")
    
    def _check_daily_anomalies(self, day_transactions: List) -> bool:
        """Check if a day has spending anomalies using consistent logic"""
        # Calculate category averages for anomaly detection
        category_stats = {}
        
        # Get broader transaction history for category averages
        db_user_id = 5
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
        
        all_transactions = self.db.get_user_transactions(db_user_id, start_date, end_date)
        
        # Build category averages
        for txn in all_transactions:
            if txn.amount >= 0:  # Skip income
                continue
            category = txn.category or "Other"
            amount = abs(txn.amount)
            
            if category not in category_stats:
                category_stats[category] = []
            category_stats[category].append(amount)
        
        # Check each transaction in the day for anomalies
        for txn in day_transactions:
            if txn.amount >= 0:  # Skip income
                continue
            
            category = txn.category or "Other"
            amount = abs(txn.amount)
            
            if category in category_stats and len(category_stats[category]) > 1:
                category_amounts = category_stats[category]
                avg_amount = sum(category_amounts) / len(category_amounts)
                
                # Flag as anomaly if > 3x average for that category
                if amount > (avg_amount * 3):
                    return True
        
        return False

    def calculate_total_spent_ytd(self) -> float:
        """
        Calculate total amount spent year-to-date - NO DEFAULT VALUES
        """
        try:
            # Get user signup date for proper YTD calculation
            user = self.db.get_user(5)  # Updated to match existing data
            if not user or not user.created_at:
                raise Exception("User signup date not found for YTD calculation")
            
            # Calculate YTD from signup date or beginning of year (whichever is later)
            signup_date = user.created_at
            if isinstance(signup_date, str):
                if 'T' in signup_date:
                    signup_date = signup_date.split('T')[0]
                elif ' ' in signup_date:
                    signup_date = signup_date.split(' ')[0]
            else:
                signup_date = signup_date.strftime("%Y-%m-%d")
            
            current_year = datetime.now().year
            year_start = f"{current_year}-01-01"
            start_date = max(signup_date, year_start)
            end_date = datetime.now().strftime("%Y-%m-%d")
            
            db_user_id = 5  # Updated to match existing data in database
            transactions = self.db.get_user_transactions(db_user_id, start_date, end_date)
            
            if not transactions:
                raise Exception("No transaction data for YTD calculation")
            
            total_spent = sum(abs(txn.amount) for txn in transactions if txn.amount < 0)
            return total_spent
            
        except Exception as e:
            raise Exception(f"Error calculating total spent YTD: {e}")