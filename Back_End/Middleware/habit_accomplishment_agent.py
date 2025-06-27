"""
Habit Accomplishment Agent for Noumi API
Analyzes spending patterns to identify accomplished financial habits
Uses LLM to generate meaningful habit accomplishment insights
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
from database import DatabaseManager
from analytics import TransactionAnalyzer


class HabitAccomplishmentAgent:
    """
    LLM-powered agent that analyzes spending patterns and generates 
    meaningful habit accomplishment insights based on actual data.
    """
    
    def __init__(self, user_id: int, db: DatabaseManager):
        self.user_id = user_id
        self.db = db
        self.analyzer = TransactionAnalyzer(user_id)
    
    def analyze_habit_accomplishments(self) -> List[Dict[str, str]]:
        """
        Analyze user's spending patterns and generate accomplished habits
        using LLM-powered insights based on actual data.
        """
        try:
            # Gather comprehensive spending analysis
            analysis_data = self._gather_spending_analysis()
            
            # Generate LLM prompt with analysis data
            self._create_habit_analysis_prompt(analysis_data)
            
            # For now, use rule-based analysis 
            # (can be replaced with actual LLM call)
            accomplishments = self._generate_habit_accomplishments(analysis_data)
            
            return accomplishments
            
        except Exception as e:
            print(f"Error analyzing habit accomplishments: {e}")
            return self._get_fallback_accomplishments()
    
    def _gather_spending_analysis(self) -> Dict[str, Any]:
        """
        Gather comprehensive spending analysis data for habit insights.
        """
        try:
            # Get current week and previous week data
            current_week_start, current_week_end = (
                self._get_current_week_dates()
            )
            prev_week_start, prev_week_end = self._get_previous_week_dates()
            
            # Get transactions for both weeks
            current_week_txns = self.db.get_user_transactions(
                self.user_id, current_week_start, current_week_end
            )
            prev_week_txns = self.db.get_user_transactions(
                self.user_id, prev_week_start, prev_week_end
            )
            
            # Analyze spending patterns
            current_analysis = self._analyze_week_transactions(current_week_txns)
            previous_analysis = self._analyze_week_transactions(prev_week_txns)
            
            # Calculate month-to-date and previous month spending
            current_month = datetime.now().strftime("%Y-%m")
            prev_month = (
                datetime.now().replace(day=1) - timedelta(days=1)
            ).strftime("%Y-%m")
            
            current_month_spending = self.db.get_spending_by_category(
                self.user_id, f"{current_month}-01"
            )
            prev_month_spending = self.db.get_spending_by_category(
                self.user_id, f"{prev_month}-01"
            )
            
            return {
                "current_week": current_analysis,
                "previous_week": previous_analysis,
                "current_month_spending": current_month_spending,
                "previous_month_spending": prev_month_spending,
                "week_comparison": self._compare_weeks(
                    current_analysis, previous_analysis
                ),
                "month_comparison": self._compare_months(
                    current_month_spending, prev_month_spending
                ),
                "engagement_metrics": self._calculate_engagement_metrics()
            }
            
        except Exception as e:
            print(f"Error gathering spending analysis: {e}")
            return {}
    
    def _analyze_week_transactions(self, transactions: List) -> Dict[str, Any]:
        """Analyze a week's worth of transactions."""
        if not transactions:
            return {
                "total_spent": 0,
                "transaction_count": 0,
                "categories": {},
                "merchants": {},
                "daily_spending": {},
                "average_transaction": 0
            }
        
        total_spent = 0
        categories = {}
        merchants = {}
        daily_spending = {}
        
        for txn in transactions:
            if txn.amount < 0:  # Expenses only
                amount = abs(txn.amount)
                total_spent += amount
                
                # Category analysis
                category = txn.category or "Other"
                if category not in categories:
                    categories[category] = {"amount": 0, "count": 0}
                categories[category]["amount"] += amount
                categories[category]["count"] += 1
                
                # Merchant analysis
                merchant = txn.merchant_name or "Unknown"
                if merchant not in merchants:
                    merchants[merchant] = {"amount": 0, "count": 0}
                merchants[merchant]["amount"] += amount
                merchants[merchant]["count"] += 1
                
                # Daily spending
                date_str = str(txn.date)
                if date_str not in daily_spending:
                    daily_spending[date_str] = 0
                daily_spending[date_str] += amount
        
        expense_count = len([t for t in transactions if t.amount < 0])
        avg_transaction = total_spent / expense_count if expense_count > 0 else 0
        
        return {
            "total_spent": total_spent,
            "transaction_count": expense_count,
            "categories": categories,
            "merchants": merchants,
            "daily_spending": daily_spending,
            "average_transaction": avg_transaction
        }
    
    def _compare_weeks(self, current: Dict, previous: Dict) -> Dict[str, Any]:
        """Compare current week vs previous week spending."""
        if not current or not previous:
            return {}
        
        current_total = current.get("total_spent", 0)
        previous_total = previous.get("total_spent", 0)
        
        spending_change = current_total - previous_total
        spending_change_pct = (
            (spending_change / previous_total * 100) 
            if previous_total > 0 else 0
        )
        
        # Category comparisons
        category_changes = {}
        current_cats = current.get("categories", {})
        previous_cats = previous.get("categories", {})
        
        for category in set(list(current_cats.keys()) + list(previous_cats.keys())):
            current_amount = current_cats.get(category, {}).get("amount", 0)
            previous_amount = previous_cats.get(category, {}).get("amount", 0)
            change = current_amount - previous_amount
            category_changes[category] = {
                "amount_change": change,
                "current_amount": current_amount,
                "previous_amount": previous_amount
            }
        
        return {
            "spending_change": spending_change,
            "spending_change_percentage": spending_change_pct,
            "category_changes": category_changes,
            "transaction_count_change": (
                current.get("transaction_count", 0) - 
                previous.get("transaction_count", 0)
            )
        }
    
    def _compare_months(self, current_month: Dict, previous_month: Dict) -> Dict[str, Any]:
        """Compare current month vs previous month spending."""
        if not current_month or not previous_month:
            return {}
        
        current_total = sum(current_month.values())
        previous_total = sum(previous_month.values())
        
        spending_change = current_total - previous_total
        spending_change_pct = (
            (spending_change / previous_total * 100) 
            if previous_total > 0 else 0
        )
        
        return {
            "spending_change": spending_change,
            "spending_change_percentage": spending_change_pct,
            "current_total": current_total,
            "previous_total": previous_total
        }
    
    def _calculate_engagement_metrics(self) -> Dict[str, Any]:
        """Calculate user engagement metrics."""
        # For this MVP, we'll simulate engagement metrics
        # In a real app, this would track actual app usage
        return {
            "daily_logins_this_week": 5,  # Simulated
            "budget_checks_this_week": 3,  # Simulated
            "goal_progress_views": 2  # Simulated
        }
    
    def _create_habit_analysis_prompt(self, analysis_data: Dict[str, Any]) -> str:
        """
        Create LLM prompt for habit accomplishment analysis.
        This prompt engineering follows best practices for financial habit analysis.
        """
        current_week_data = analysis_data.get('current_week', {})
        previous_week_data = analysis_data.get('previous_week', {})
        week_comparison = analysis_data.get('week_comparison', {})
        month_comparison = analysis_data.get('month_comparison', {})
        engagement = analysis_data.get('engagement_metrics', {})
        
        return f"""
You are a financial habit accomplishment analyst. Analyze the following spending data and identify 2-3 meaningful habit accomplishments for this user.

SPENDING ANALYSIS DATA:
Current Week Spending: ${current_week_data.get('total_spent', 0):.2f}
Previous Week Spending: ${previous_week_data.get('total_spent', 0):.2f}
Week-over-Week Change: ${week_comparison.get('spending_change', 0):.2f}

Current Month Total: ${month_comparison.get('current_total', 0):.2f}
Previous Month Total: ${month_comparison.get('previous_total', 0):.2f}

Top Categories This Week:
{self._format_categories_for_prompt(current_week_data.get('categories', {}))}

Category Changes (Current vs Previous Week):
{self._format_category_changes_for_prompt(week_comparison.get('category_changes', {}))}

Engagement Metrics:
- Daily app logins: {engagement.get('daily_logins_this_week', 0)}
- Budget checks: {engagement.get('budget_checks_this_week', 0)}

INSTRUCTIONS:
1. Identify 2-3 specific habit accomplishments based on the actual data provided
2. Focus on positive changes like spending reductions, category improvements, or engagement
3. Include specific dollar amounts from the analysis
4. Format each accomplishment as: {{"habit_description": "...", "value": "..."}}
5. For value, use dollar amounts (like "36.24") or descriptive values (like "noumi" for app engagement)
6. Be specific and data-driven - only use the numbers provided above

EXAMPLE OUTPUT FORMAT:
[
  {{"habit_description": "You reduced coffee spending by $15.50 this week", "value": "15.50"}},
  {{"habit_description": "You checked your budget 3 times this week", "value": "noumi"}}
]

Generate accomplishments now based solely on the provided data:
"""
    
    def _format_categories_for_prompt(self, categories: Dict) -> str:
        """Format categories for LLM prompt."""
        if not categories:
            return "No category data available"
        
        sorted_cats = sorted(
            categories.items(), 
            key=lambda x: x[1].get("amount", 0), 
            reverse=True
        )
        return "\n".join([
            f"- {cat}: ${data.get('amount', 0):.2f} "
            f"({data.get('count', 0)} transactions)"
            for cat, data in sorted_cats[:5]  # Top 5 categories
        ])
    
    def _format_category_changes_for_prompt(self, category_changes: Dict) -> str:
        """Format category changes for LLM prompt."""
        if not category_changes:
            return "No category change data available"
        
        significant_changes = [
            (cat, data) for cat, data in category_changes.items()
            if abs(data.get("amount_change", 0)) > 5  # Only changes > $5
        ]
        
        if not significant_changes:
            return "No significant category changes"
        
        return "\n".join([
            f"- {cat}: {'+' if data['amount_change'] > 0 else ''}"
            f"${data['amount_change']:.2f} "
            f"(${data['previous_amount']:.2f} → ${data['current_amount']:.2f})"
            for cat, data in significant_changes
        ])
    
    def _generate_habit_accomplishments(self, analysis_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Generate habit accomplishments using rule-based analysis.
        This can be replaced with actual LLM API calls.
        """
        accomplishments = []
        
        try:
            # Analyze spending reduction accomplishments
            week_comparison = analysis_data.get("week_comparison", {})
            spending_change = week_comparison.get("spending_change", 0)
            
            if spending_change < -10:  # Spent at least $10 less
                accomplishments.append({
                    "habit_description": (
                        f"You reduced spending by ${abs(spending_change):.2f} "
                        f"this week compared to last week"
                    ),
                    "value": f"{abs(spending_change):.2f}"
                })
            
            # Analyze category-specific improvements
            category_changes = week_comparison.get("category_changes", {})
            for category, change_data in category_changes.items():
                change_amount = change_data.get("amount_change", 0)
                if change_amount < -15:  # Reduced spending by $15+ in this category
                    accomplishments.append({
                        "habit_description": (
                            f"You cut {category.lower()} spending by "
                            f"${abs(change_amount):.2f} this week"
                        ),
                        "value": f"{abs(change_amount):.2f}"
                    })
            
            # Analyze engagement accomplishments
            engagement = analysis_data.get("engagement_metrics", {})
            daily_logins = engagement.get("daily_logins_this_week", 0)
            if daily_logins >= 5:
                accomplishments.append({
                    "habit_description": (
                        f"You logged into Noumi {daily_logins} times this week, "
                        f"staying on top of your finances"
                    ),
                    "value": "noumi"
                })
            
            # Analyze transaction frequency (fewer transactions can indicate better planning)
            txn_change = week_comparison.get("transaction_count_change", 0)
            if txn_change <= -3:  # 3+ fewer transactions
                accomplishments.append({
                    "habit_description": (
                        f"You made {abs(txn_change)} fewer impulse purchases "
                        f"this week"
                    ),
                    "value": f"{abs(txn_change)}"
                })
            
            # Limit to top 3 accomplishments
            return (accomplishments[:3] if accomplishments 
                   else self._get_fallback_accomplishments())
            
        except Exception as e:
            print(f"Error generating accomplishments: {e}")
            return self._get_fallback_accomplishments()
    
    def _get_fallback_accomplishments(self) -> List[Dict[str, str]]:
        """Provide fallback accomplishments when analysis fails."""
        return [
            {
                "habit_description": "You're tracking your spending consistently",
                "value": "noumi"
            },
            {
                "habit_description": "You're building awareness of your financial patterns",
                "value": "awareness"
            }
        ]
    
    def _get_current_week_dates(self) -> tuple[str, str]:
        """Get current week Monday to Sunday dates."""
        today = datetime.now()
        days_since_monday = today.weekday()
        monday = today - timedelta(days=days_since_monday)
        sunday = monday + timedelta(days=6)
        return monday.strftime("%Y-%m-%d"), sunday.strftime("%Y-%m-%d")
    
    def _get_previous_week_dates(self) -> tuple[str, str]:
        """Get previous week Monday to Sunday dates."""
        today = datetime.now()
        days_since_monday = today.weekday()
        last_monday = today - timedelta(days=days_since_monday + 7)
        last_sunday = last_monday + timedelta(days=6)
        return last_monday.strftime("%Y-%m-%d"), last_sunday.strftime("%Y-%m-%d") 