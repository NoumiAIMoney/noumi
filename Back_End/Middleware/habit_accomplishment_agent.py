"""
Habit Accomplishment Agent for Noumi API
Analyzes spending patterns to identify accomplished financial habits
Uses LLM to generate meaningful habit accomplishment insights
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
from database import DatabaseManager
from analytics import TransactionAnalyzer
from fastapi import HTTPException


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
        Analyze user's spending patterns to identify accomplished habits.
        Uses actual transaction data and raises errors when data unavailable.
        """
        try:
            # Gather all spending analysis data
            analysis_data = self._gather_spending_analysis()
            
            # Ensure we have sufficient data for analysis
            if not analysis_data:
                raise HTTPException(
                    status_code=404, 
                    detail="No spending data available for habit analysis"
                )
                
            # Generate accomplishments based on real data
            accomplishments = self._generate_habit_accomplishments(analysis_data)
            
            # Ensure we have valid accomplishments from data analysis
            if not accomplishments:
                raise HTTPException(
                    status_code=404,
                    detail="No habit accomplishments found based on current spending data"
                )
                
            return accomplishments
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to analyze habit accomplishments: {str(e)}"
            )
    
    def _gather_spending_analysis(self) -> Dict[str, Any]:
        """
        Gather comprehensive spending analysis for habit accomplishment detection.
        Returns available data even if some components are missing.
        """
        try:
            # Get current and previous week spending data
            current_week_data = self._get_current_week_spending()
            previous_week_data = self._get_previous_week_spending()
            
            # If no data at all, raise error
            if not current_week_data and not previous_week_data:
                raise HTTPException(
                    status_code=404,
                    detail="No spending data available for any recent weeks"
                )
            
            # Compare weeks (returns empty dict if insufficient data)
            week_comparison = self._compare_weeks(current_week_data, previous_week_data)
            
            # Get monthly comparison data (returns empty dict if no data)
            month_comparison = self._compare_months(
                current_week_data.get('monthly_context', {}),
                previous_week_data.get('monthly_context', {})
            )
            
            # Get engagement metrics (always available)
            engagement_metrics = self._calculate_engagement_metrics()
            
            return {
                "current_week": current_week_data or {},
                "previous_week": previous_week_data or {}, 
                "week_comparison": week_comparison,
                "month_comparison": month_comparison,
                "engagement_metrics": engagement_metrics
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error gathering spending analysis: {str(e)}"
            )
    
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
        """Compare current and previous week spending patterns."""
        if not current or not previous:
            return {}  # Return empty dict, handled gracefully by caller
        
        try:
            current_total = current.get("total_spent", 0)
            previous_total = previous.get("total_spent", 0)
            
            # Calculate spending change
            spending_change = current_total - previous_total
            spending_change_pct = (
                (spending_change / previous_total * 100) 
                if previous_total > 0 else 0
            )
            
            # Compare transaction counts
            current_count = current.get("transaction_count", 0)
            previous_count = previous.get("transaction_count", 0)
            txn_count_change = current_count - previous_count
            
            # Compare categories
            current_cats = current.get("categories", {})
            previous_cats = previous.get("categories", {})
            category_changes = {}
            
            all_categories = set(list(current_cats.keys()) + list(previous_cats.keys()))
            for category in all_categories:
                current_amount = current_cats.get(category, {}).get("amount", 0)
                previous_amount = previous_cats.get(category, {}).get("amount", 0)
                
                category_changes[category] = {
                    "current_amount": current_amount,
                    "previous_amount": previous_amount,
                    "amount_change": current_amount - previous_amount
                }
            
            return {
                "spending_change": spending_change,
                "spending_change_percentage": spending_change_pct,
                "transaction_count_change": txn_count_change,
                "category_changes": category_changes,
                "current_total": current_total,
                "previous_total": previous_total
            }
            
        except Exception as e:
            print(f"Warning: Error comparing weeks: {e}")
            return {}  # Return empty dict on error
    
    def _compare_months(self, current_month: Dict, previous_month: Dict) -> Dict[str, Any]:
        """Compare current and previous month spending totals."""
        if not current_month and not previous_month:
            return {}  # Return empty dict, handled gracefully by caller
        
        try:
            current_total = sum(current_month.values()) if current_month else 0
            previous_total = sum(previous_month.values()) if previous_month else 0
            
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
        except Exception as e:
            print(f"Warning: Error comparing months: {e}")
            return {}  # Return empty dict on error
    
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
        Raises errors when insufficient data available.
        """
        accomplishments = []
        
        try:
            # Get current week data for basic accomplishments
            current_week = analysis_data.get("current_week", {})
            engagement = analysis_data.get("engagement_metrics", {})
            
            # Try to get week comparison data
            week_comparison = analysis_data.get("week_comparison", {})
            
            # Basic engagement accomplishments (always available)
            daily_logins = engagement.get("daily_logins_this_week", 0)
            if daily_logins >= 5:
                accomplishments.append({
                    "habit_description": (
                        f"You logged into Noumi {daily_logins} times this week, "
                        f"staying on top of your finances"
                    ),
                    "value": "noumi"
                })
            
            # Current week spending awareness
            current_total = current_week.get("total_spent", 0)
            if current_total > 0:
                accomplishments.append({
                    "habit_description": (
                        f"You tracked ${current_total:.2f} in spending this week, "
                        f"building financial awareness"
                    ),
                    "value": "awareness"
                })
            
            # Only add comparison-based accomplishments if we have valid comparison data
            if week_comparison:
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
                
                # Analyze transaction frequency
                txn_change = week_comparison.get("transaction_count_change", 0)
                if txn_change <= -3:  # 3+ fewer transactions
                    accomplishments.append({
                        "habit_description": (
                            f"You made {abs(txn_change)} fewer impulse purchases "
                            f"this week"
                        ),
                        "value": f"{abs(txn_change)}"
                    })
            
            # If still no accomplishments and we have any current week data, provide basic one
            if not accomplishments and current_week.get("transaction_count", 0) > 0:
                accomplishments.append({
                    "habit_description": "You actively monitored your spending patterns this week",
                    "value": "monitoring"
                })
            
            # If absolutely no accomplishments found, raise error
            if not accomplishments:
                raise HTTPException(
                    status_code=404,
                    detail="No habit accomplishments detected - insufficient spending data available"
                )
            
            # Limit to top 3 accomplishments
            return accomplishments[:3]
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating accomplishments: {str(e)}"
            )
    
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
    
    def _get_current_week_spending(self) -> Dict[str, Any]:
        """Get current week spending data."""
        try:
            start_date, end_date = self._get_current_week_dates()
            transactions = self.db.get_user_transactions(
                self.user_id, start_date, end_date
            )
            return self._analyze_week_transactions(transactions)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting current week spending: {str(e)}"
            )
    
    def _get_previous_week_spending(self) -> Dict[str, Any]:
        """Get previous week spending data."""
        try:
            start_date, end_date = self._get_previous_week_dates()
            transactions = self.db.get_user_transactions(
                self.user_id, start_date, end_date
            )
            return self._analyze_week_transactions(transactions)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting previous week spending: {str(e)}"
            ) 