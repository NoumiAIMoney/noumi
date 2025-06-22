"""
Chain of Guidance (CoG) Planning Agent for Noumi
Implements consistent weekly savings plans using multi-step refinement.
Based on research: arXiv:2502.15924 - Chain of Guidance for LLM Consistency
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

from .base_planning_agent import BasePlanningAgent
from ..utils.llm_client import NoumiLLMClient


class ChainOfGuidancePlanningAgent(BasePlanningAgent):
    """
    Chain of Guidance planning agent for consistent financial planning.
    
    CoG Process:
    1. Generate multiple planning options (divergent thinking)
    2. Refine and evaluate options (analytical thinking)  
    3. Select optimal plan (convergent thinking)
    4. Finalize consistent format with ML features (standardization)
    """

    def __init__(self, user_preferences: Dict[str, Any],
                 spending_analysis: Dict[str, Any],
                 llm_client: Optional[NoumiLLMClient] = None):
        super().__init__(user_preferences, spending_analysis)
        self.llm_client = llm_client or NoumiLLMClient(provider="google")
        self.cog_trace = []  # Track CoG steps for debugging

    def generate_weekly_plan(self) -> Dict[str, Any]:
        """
        Generate consistent weekly plan using Chain of Guidance methodology.
        """
        
        # CoG Step 1: Generate Multiple Options
        self._log_cog_step("Generating planning options")
        planning_options = self._cog_step1_generate_options()
        
        # CoG Step 2: Refine and Evaluate Options
        self._log_cog_step("Refining and evaluating options")
        refined_options = self._cog_step2_refine_options(planning_options)
        
        # CoG Step 3: Select Optimal Plan
        self._log_cog_step("Selecting optimal plan")
        selected_plan = self._cog_step3_select_plan(refined_options)
        
        # CoG Step 4: Standardize Format with ML Features
        self._log_cog_step("Finalizing consistent format with ML features")
        final_plan = self._cog_step4_standardize_format(selected_plan)
        
        self.savings_plan = final_plan
        return final_plan

    def _cog_step1_generate_options(self) -> Dict[str, Any]:
        """
        CoG Step 1: Generate comprehensive planning options.
        Focus: Creativity, breadth, comprehensive coverage
        """
        system_role = """
        You are a financial planning strategist generating comprehensive savings 
        options. Create diverse approaches covering all angles and possibilities.
        
        REQUIREMENTS:
        1. Generate 3-4 distinct planning approaches
        2. Cover conservative, moderate, and aggressive strategies
        3. Include specific spending adjustments for each category
        4. Provide concrete daily actions for each approach
        5. Base all numbers on provided spending data
        6. Include ML features for each option (suggested_savings_amount, 
           spending_efficiency_score)
        """

        content = f"""
        USER SPENDING DATA: {json.dumps(self.spending_analysis)}
        USER PREFERENCES: {json.dumps(self.user_preferences)}
        
        Generate diverse weekly savings plan options. Return ONLY valid JSON:
        {{
            "options": [
                {{
                    "id": "conservative|moderate|aggressive|creative",
                    "name": "Approach Name",
                    "weekly_savings_target": number,
                    "savings_rate": "percentage of income",
                    "ml_features": {{
                        "suggested_savings_amount": number,
                        "spending_efficiency_score": number
                    }},
                    "key_strategies": ["strategy1", "strategy2", "strategy3"],
                    "category_adjustments": {{
                        "Food and Drink": {{"reduction_pct": number, 
                                          "new_weekly_limit": number}},
                        "Entertainment": {{"reduction_pct": number, 
                                        "new_weekly_limit": number}}
                    }},
                    "daily_actions": [
                        "Monday: Specific action",
                        "Tuesday: Specific action"
                    ],
                    "risk_level": "low|medium|high",
                    "difficulty": "easy|medium|hard"
                }}
            ]
        }}
        """

        return self.llm_client.query_financial_planner(
            content, system_role, return_json=True
        )

    def _cog_step2_refine_options(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        CoG Step 2: Analytical evaluation and refinement.
        Focus: Feasibility, effectiveness, user alignment
        """
        system_role = """
        You are a financial planning analyst evaluating savings plan options.
        Apply rigorous analysis to score and improve each option.
        
        EVALUATION CRITERIA (0-10 scale):
        1. FEASIBILITY: Can user realistically achieve this?
        2. EFFECTIVENESS: Will this create meaningful savings?  
        3. SUSTAINABILITY: Can user maintain long-term?
        4. USER_ALIGNMENT: Matches user profile and preferences?
        
        Provide specific scores and improvements for each option.
        Refine ML features based on analysis.
        """

        content = f"""
        OPTIONS TO EVALUATE: {json.dumps(options)}
        USER CONTEXT: {json.dumps(self.user_preferences)}
        SPENDING REALITY: {json.dumps(self.spending_analysis)}
        
        Evaluate each option and provide improvements. Return ONLY valid JSON:
        {{
            "evaluated_options": [
                {{
                    "id": "same as original",
                    "scores": {{
                        "feasibility": number,
                        "effectiveness": number,
                        "sustainability": number,
                        "user_alignment": number,
                        "total_score": number
                    }},
                    "analysis": {{
                        "strengths": ["strength1", "strength2"],
                        "weaknesses": ["weakness1", "weakness2"],
                        "improvements": ["improvement1", "improvement2"],
                        "risk_assessment": "description"
                    }},
                    "improved_plan": {{
                        "weekly_savings_target": number,
                        "ml_features": {{
                            "suggested_savings_amount": number,
                            "spending_efficiency_score": number
                        }},
                        "category_adjustments": {{}},
                        "daily_actions": [],
                        "success_factors": ["factor1", "factor2"]
                    }}
                }}
            ],
            "ranking": ["option_id_1", "option_id_2", "option_id_3"],
            "top_recommendation": "option_id"
        }}
        """

        return self.llm_client.query_financial_planner(
            content, system_role, return_json=True
        )

    def _cog_step3_select_plan(self, refined_options: Dict[str, Any]) -> Dict[str, Any]:
        """
        CoG Step 3: Consistent plan selection using deterministic criteria.
        Focus: Reproducible decision-making, consistency
        """
        system_role = """
        You are a financial planning decision engine. Select the optimal plan 
        using DETERMINISTIC criteria to ensure identical choices for similar 
        user profiles.
        
        SELECTION ALGORITHM (weighted scoring):
        - User Alignment: 40% weight
        - Feasibility: 30% weight  
        - Effectiveness: 20% weight
        - Sustainability: 10% weight
        
        Always select highest weighted score. Break ties using feasibility.
        """

        content = f"""
        EVALUATED OPTIONS: {json.dumps(refined_options)}
        USER PROFILE: {json.dumps(self.user_preferences)}
        
        Apply deterministic selection algorithm. Return ONLY valid JSON:
        {{
            "selection_process": {{
                "weighted_scores": [
                    {{
                        "id": "option_id",
                        "alignment_weighted": number,
                        "feasibility_weighted": number,
                        "effectiveness_weighted": number,
                        "sustainability_weighted": number,
                        "final_score": number
                    }}
                ],
                "selection_reason": "Why this option scored highest",
                "tie_breaker_used": "none|feasibility|effectiveness",
                "consistency_note": "How this ensures reproducibility"
            }},
            "selected_plan": {{
                "selected_id": "winning_option_id",
                "confidence": "high|medium|low",
                "plan_summary": {{
                    "weekly_savings_target": number,
                    "ml_features": {{
                        "suggested_savings_amount": number,
                        "spending_efficiency_score": number
                    }},
                    "primary_strategy": "main strategy description",
                    "key_adjustments": {{}},
                    "implementation_steps": []
                }}
            }}
        }}
        """

        return self.llm_client.query_financial_planner(
            content, system_role, return_json=True
        )

    def _cog_step4_standardize_format(self, selected_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        CoG Step 4: Convert to standard format with consistent calculations 
        and ML features.
        Focus: Standardization, reproducibility, exact format compliance, 
        ML feature extraction
        """
        system_role = """
        You are a financial plan formatter ensuring absolute consistency in 
        output format and calculations. Use DETERMINISTIC formulas only.
        
        STANDARD CALCULATIONS:
        - Week start: Next Monday from today
        - Daily limits: Weekly limit / 7
        - Challenge count: Exactly 3 challenges
        - Success tips: Exactly 3 tips
        - Daily recommendations: 7 days, consistent structure
        
        ML FEATURE REQUIREMENTS:
        - suggested_savings_amount: Weekly savings target (extractable for ML)
        - spending_efficiency_score: 0-100 score of spending optimization 
          (extractable for ML)
        
        NO creative variations - use exact same language patterns.
        """

        # Calculate deterministic values
        today = datetime.now()
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        next_monday = today + timedelta(days=days_until_monday)

        content = f"""
        SELECTED PLAN: {json.dumps(selected_plan)}
        USER_DATA: {json.dumps(self.user_preferences)}
        SPENDING_DATA: {json.dumps(self.spending_analysis)}
        NEXT_MONDAY: {next_monday.strftime('%Y-%m-%d')}
        
        Convert to exact standard format with ML features. Return ONLY valid JSON:
        {{
            "week_start_date": "{next_monday.strftime('%Y-%m-%d')}",
            "ml_features": {{
                "suggested_savings_amount": number,
                "spending_efficiency_score": number
            }},
            "savings_target": {{
                "amount": number,
                "currency": "USD"
            }},
            "spending_limits": {{
                "Food and Drink": {{
                    "daily_limit": number,
                    "weekly_limit": number
                }},
                "Entertainment": {{
                    "daily_limit": number,
                    "weekly_limit": number
                }}
            }},
            "daily_recommendations": [
                {{
                    "day": "Monday",
                    "actions": ["Check account balance", "Set weekly goals"],
                    "focus_area": "Goal Setting",
                    "motivation": "Start your week strong!"
                }},
                {{
                    "day": "Tuesday", 
                    "actions": ["Track expenses", "Review spending limits"],
                    "focus_area": "Expense Tracking",
                    "motivation": "Stay on track!"
                }},
                {{
                    "day": "Wednesday",
                    "actions": ["Mid-week check-in", "Adjust if needed"],
                    "focus_area": "Progress Review",
                    "motivation": "You're halfway there!"
                }},
                {{
                    "day": "Thursday",
                    "actions": ["Evaluate spending", "Plan weekend budget"],
                    "focus_area": "Weekend Planning",
                    "motivation": "Prepare for success!"
                }},
                {{
                    "day": "Friday",
                    "actions": ["Review week's progress", "Set weekend limits"],
                    "focus_area": "Week Review",
                    "motivation": "Strong finish ahead!"
                }},
                {{
                    "day": "Saturday",
                    "actions": ["Track weekend spending", "Find free activities"],
                    "focus_area": "Weekend Management",
                    "motivation": "Smart weekend choices!"
                }},
                {{
                    "day": "Sunday",
                    "actions": ["Calculate weekly total", "Plan next week"],
                    "focus_area": "Weekly Wrap-up",
                    "motivation": "Prepare for another successful week!"
                }}
            ],
            "tracking_metrics": [
                {{
                    "metric_name": "Weekly Savings",
                    "target_value": number,
                    "current_value": 0
                }},
                {{
                    "metric_name": "Days Under Budget",
                    "target_value": 7,
                    "current_value": 0
                }}
            ],
            "weekly_challenges": [
                "Track every expense for 7 days",
                "Cook at home 5 out of 7 days", 
                "Find one free entertainment activity"
            ],
            "success_tips": [
                "Review progress daily",
                "Celebrate small wins",
                "Stay consistent with tracking"
            ]
        }}
        """

        return self.llm_client.query_financial_planner(
            content, system_role, return_json=True
        )

    def _log_cog_step(self, step_description: str):
        """Log Chain of Guidance steps for transparency."""
        self.cog_trace.append({
            "timestamp": datetime.now().isoformat(),
            "step": len(self.cog_trace) + 1,
            "description": step_description
        })
        print(f"🔄 CoG Step {len(self.cog_trace)}: {step_description}")

    def get_cog_trace(self) -> List[Dict[str, Any]]:
        """Return Chain of Guidance execution trace for debugging."""
        return self.cog_trace

    def extract_ml_features(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract ML features from the generated plan for machine learning 
        workflow.
        
        Args:
            plan: Generated weekly plan
            
        Returns:
            Dictionary containing extractable ML features
        """
        try:
            ml_features = plan.get('ml_features', {})
            return {
                'suggested_savings_amount': ml_features.get(
                    'suggested_savings_amount'
                ),
                'spending_efficiency_score': ml_features.get(
                    'spending_efficiency_score'
                ),
                'extraction_successful': True,
                'extraction_timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'suggested_savings_amount': None,
                'spending_efficiency_score': None,
                'extraction_successful': False,
                'error': str(e),
                'extraction_timestamp': datetime.now().isoformat()
            }

    def _get_top_spending_category(self) -> str:
        """Get top spending category using consistent logic."""
        if (not self.spending_analysis or 
            'category_analysis' not in self.spending_analysis):
            print("No spending analysis or category analysis found. "
                  "Returning default category.")
            return "Food and Drink"  # Default fallback
        
        categories = self.spending_analysis['category_analysis']
        if not categories:
            print("No categories found. Returning default category.")
            return "Food and Drink"
        
        # Return category with highest total_amount
        top_category = max(categories.items(), 
                          key=lambda x: x[1].get('total_amount', 0))[0]
        return top_category 