"""
Analytics module for Noumi API
Handles transaction analysis, anomaly detection, and spending insights
"""

import math
import statistics
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from collections import defaultdict, Counter
from database import db, Transaction


class TransactionAnalyzer:
    """Analyze user transactions for insights and anomalies"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
    
    def detect_spending_anomalies(self, year: int = None) -> List[int]:
        """Detect spending anomalies per month for the year"""
        if year is None:
            year = datetime.now().year
        
        # Get all transactions for the year
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        transactions = db.get_user_transactions(
            self.user_id, start_date, end_date
        )
        
        # Group spending by month
        monthly_spending = defaultdict(list)
        for txn in transactions:
            if txn.amount < 0:  # Only spending transactions
                month = int(txn.date.split('-')[1])
                monthly_spending[month].append(abs(txn.amount))
        
        # Calculate anomalies for each month
        anomalies_per_month = []
        for month in range(1, 13):
            month_amounts = monthly_spending.get(month, [])
            if not month_amounts:
                anomalies_per_month.append(0)
                continue
            
            # Use Z-score to detect anomalies
            if len(month_amounts) < 3:
                anomalies_per_month.append(0)
                continue
            
            mean_amount = statistics.mean(month_amounts)
            std_amount = statistics.stdev(month_amounts)
            
            anomaly_count = 0
            for amount in month_amounts:
                if std_amount > 0:
                    z_score = abs(amount - mean_amount) / std_amount
                    if z_score > 2.0:  # More than 2 standard deviations
                        anomaly_count += 1
            
            anomalies_per_month.append(anomaly_count)
        
        return anomalies_per_month
    
    def analyze_spending_trends(self) -> List[Dict[str, str]]:
        """Analyze spending patterns and generate insights"""
        # Get last 3 months of transactions
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        transactions = db.get_user_transactions(
            self.user_id, 
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        
        trends = []
        
        # Analyze day-of-week patterns
        spending_by_day = defaultdict(list)
        for txn in transactions:
            if txn.amount < 0:
                date_obj = datetime.strptime(txn.date, "%Y-%m-%d")
                day_name = date_obj.strftime("%A")
                spending_by_day[day_name].append(abs(txn.amount))
        
        # Find highest spending days
        day_totals = {
            day: sum(amounts) for day, amounts in spending_by_day.items()
        }
        if day_totals:
            max_day = max(day_totals, key=day_totals.get)
            trends.append({
                "icon": "📅",
                "trend": f"{max_day} is your highest spending day with "
                        f"${day_totals[max_day]:.2f} total this quarter."
            })
        
        # Analyze merchant patterns
        merchant_spending = defaultdict(float)
        for txn in transactions:
            if txn.amount < 0 and txn.merchant_name:
                merchant_spending[txn.merchant_name] += abs(txn.amount)
        
        if merchant_spending:
            top_merchant = max(merchant_spending, key=merchant_spending.get)
            trends.append({
                "icon": "🏪",
                "trend": f"{top_merchant} is your top merchant with "
                        f"${merchant_spending[top_merchant]:.2f} spent."
            })
        
        # Analyze category trends
        category_spending = defaultdict(float)
        for txn in transactions:
            if txn.amount < 0:
                category_spending[txn.category] += abs(txn.amount)
        
        if len(category_spending) >= 2:
            sorted_categories = sorted(
                category_spending.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            top_category = sorted_categories[0]
            trends.append({
                "icon": "📊",
                "trend": f"Your top spending category is {top_category[0]} "
                        f"at ${top_category[1]:.2f} this quarter."
            })
        
        # Transaction frequency analysis
        daily_transactions = defaultdict(int)
        for txn in transactions:
            if txn.amount < 0:
                daily_transactions[txn.date] += 1
        
        if daily_transactions:
            avg_daily_txns = statistics.mean(daily_transactions.values())
            if avg_daily_txns > 3:
                trends.append({
                    "icon": "💳",
                    "trend": f"You average {avg_daily_txns:.1f} "
                            "transactions per day - consider consolidating."
                })
        
        return trends[:4]  # Return top 4 trends
    
    def get_spending_categories_with_history(self) -> List[Dict[str, Any]]:
        """Get spending categories with month-over-month data"""
        current_date = datetime.now()
        current_month = current_date.strftime("%Y-%m")
        prev_month = (current_date - timedelta(days=30)).strftime("%Y-%m")
        
        # Get current month transactions
        current_start = f"{current_month}-01"
        current_spending = db.get_spending_by_category(
            self.user_id, current_start
        )
        
        # Get previous month transactions
        prev_start = f"{prev_month}-01"
        prev_end = current_start
        prev_transactions = db.get_user_transactions(
            self.user_id, prev_start, prev_end
        )
        
        # Calculate previous month spending by category
        prev_spending = defaultdict(float)
        for txn in prev_transactions:
            if txn.amount < 0:
                prev_spending[txn.category] += abs(txn.amount)
        
        # Combine data
        categories = []
        all_categories = set(current_spending.keys()) | set(prev_spending.keys())
        
        for category in all_categories:
            current_amount = current_spending.get(category, 0)
            prev_amount = prev_spending.get(category, 0)
            
            if current_amount > 0:
                categories.append({
                    "category_name": category,
                    "amount": current_amount,
                    "month": current_month
                })
            
            if prev_amount > 0:
                categories.append({
                    "category_name": category,
                    "amount": prev_amount,
                    "month": prev_month
                })
        
        # Sort by current month amount
        categories.sort(
            key=lambda x: x["amount"] if x["month"] == current_month else 0,
            reverse=True
        )
        
        return categories
    
    def calculate_spending_status(self) -> Dict[str, float]:
        """Calculate current spending status for the month"""
        # Get user goal for income
        goal = db.get_user_goal(self.user_id)
        if not goal:
            return {
                "income": 0,
                "expenses": 0,
                "amount_safe_to_spend": 0
            }
        
        # Get current month transactions
        current_month_start = datetime.now().strftime("%Y-%m-01")
        transactions = db.get_user_transactions(
            self.user_id, current_month_start
        )
        
        # Calculate total expenses this month
        total_expenses = sum(
            abs(txn.amount) for txn in transactions if txn.amount < 0
        )
        
        # Calculate safe amount to spend (income - expenses - 20% buffer)
        monthly_income = goal.net_monthly_income
        buffer = monthly_income * 0.2  # 20% savings buffer
        safe_to_spend = max(0, monthly_income - total_expenses - buffer)
        
        return {
            "income": monthly_income,
            "expenses": total_expenses,
            "amount_safe_to_spend": safe_to_spend
        }
    
    def calculate_total_spent_ytd(self) -> float:
        """Calculate total amount spent year-to-date"""
        year_start = f"{datetime.now().year}-01-01"
        transactions = db.get_user_transactions(self.user_id, year_start)
        
        return sum(abs(txn.amount) for txn in transactions if txn.amount < 0)
    
    def calculate_weekly_streak(self) -> List[int]:
        """Calculate weekly no-overspend streak"""
        # Get user's spending limits from most recent weekly plan
        # For now, use a default daily limit of $50
        daily_limit = 50.0
        
        # Get current week's transactions (Monday to Sunday)
        today = datetime.now()
        days_since_monday = today.weekday()
        monday = today - timedelta(days=days_since_monday)
        
        streak = []
        for i in range(7):  # Monday to Sunday
            day = monday + timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            
            # Get transactions for this day
            day_end = (day + timedelta(days=1)).strftime("%Y-%m-%d")
            day_transactions = db.get_user_transactions(
                self.user_id, day_str, day_end
            )
            
            # Calculate daily spending
            daily_spending = sum(
                abs(txn.amount) for txn in day_transactions if txn.amount < 0
            )
            
            # 1 if under budget, 0 if over
            streak.append(1 if daily_spending <= daily_limit else 0)
        
        return streak
    
    def calculate_longest_streak(self) -> int:
        """Calculate longest consecutive no-overspend streak this year"""
        # Get all transactions for current year
        year_start = f"{datetime.now().year}-01-01"
        transactions = db.get_user_transactions(self.user_id, year_start)
        
        # Group by date
        daily_spending = defaultdict(float)
        for txn in transactions:
            if txn.amount < 0:
                daily_spending[txn.date] += abs(txn.amount)
        
        # Use default daily limit
        daily_limit = 50.0
        
        # Calculate streaks
        current_streak = 0
        longest_streak = 0
        
        # Go through each day of the year so far
        start_date = datetime.strptime(year_start, "%Y-%m-%d")
        end_date = datetime.now()
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            day_spending = daily_spending.get(date_str, 0)
            
            if day_spending <= daily_limit:
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 0
            
            current_date += timedelta(days=1)
        
        return longest_streak
    
    def calculate_weekly_savings(self) -> Dict[str, float]:
        """Calculate actual vs suggested weekly savings"""
        # Get current and previous week spending
        today = datetime.now()
        
        # Current week (Monday to Sunday)
        days_since_monday = today.weekday()
        current_monday = today - timedelta(days=days_since_monday)
        current_week_start = current_monday.strftime("%Y-%m-%d")
        
        # Previous week
        prev_monday = current_monday - timedelta(days=7)
        prev_week_start = prev_monday.strftime("%Y-%m-%d")
        prev_week_end = current_monday.strftime("%Y-%m-%d")
        
        # Get transactions for both weeks
        current_week_txns = db.get_user_transactions(
            self.user_id, current_week_start
        )
        prev_week_txns = db.get_user_transactions(
            self.user_id, prev_week_start, prev_week_end
        )
        
        # Calculate spending for each week
        current_week_spending = sum(
            abs(txn.amount) for txn in current_week_txns if txn.amount < 0
        )
        prev_week_spending = sum(
            abs(txn.amount) for txn in prev_week_txns if txn.amount < 0
        )
        
        # Actual savings = reduction in spending
        actual_savings = max(0, prev_week_spending - current_week_spending)
        
        # Suggested savings based on income (target 20% of weekly income)
        goal = db.get_user_goal(self.user_id)
        weekly_income = goal.net_monthly_income / 4 if goal else 1000
        suggested_savings = weekly_income * 0.2
        
        return {
            "actual_savings": actual_savings,
            "suggested_savings_amount_weekly": suggested_savings
        } 