"""
Financial Quiz Agent for Noumi
Generates personalized quizzes to understand user financial goals and preferences.
"""

from typing import Dict, List, Any, Optional
import json

from .base_quiz_agent import BaseQuizAgent
from ..utils.llm_client import NoumiLLMClient


class FinancialQuizAgent(BaseQuizAgent):
    """
    Concrete implementation for generating personalized financial quizzes.
    """

    def __init__(self, user_profile: Dict[str, Any] = None,
                 llm_client: Optional[NoumiLLMClient] = None):
        super().__init__(user_profile)
        self.llm_client = llm_client or NoumiLLMClient(provider="google")

    def generate_personalized_quiz(self) -> List[Dict[str, Any]]:
        """
        Generate personalized quiz questions based on user profile.
        """
        # Base questions that apply to all users
        base_questions = self._get_base_questions()

        # Generate additional personalized questions using LLM
        personalized_questions = self._generate_llm_questions()

        # Combine and return all questions
        self.quiz_questions = base_questions + personalized_questions
        return self.quiz_questions

    def analyze_quiz_responses(self, responses: Dict[str, Any]) -> \
            Dict[str, Any]:
        """
        Analyze quiz responses to extract user preferences and goals.
        """
        # Process responses to extract insights
        analysis = {
            'risk_tolerance': self._analyze_risk_tolerance(responses),
            'savings_goals': self._analyze_savings_goals(responses),
            'spending_priorities': self._analyze_spending_priorities(responses),
            'financial_knowledge': self._analyze_financial_knowledge(responses),
            'motivation_factors': self._analyze_motivation_factors(responses),
            'preferred_saving_methods': self._analyze_saving_methods(responses)
        }

        # Use LLM for deeper analysis
        llm_analysis = self._get_llm_analysis(responses, analysis)
        analysis['ai_insights'] = llm_analysis

        self.user_preferences = analysis
        return analysis

    def _get_base_questions(self) -> List[Dict[str, Any]]:
        """
        Get base quiz questions that apply to all users.
        """
        return [
            {
                "id": "savings_goal",
                "type": "multiple_choice",
                "question": "What is your primary savings goal?",
                "options": [
                    "Emergency fund",
                    "Vacation or travel",
                    "Major purchase (car, home, etc.)",
                    "Retirement",
                    "General financial security",
                    "Debt reduction"
                ],
                "required": True
            },
            {
                "id": "monthly_income",
                "type": "range",
                "question": "What is your approximate monthly income?",
                "min_value": 0,
                "max_value": 20000,
                "step": 500,
                "required": True
            },
            {
                "id": "current_savings",
                "type": "multiple_choice",
                "question": "How much do you currently have in savings?",
                "options": [
                    "Less than $500",
                    "$500 - $2,000",
                    "$2,000 - $10,000",
                    "$10,000 - $50,000",
                    "More than $50,000"
                ],
                "required": True
            },
            {
                "id": "savings_timeframe",
                "type": "multiple_choice",
                "question": "What is your target timeframe for your main savings goal?",
                "options": [
                    "1-3 months",
                    "3-6 months",
                    "6-12 months",
                    "1-2 years",
                    "2-5 years",
                    "5+ years"
                ],
                "required": True
            },
            {
                "id": "spending_categories",
                "type": "multiple_select",
                "question": "Which categories do you spend the most on? (Select all that apply)",
                "options": [
                    "Housing/Rent",
                    "Food & Dining",
                    "Transportation",
                    "Entertainment",
                    "Shopping",
                    "Healthcare",
                    "Education",
                    "Travel",
                    "Subscriptions & Services"
                ],
                "required": True
            },
            {
                "id": "financial_stress",
                "type": "scale",
                "question": "How stressed do you feel about your finances?",
                "scale_min": 1,
                "scale_max": 10,
                "min_label": "Not stressed at all",
                "max_label": "Extremely stressed",
                "required": True
            },
            {
                "id": "saving_difficulty",
                "type": "multiple_choice",
                "question": "What is your biggest challenge when it comes to saving money?",
                "options": [
                    "Not enough income",
                    "Too many expenses",
                    "Lack of motivation",
                    "No clear goals",
                    "Unexpected expenses",
                    "Poor spending habits",
                    "Don't know where to start"
                ],
                "required": True
            },
            {
                "id": "spending_tracking",
                "type": "multiple_choice",
                "question": "How do you currently track your spending?",
                "options": [
                    "I don't track my spending",
                    "Mental tracking only",
                    "Bank statements review",
                    "Spreadsheet or manual tracking",
                    "Mobile app",
                    "Other digital tools"
                ],
                "required": True
            },
            {
                "id": "risk_tolerance",
                "type": "multiple_choice",
                "question": "How would you describe your approach to financial risk?",
                "options": [
                    "Very conservative - I avoid all risk",
                    "Conservative - I prefer safe investments",
                    "Moderate - I'm comfortable with some risk",
                    "Aggressive - I'm willing to take significant risks for higher returns",
                    "I don't know enough to decide"
                ],
                "required": True
            },
            {
                "id": "motivation_style",
                "type": "multiple_choice",
                "question": "What motivates you most to save money?",
                "options": [
                    "Reaching specific financial milestones",
                    "Competing with others or challenges",
                    "Seeing daily/weekly progress",
                    "Long-term financial security",
                    "Rewarding myself for achievements",
                    "Avoiding financial stress"
                ],
                "required": True
            }
        ]

    def _generate_llm_questions(self) -> List[Dict[str, Any]]:
        """
        Generate additional personalized questions using LLM.
        """
        system_role = """
        You are a financial advisor AI creating personalized quiz questions.
        Generate 3-5 additional quiz questions based on the user profile provided.
        Focus on understanding specific saving preferences and behavioral patterns.
        """

        content = f"""
        User Profile: {json.dumps(self.user_profile)}

        Create additional quiz questions that will help understand:
        1. Specific spending triggers and habits
        2. Preferred communication and reminder styles
        3. Social influences on spending
        4. Technology preferences for financial management
        5. Past success/failure patterns with savings

        Return as JSON array with each question having:
        - id: unique identifier
        - type: question type (multiple_choice, scale, text, etc.)
        - question: the question text
        - options: available options (for multiple choice)
        - required: boolean
        """

        try:
            llm_questions = self.llm_client.query_financial_planner(
                content, system_role, return_json=True
            )
            return llm_questions if isinstance(llm_questions, list) else []
        except Exception:
            # Return empty list if LLM fails
            return []

    def _analyze_risk_tolerance(self, responses: Dict[str, Any]) -> str:
        """Analyze user's risk tolerance from responses."""
        risk_response = responses.get('risk_tolerance', '')
        
        risk_mapping = {
            'Very conservative - I avoid all risk': 'very_low',
            'Conservative - I prefer safe investments': 'low',
            'Moderate - I\'m comfortable with some risk': 'moderate',
            'Aggressive - I\'m willing to take significant risks for higher returns': 'high',
            'I don\'t know enough to decide': 'unknown'
        }
        
        return risk_mapping.get(risk_response, 'unknown')

    def _analyze_savings_goals(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user's savings goals from responses."""
        primary_goal = responses.get('savings_goal', '')
        timeframe = responses.get('savings_timeframe', '')
        current_savings = responses.get('current_savings', '')
        
        # Convert timeframe to months for calculation
        timeframe_mapping = {
            '1-3 months': 2,
            '3-6 months': 4.5,
            '6-12 months': 9,
            '1-2 years': 18,
            '2-5 years': 42,
            '5+ years': 60
        }
        
        return {
            'primary_goal': primary_goal,
            'timeframe_months': timeframe_mapping.get(timeframe, 12),
            'current_savings_level': current_savings,
            'urgency': 'high' if timeframe_mapping.get(timeframe, 12) <= 6 else 'medium' if timeframe_mapping.get(timeframe, 12) <= 24 else 'low'
        }

    def _analyze_spending_priorities(self, responses: Dict[str, Any]) -> List[str]:
        """Analyze user's spending priorities from responses."""
        categories = responses.get('spending_categories', [])
        if isinstance(categories, str):
            # Handle single selection
            return [categories]
        return categories

    def _analyze_financial_knowledge(self, responses: Dict[str, Any]) -> str:
        """Analyze user's financial knowledge level from responses."""
        tracking_method = responses.get('spending_tracking', '')
        risk_knowledge = responses.get('risk_tolerance', '')
        
        # Simple scoring based on tracking sophistication and risk awareness
        knowledge_score = 0
        
        if 'app' in tracking_method.lower() or 'digital' in tracking_method.lower():
            knowledge_score += 2
        elif 'spreadsheet' in tracking_method.lower():
            knowledge_score += 1
        elif 'don\'t track' in tracking_method.lower():
            knowledge_score -= 1
            
        if 'don\'t know' in risk_knowledge.lower():
            knowledge_score -= 1
        elif 'moderate' in risk_knowledge.lower() or 'aggressive' in risk_knowledge.lower():
            knowledge_score += 1
            
        if knowledge_score >= 2:
            return 'high'
        elif knowledge_score >= 0:
            return 'medium'
        else:
            return 'low'

    def _analyze_motivation_factors(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user's motivation factors from responses."""
        motivation_style = responses.get('motivation_style', '')
        financial_stress = responses.get('financial_stress', 5)
        
        # Convert stress level to motivation urgency
        stress_level = int(financial_stress) if isinstance(financial_stress, (int, str)) else 5
        
        return {
            'style': motivation_style,
            'stress_level': stress_level,
            'urgency': 'high' if stress_level >= 7 else 'medium' if stress_level >= 4 else 'low',
            'needs_encouragement': stress_level >= 6
        }

    def _analyze_saving_methods(self, responses: Dict[str, Any]) -> List[str]:
        """Analyze preferred saving methods from responses."""
        difficulty = responses.get('saving_difficulty', '')
        tracking = responses.get('spending_tracking', '')
        
        methods = []
        
        # Suggest methods based on current challenges
        if 'motivation' in difficulty.lower():
            methods.extend(['gamification', 'social_challenges', 'milestone_rewards'])
        if 'expenses' in difficulty.lower():
            methods.extend(['automatic_transfers', 'category_limits', 'spending_alerts'])
        if 'goals' in difficulty.lower():
            methods.extend(['goal_setting_tools', 'progress_visualization'])
        if 'don\'t track' in tracking.lower():
            methods.extend(['automated_tracking', 'simple_budgeting'])
            
        return methods

    def _get_llm_analysis(self, responses: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get deeper analysis using LLM."""
        system_role = """
        You are a financial psychology expert analyzing quiz responses.
        Provide insights into the user's financial personality and recommend
        personalized strategies.
        """
        
        content = f"""
        Quiz Responses: {json.dumps(responses)}
        Initial Analysis: {json.dumps(analysis)}
        
        Provide deeper insights including:
        1. Financial personality type
        2. Key behavioral patterns
        3. Potential obstacles to saving
        4. Recommended intervention strategies
        5. Communication preferences
        
        Return as JSON with keys: personality_type, behavioral_patterns,
        obstacles, strategies, communication_style
        """
        
        try:
            return self.llm_client.query_financial_planner(
                content, system_role, return_json=True
            )
        except Exception:
            return {
                'personality_type': 'unknown',
                'behavioral_patterns': [],
                'obstacles': [],
                'strategies': [],
                'communication_style': 'balanced'
            } 