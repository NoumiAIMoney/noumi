"""
Recap Agent for Noumi AI
Analyzes past week's transactions against the weekly plan to provide insights
and performance evaluation.

This agent:
- Compares actual spending vs planned limits
- Identifies successful areas and problem areas  
- Provides actionable insights for future plans
- Generates performance scores and trends
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

from .base_planning_agent import BasePlanningAgent
from ..utils.llm_client import NoumiLLMClient


class RecapAgent(BasePlanningAgent):
    """
    Analyzes weekly performance by comparing actual transactions 
    against the planned weekly budget and goals.
    
    Key Features:
    - Performance analysis vs planned targets
    - Category-wise spending evaluation
    - Success/failure identification
    - Actionable insights for improvement
    - ML-ready performance metrics
    """

    def __init__(self, 
                 weekly_plan: Dict[str, Any],
                 actual_transactions: List[Dict[str, Any]],
                 user_preferences: Dict[str, Any] = None,
                 llm_client: Optional[NoumiLLMClient] = None):
        """
        Initialize Recap Agent.
        
        Args:
            weekly_plan: The planned weekly budget and goals
            actual_transactions: List of actual transactions for the week
            user_preferences: User preferences and profile
            llm_client: LLM client for AI analysis
        """
        self.weekly_plan = weekly_plan
        self.actual_transactions = actual_transactions
        self.user_preferences = user_preferences or {}
        self.llm_client = llm_client or NoumiLLMClient(provider="google")
        
        # Initialize parent class
        super().__init__(
            self.user_preferences, 
            self._process_transaction_data()
        )

        # Analysis results
        self.performance_analysis = {}
        self.insights = []

    def generate_weekly_recap(self) -> Dict[str, Any]:
        """
        Generate comprehensive weekly recap with performance analysis.
        
        Returns:
            Complete recap with analysis, insights, and recommendations
        """
        # Step 1: Analyze spending performance
        spending_analysis = self._analyze_spending_performance()
        
        # Step 2: Analyze category performance
        category_analysis = self._analyze_category_performance()
        
        # Step 3: Analyze goal achievement
        goal_analysis = self._analyze_goal_achievement()
        
        # Step 4: Generate insights using LLM
        insights = self._generate_insights_with_llm()
        
        # Step 5: Create performance scores
        performance_scores = self._calculate_performance_scores()
        
        # Compile comprehensive recap
        recap = {
            'recap_metadata': {
                'week_period': self._get_week_period(),
                'analysis_timestamp': datetime.now().isoformat(),
                'transaction_count': len(self.actual_transactions)
            },
            'spending_performance': spending_analysis,
            'category_performance': category_analysis,
            'goal_achievement': goal_analysis,
            'ai_insights': insights,
            'performance_scores': performance_scores,
            'recommendations': self._generate_recommendations()
        }
        
        self.performance_analysis = recap
        return recap

    def generate_weekly_plan(self) -> Dict[str, Any]:
        """
        Implementation of abstract method from base class.
        
        Note: Recap agent analyzes plans rather than generates them.
        This method returns the analyzed recap data.
        
        Returns:
            The weekly recap analysis
        """
        return self.generate_weekly_recap()

    def _analyze_spending_performance(self) -> Dict[str, Any]:
        """Analyze overall spending vs planned targets."""
        planned_savings = self.weekly_plan.get('savings_target', {}).get('amount', 0)
        planned_limits = self.weekly_plan.get('spending_limits', {})
        
        # Calculate actual spending
        total_actual_spending = sum(
            abs(t.get('amount', 0)) for t in self.actual_transactions
            if t.get('amount', 0) < 0  # Only spending (negative amounts)
        )
        
        # Calculate planned total spending
        total_planned_spending = sum(
            limit.get('weekly_limit', 0) for limit in planned_limits.values()
        )
        
        # Calculate actual vs planned
        spending_vs_plan = total_actual_spending - total_planned_spending
        spending_adherence = (
            (total_planned_spending - total_actual_spending) / total_planned_spending
            if total_planned_spending > 0 else 0
        )
        
        return {
            'total_planned_spending': total_planned_spending,
            'total_actual_spending': total_actual_spending,
            'planned_savings_target': planned_savings,
            'spending_vs_plan': spending_vs_plan,
            'spending_adherence_rate': max(0, spending_adherence),
            'over_budget': spending_vs_plan > 0,
            'budget_variance_percentage': (
                (spending_vs_plan / total_planned_spending * 100) 
                if total_planned_spending > 0 else 0
            )
        }

    def _analyze_category_performance(self) -> Dict[str, Any]:
        """Analyze performance by spending category."""
        planned_limits = self.weekly_plan.get('spending_limits', {})
        
        # Group actual spending by category
        actual_by_category = {}
        for transaction in self.actual_transactions:
            if transaction.get('amount', 0) < 0:  # Only spending
                category = transaction.get('category', 'Other')
                amount = abs(transaction.get('amount', 0))
                actual_by_category[category] = actual_by_category.get(category, 0) + amount
        
        # Compare each category
        category_performance = {}
        for category, limits in planned_limits.items():
            planned_limit = limits.get('weekly_limit', 0)
            actual_spent = actual_by_category.get(category, 0)
            
            variance = actual_spent - planned_limit
            adherence_rate = (
                (planned_limit - actual_spent) / planned_limit 
                if planned_limit > 0 else 0
            )
            
            category_performance[category] = {
                'planned_limit': planned_limit,
                'actual_spent': actual_spent,
                'variance': variance,
                'adherence_rate': max(0, adherence_rate),
                'status': (
                    'under_budget' if variance <= 0 
                    else 'over_budget'
                ),
                'variance_percentage': (
                    (variance / planned_limit * 100) 
                    if planned_limit > 0 else 0
                )
            }
        
        return category_performance

    def _analyze_goal_achievement(self) -> Dict[str, Any]:
        """Analyze achievement of weekly goals and challenges."""
        tracking_metrics = self.weekly_plan.get('tracking_metrics', [])
        weekly_challenges = self.weekly_plan.get('weekly_challenges', [])
        
        # Analyze tracking metrics
        metric_achievements = []
        for metric in tracking_metrics:
            metric_name = metric.get('metric_name', '')
            target_value = metric.get('target_value', 0)
            
            # Estimate achievement based on spending analysis
            if 'Savings' in metric_name:
                spending_perf = self._analyze_spending_performance()
                estimated_achievement = max(0, spending_perf['spending_adherence_rate'])
            elif 'Budget' in metric_name:
                category_perf = self._analyze_category_performance()
                under_budget_categories = sum(
                    1 for cat_data in category_perf.values() 
                    if cat_data['status'] == 'under_budget'
                )
                estimated_achievement = under_budget_categories / len(category_perf) if category_perf else 0
            else:
                estimated_achievement = 0.7  # Default estimate
            
            metric_achievements.append({
                'metric_name': metric_name,
                'target_value': target_value,
                'estimated_achievement_rate': min(1.0, estimated_achievement),
                'status': (
                    'achieved' if estimated_achievement >= 0.8 
                    else 'partial' if estimated_achievement >= 0.5 
                    else 'not_achieved'
                )
            })
        
        return {
            'metric_achievements': metric_achievements,
            'challenge_count': len(weekly_challenges),
            'overall_goal_success_rate': (
                sum(m['estimated_achievement_rate'] for m in metric_achievements) / 
                len(metric_achievements) if metric_achievements else 0
            )
        }

    def _generate_insights_with_llm(self) -> Dict[str, Any]:
        """Generate insights using LLM analysis."""
        system_role = """
        You are a financial performance analyst providing insights on weekly 
        spending performance. Analyze the data and provide actionable insights.
        
        ANALYSIS REQUIREMENTS:
        1. Identify 2-3 key performance insights
        2. Highlight both successes and areas for improvement
        3. Provide specific, actionable recommendations
        4. Focus on behavioral patterns and trends
        5. Be encouraging but realistic
        """

        content = f"""
        WEEKLY PLAN: {json.dumps(self.weekly_plan)}
        ACTUAL TRANSACTIONS: {json.dumps(self.actual_transactions)}
        SPENDING PERFORMANCE: {json.dumps(self._analyze_spending_performance())}
        CATEGORY PERFORMANCE: {json.dumps(self._analyze_category_performance())}
        
        Analyze this week's financial performance. Return ONLY valid JSON:
        {{
            "key_insights": [
                {{
                    "insight_type": "success|improvement|behavioral|trend",
                    "title": "Brief insight title",
                    "description": "Detailed insight description",
                    "impact_level": "high|medium|low"
                }}
            ],
            "behavioral_patterns": [
                {{
                    "pattern_type": "spending_timing|category_preference|amount_clustering",
                    "description": "Description of observed pattern",
                    "recommendation": "Specific action to take"
                }}
            ],
            "success_highlights": [
                "Specific success #1",
                "Specific success #2"
            ],
            "improvement_areas": [
                {{
                    "area": "Specific area needing improvement",
                    "current_impact": "How it affected this week",
                    "suggested_action": "Specific improvement action"
                }}
            ],
            "overall_performance_summary": "2-3 sentence summary of the week"
        }}
        """

        return self.llm_client.query_financial_planner(
            content, system_role, return_json=True
        )

    def _calculate_performance_scores(self) -> Dict[str, Any]:
        """Calculate quantitative performance scores."""
        spending_perf = self._analyze_spending_performance()
        category_perf = self._analyze_category_performance()
        goal_perf = self._analyze_goal_achievement()
        
        # Overall performance score (0-100)
        adherence_score = spending_perf.get('spending_adherence_rate', 0) * 100
        
        # Category discipline score
        category_scores = [
            max(0, cat_data['adherence_rate']) 
            for cat_data in category_perf.values()
        ]
        category_discipline_score = (
            (sum(category_scores) / len(category_scores)) * 100 
            if category_scores else 0
        )
        
        # Goal achievement score
        goal_achievement_score = goal_perf.get('overall_goal_success_rate', 0) * 100
        
        # Weighted overall score
        overall_score = (
            adherence_score * 0.4 + 
            category_discipline_score * 0.4 + 
            goal_achievement_score * 0.2
        )
        
        return {
            'overall_performance_score': round(overall_score, 1),
            'spending_adherence_score': round(adherence_score, 1),
            'category_discipline_score': round(category_discipline_score, 1),
            'goal_achievement_score': round(goal_achievement_score, 1),
            'performance_grade': self._get_performance_grade(overall_score)
        }

    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate specific recommendations for next week."""
        recommendations = []
        
        spending_perf = self._analyze_spending_performance()
        category_perf = self._analyze_category_performance()
        
        # Recommendation based on overall performance
        if spending_perf.get('over_budget', False):
            recommendations.append({
                'type': 'budget_adjustment',
                'priority': 'high',
                'title': 'Reduce Overall Spending',
                'description': f"You exceeded budget by ${abs(spending_perf['spending_vs_plan']):.2f}. Focus on staying within limits next week.",
                'specific_action': 'Set daily spending alerts'
            })
        
        # Category-specific recommendations
        for category, perf in category_perf.items():
            if perf['status'] == 'over_budget' and perf['variance'] > 20:
                recommendations.append({
                    'type': 'category_focus',
                    'priority': 'medium',
                    'title': f'Optimize {category} Spending',
                    'description': f"You overspent in {category} by ${perf['variance']:.2f}",
                    'specific_action': f'Set stricter limits for {category} next week'
                })
        
        return recommendations

    def _process_transaction_data(self) -> Dict[str, Any]:
        """Process transaction data for parent class."""
        total_spending = sum(
            abs(t.get('amount', 0)) for t in self.actual_transactions 
            if t.get('amount', 0) < 0
        )
        
        # Group by categories
        categories = {}
        for transaction in self.actual_transactions:
            if transaction.get('amount', 0) < 0:  # Only spending
                category = transaction.get('category', 'Other')
                amount = abs(transaction.get('amount', 0))
                if category not in categories:
                    categories[category] = {'total_amount': 0, 'count': 0}
                categories[category]['total_amount'] += amount
                categories[category]['count'] += 1
        
        return {
            'total_spending': total_spending,
            'category_analysis': categories,
            'transaction_count': len(self.actual_transactions)
        }

    def _get_week_period(self) -> str:
        """Get the week period string."""
        if self.weekly_plan.get('week_start_date'):
            start_date = datetime.strptime(
                self.weekly_plan['week_start_date'], '%Y-%m-%d'
            )
            end_date = start_date + timedelta(days=6)
            return f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        return "Current week"

    def _get_performance_grade(self, score: float) -> str:
        """Convert performance score to letter grade."""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'

    def get_ml_performance_features(self) -> Dict[str, Any]:
        """
        Extract ML-ready performance features for machine learning models.
        
        Returns:
            Dictionary with ML features for performance prediction
        """
        if not self.performance_analysis:
            return {'features_available': False}
        
        performance_scores = self.performance_analysis.get('performance_scores', {})
        spending_perf = self.performance_analysis.get('spending_performance', {})
        category_perf = self.performance_analysis.get('category_performance', {})
        
        return {
            'features_available': True,
            'overall_performance_score': performance_scores.get('overall_performance_score', 0),
            'spending_adherence_rate': spending_perf.get('spending_adherence_rate', 0),
            'budget_variance_percentage': spending_perf.get('budget_variance_percentage', 0),
            'categories_over_budget': sum(
                1 for cat_data in category_perf.values() 
                if cat_data.get('status') == 'over_budget'
            ),
            'average_category_adherence': (
                sum(cat_data.get('adherence_rate', 0) for cat_data in category_perf.values()) /
                len(category_perf) if category_perf else 0
            ),
            'extraction_timestamp': datetime.now().isoformat()
        } 