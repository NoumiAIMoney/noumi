"""
Noumi AI API Service
Provides REST API endpoints for financial planning and performance analysis.

Main Endpoints:
- POST /api/generate-weekly-plan: Generate weekly plan from user profile + transactions
- POST /api/generate-weekly-recap: Generate weekly recap from plan + actual transactions
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file if it exists."""
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

# Load environment variables at startup
load_env_file()

# Import Noumi agents
from noumi_agents.quiz_agent.financial_quiz_agent import FinancialQuizAgent
from noumi_agents.transaction_agent.plaid_transaction_agent import PlaidTransactionAgent
from noumi_agents.planning_agent.chain_of_guidance_planner import ChainOfGuidancePlanningAgent
from noumi_agents.planning_agent.recap_agent import RecapAgent
from noumi_agents.utils.llm_client import NoumiLLMClient

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize LLM client
try:
    llm_client = NoumiLLMClient(provider="google")
except Exception as e:
    logger.warning(f"LLM client initialization failed: {e}. Running in demo mode.")
    llm_client = None


class NoumiAPI:
    """Main API class for Noumi AI financial planning services."""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
    
    def process_user_profile(self, user_profile_json: Dict[str, Any]) -> Dict[str, Any]:
        """Process user profile through Quiz Agent."""
        try:
            quiz_agent = FinancialQuizAgent(llm_client=self.llm_client)
            user_preferences = quiz_agent.analyze_quiz_responses(user_profile_json)
            return user_preferences
        except Exception as e:
            logger.error(f"Error processing user profile: {e}")
            # Return minimal profile for demo purposes
            return {
                "user_id": user_profile_json.get("user_id", "demo_user"),
                "risk_tolerance": user_profile_json.get("risk_tolerance", "moderate"),
                "financial_knowledge": user_profile_json.get("financial_knowledge", "intermediate"),
                "savings_goals": {
                    "primary_goal": user_profile_json.get("savings_goal", "emergency_fund"),
                    "target_amount": user_profile_json.get("target_amount", 5000),
                    "timeline": user_profile_json.get("savings_timeframe", "6-12 months")
                },
                "spending_patterns": {
                    "problem_categories": user_profile_json.get("problem_categories", []),
                    "spending_personality": "planner"
                },
                "motivation_factors": {
                    "stress_level": user_profile_json.get("financial_stress", 5),
                    "primary_motivation": "milestones"
                },
                "analysis_timestamp": datetime.now().isoformat()
            }
    
    def analyze_transactions(self, user_id: str, transactions_json: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze transactions through Plaid Agent."""
        try:
            plaid_agent = PlaidTransactionAgent(
                user_id=user_id,
                transactions_data=transactions_json,
                llm_client=self.llm_client
            )
            spending_patterns = plaid_agent.analyze_spending_patterns()
            return spending_patterns
        except Exception as e:
            logger.error(f"Error analyzing transactions: {e}")
            # Return minimal analysis for demo purposes
            return {
                "user_id": user_id,
                "analysis_period": {
                    "transaction_count": len(transactions_json),
                    "start_date": "2024-05-01",
                    "end_date": "2024-06-15"
                },
                "category_analysis": self._basic_category_analysis(transactions_json),
                "monthly_analysis": {
                    "average_monthly_spending": sum(abs(t.get("amount", 0)) for t in transactions_json if t.get("amount", 0) < 0) / 1.5,
                    "spending_variance": 100.0
                },
                "analysis_timestamp": datetime.now().isoformat()
            }
    
    def _basic_category_analysis(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Basic category analysis for fallback."""
        categories = {}
        for transaction in transactions:
            amount = transaction.get("amount", 0)
            if amount >= 0:  # Skip income
                continue
            
            category = transaction.get("category", ["Other"])
            if isinstance(category, list):
                category = category[0] if category else "Other"
            
            if category not in categories:
                categories[category] = {
                    "total_amount": 0,
                    "transaction_count": 0,
                    "average_transaction": 0,
                    "percentage_of_spending": 0,
                    "trend": "stable"
                }
            
            categories[category]["total_amount"] += abs(amount)
            categories[category]["transaction_count"] += 1
        
        # Calculate averages
        total_spending = sum(cat["total_amount"] for cat in categories.values())
        for category, data in categories.items():
            if data["transaction_count"] > 0:
                data["average_transaction"] = data["total_amount"] / data["transaction_count"]
            if total_spending > 0:
                data["percentage_of_spending"] = (data["total_amount"] / total_spending) * 100
        
        return categories
    
    def generate_weekly_plan(self, user_preferences: Dict[str, Any], spending_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate weekly plan through Chain of Guidance Planner."""
        try:
            planner = ChainOfGuidancePlanningAgent(
                user_preferences=user_preferences,
                spending_analysis=spending_analysis,
                llm_client=self.llm_client
            )
            weekly_plan = planner.generate_weekly_plan()
            return weekly_plan
        except Exception as e:
            logger.error(f"Error generating weekly plan: {e}")
            # Return minimal plan for demo purposes
            return self._create_fallback_plan(user_preferences, spending_analysis)
    
    def _create_fallback_plan(self, user_preferences: Dict[str, Any], spending_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create a basic fallback weekly plan."""
        monthly_spending = spending_analysis.get("monthly_analysis", {}).get("average_monthly_spending", 1500)
        weekly_budget = monthly_spending / 4.33  # Convert monthly to weekly
        suggested_savings = min(weekly_budget * 0.2, 150)  # 20% savings target, max $150
        
        return {
            "week_start_date": datetime.now().strftime("%Y-%m-%d"),
            "ml_features": {
                "suggested_savings_amount": round(suggested_savings, 2),
                "spending_efficiency_score": 75
            },
            "savings_target": {
                "amount": round(suggested_savings, 2),
                "currency": "USD"
            },
            "spending_limits": {
                "Food and Drink": {
                    "daily_limit": round(weekly_budget * 0.35 / 7, 2),
                    "weekly_limit": round(weekly_budget * 0.35, 2)
                },
                "Entertainment": {
                    "daily_limit": round(weekly_budget * 0.15 / 7, 2),
                    "weekly_limit": round(weekly_budget * 0.15, 2)
                },
                "Transportation": {
                    "daily_limit": round(weekly_budget * 0.25 / 7, 2),
                    "weekly_limit": round(weekly_budget * 0.25, 2)
                },
                "Shopping": {
                    "daily_limit": round(weekly_budget * 0.25 / 7, 2),
                    "weekly_limit": round(weekly_budget * 0.25, 2)
                }
            },
            "daily_recommendations": [
                {
                    "day": "Monday",
                    "actions": ["Check account balance", "Set weekly spending goals"],
                    "focus_area": "Goal Setting",
                    "motivation": "Start your week strong!"
                },
                {
                    "day": "Tuesday",
                    "actions": ["Track all expenses", "Review yesterday's spending"],
                    "focus_area": "Expense Tracking",
                    "motivation": "Stay on track!"
                }
            ],
            "tracking_metrics": [
                {
                    "metric_name": "Weekly Savings",
                    "target_value": round(suggested_savings, 2),
                    "current_value": 0
                }
            ],
            "weekly_challenges": [
                "Track every expense for 7 days",
                "Cook at home 5 out of 7 days"
            ],
            "success_tips": [
                "Review progress daily",
                "Celebrate small wins"
            ]
        }
    
    def generate_weekly_recap(self, weekly_plan: Dict[str, Any], actual_transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate weekly recap through Recap Agent."""
        try:
            recap_agent = RecapAgent(
                weekly_plan=weekly_plan,
                actual_transactions=actual_transactions,
                llm_client=self.llm_client
            )
            weekly_recap = recap_agent.generate_weekly_recap()
            return weekly_recap
        except Exception as e:
            logger.error(f"Error generating weekly recap: {e}")
            # Return minimal recap for demo purposes
            return self._create_fallback_recap(weekly_plan, actual_transactions)
    
    def _create_fallback_recap(self, weekly_plan: Dict[str, Any], actual_transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a basic fallback weekly recap."""
        # Calculate actual spending
        total_actual = sum(abs(t.get("amount", 0)) for t in actual_transactions if t.get("amount", 0) < 0)
        
        # Get planned spending
        spending_limits = weekly_plan.get("spending_limits", {})
        total_planned = sum(cat.get("weekly_limit", 0) for cat in spending_limits.values())
        
        # Calculate performance metrics
        adherence_rate = min(total_planned / total_actual, 1.0) if total_actual > 0 else 1.0
        variance_pct = ((total_actual - total_planned) / total_planned * 100) if total_planned > 0 else 0
        performance_score = max(0, 100 - abs(variance_pct))
        
        return {
            "recap_metadata": {
                "week_period": f"{weekly_plan.get('week_start_date', 'Unknown')} to Present",
                "analysis_timestamp": datetime.now().isoformat(),
                "transaction_count": len(actual_transactions)
            },
            "spending_performance": {
                "total_planned_spending": round(total_planned, 2),
                "total_actual_spending": round(total_actual, 2),
                "planned_savings_target": weekly_plan.get("savings_target", {}).get("amount", 0),
                "spending_vs_plan": round(total_actual - total_planned, 2),
                "spending_adherence_rate": round(adherence_rate, 3),
                "over_budget": total_actual > total_planned,
                "budget_variance_percentage": round(variance_pct, 2)
            },
            "performance_scores": {
                "overall_performance_score": round(performance_score, 1),
                "spending_adherence_score": round(adherence_rate * 100, 1),
                "category_discipline_score": round(performance_score * 0.9, 1),
                "goal_achievement_score": round(performance_score * 0.95, 1),
                "performance_grade": self._get_grade(performance_score)
            },
            "ai_insights": {
                "key_insights": [
                    {
                        "insight_type": "performance",
                        "title": f"Overall Performance: {self._get_grade(performance_score)}",
                        "description": f"You spent ${total_actual:.2f} vs planned ${total_planned:.2f}",
                        "impact_level": "high"
                    }
                ],
                "success_highlights": [
                    "Successfully tracked expenses" if len(actual_transactions) > 0 else "Limited expense tracking"
                ],
                "improvement_areas": [
                    {
                        "area": "Budget adherence" if total_actual > total_planned else "Spending tracking",
                        "current_impact": f"{'Over' if total_actual > total_planned else 'Under'} budget by ${abs(total_actual - total_planned):.2f}",
                        "suggested_action": "Review spending patterns and adjust categories"
                    }
                ]
            },
            "recommendations": [
                {
                    "type": "budget_adjustment",
                    "priority": "medium",
                    "title": "Review Weekly Budget",
                    "description": f"Performance score: {performance_score:.1f}/100",
                    "specific_action": "Adjust category limits based on actual spending patterns"
                }
            ]
        }
    
    def _get_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90: return "A"
        elif score >= 80: return "B"
        elif score >= 70: return "C"
        elif score >= 60: return "D"
        else: return "F"


# Initialize API instance
noumi_api = NoumiAPI(llm_client=llm_client)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "Noumi AI API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/generate-weekly-plan', methods=['POST'])
def generate_weekly_plan():
    """
    Generate weekly financial plan.
    
    Expected JSON Input:
    {
        "user_profile": {
            "user_id": "string",
            "savings_goal": "emergency_fund",
            "monthly_income": 4500.0,
            "risk_tolerance": "moderate",
            "financial_knowledge": "intermediate",
            "financial_stress": 7,
            "problem_categories": ["Food and Drink", "Entertainment"]
        },
        "transactions": [
            {
                "transaction_id": "txn_001",
                "amount": -127.89,
                "description": "WHOLE FOODS MARKET",
                "category": ["Food and Drink"],
                "date": "2024-06-01"
            }
        ]
    }
    
    Returns: Weekly plan JSON with ml_features, spending_limits, etc.
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        
        # Validate required fields
        if 'user_profile' not in data:
            return jsonify({"error": "Missing 'user_profile' in request"}), 400
        if 'transactions' not in data:
            return jsonify({"error": "Missing 'transactions' in request"}), 400
        
        user_profile = data['user_profile']
        transactions = data['transactions']
        
        # Validate user_profile has required fields
        required_fields = ['user_id']
        for field in required_fields:
            if field not in user_profile:
                return jsonify({"error": f"Missing required field '{field}' in user_profile"}), 400
        
        logger.info(f"Processing weekly plan request for user: {user_profile.get('user_id')}")
        
        # Step 1: Process user profile through Quiz Agent
        user_preferences = noumi_api.process_user_profile(user_profile)
        
        # Step 2: Analyze transactions through Plaid Agent
        spending_analysis = noumi_api.analyze_transactions(
            user_id=user_profile['user_id'],
            transactions_json=transactions
        )
        
        # Step 3: Generate weekly plan through Chain of Guidance Planner
        weekly_plan = noumi_api.generate_weekly_plan(user_preferences, spending_analysis)
        
        # Add API metadata
        response = {
            "success": True,
            "weekly_plan": weekly_plan,
            "processing_metadata": {
                "user_id": user_profile['user_id'],
                "transactions_processed": len(transactions),
                "plan_generated_at": datetime.now().isoformat(),
                "ml_features_available": "ml_features" in weekly_plan
            }
        }
        
        logger.info(f"Successfully generated weekly plan for user: {user_profile.get('user_id')}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in generate_weekly_plan: {e}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e),
            "success": False
        }), 500


@app.route('/api/generate-weekly-recap', methods=['POST'])
def generate_weekly_recap():
    """
    Generate weekly performance recap.
    
    Expected JSON Input:
    {
        "weekly_plan": {
            "week_start_date": "2024-06-17",
            "ml_features": {
                "suggested_savings_amount": 125.50,
                "spending_efficiency_score": 78
            },
            "spending_limits": {
                "Food and Drink": {"weekly_limit": 175.00},
                "Entertainment": {"weekly_limit": 56.00}
            }
        },
        "actual_transactions": [
            {
                "transaction_id": "actual_001",
                "amount": -18.50,
                "description": "COFFEE SHOP",
                "category": "Food and Drink",
                "date": "2024-06-18"
            }
        ]
    }
    
    Returns: Weekly recap JSON with performance scores, insights, etc.
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        
        # Validate required fields
        if 'weekly_plan' not in data:
            return jsonify({"error": "Missing 'weekly_plan' in request"}), 400
        if 'actual_transactions' not in data:
            return jsonify({"error": "Missing 'actual_transactions' in request"}), 400
        
        weekly_plan = data['weekly_plan']
        actual_transactions = data['actual_transactions']
        
        logger.info(f"Processing weekly recap request with {len(actual_transactions)} transactions")
        
        # Generate weekly recap through Recap Agent
        weekly_recap = noumi_api.generate_weekly_recap(weekly_plan, actual_transactions)
        
        # Add API metadata
        response = {
            "success": True,
            "weekly_recap": weekly_recap,
            "processing_metadata": {
                "actual_transactions_processed": len(actual_transactions),
                "recap_generated_at": datetime.now().isoformat(),
                "performance_features_available": "performance_scores" in weekly_recap
            }
        }
        
        logger.info(f"Successfully generated weekly recap")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in generate_weekly_recap: {e}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e),
            "success": False
        }), 500


@app.route('/api/extract-ml-features', methods=['POST'])
def extract_ml_features():
    """
    Extract ML features from agent responses.
    
    Expected JSON Input:
    {
        "weekly_plan": { ... },
        "weekly_recap": { ... } (optional)
    }
    
    Returns: Extracted ML features for pipeline integration.
    """
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        
        if 'weekly_plan' not in data:
            return jsonify({"error": "Missing 'weekly_plan' in request"}), 400
        
        weekly_plan = data['weekly_plan']
        weekly_recap = data.get('weekly_recap')
        
        # Extract planning ML features
        ml_features = {
            "planning_features": {
                "suggested_savings_amount": weekly_plan.get("ml_features", {}).get("suggested_savings_amount"),
                "spending_efficiency_score": weekly_plan.get("ml_features", {}).get("spending_efficiency_score"),
                "total_weekly_budget": sum(
                    cat.get("weekly_limit", 0) 
                    for cat in weekly_plan.get("spending_limits", {}).values()
                ),
                "savings_target": weekly_plan.get("savings_target", {}).get("amount")
            }
        }
        
        # Extract performance ML features if recap provided
        if weekly_recap:
            ml_features["performance_features"] = {
                "overall_performance_score": weekly_recap.get("performance_scores", {}).get("overall_performance_score"),
                "spending_adherence_rate": weekly_recap.get("spending_performance", {}).get("spending_adherence_rate"),
                "budget_variance_percentage": weekly_recap.get("spending_performance", {}).get("budget_variance_percentage"),
                "categories_over_budget": len([
                    cat for cat in weekly_recap.get("category_performance", {}).values()
                    if cat.get("status") == "over_budget"
                ]),
                "performance_grade": weekly_recap.get("performance_scores", {}).get("performance_grade")
            }
        
        ml_features["extraction_metadata"] = {
            "extraction_timestamp": datetime.now().isoformat(),
            "planning_features_available": ml_features["planning_features"]["suggested_savings_amount"] is not None,
            "performance_features_available": "performance_features" in ml_features
        }
        
        return jsonify({
            "success": True,
            "ml_features": ml_features
        })
        
    except Exception as e:
        logger.error(f"Error in extract_ml_features: {e}")
        return jsonify({
            "error": "Internal server error", 
            "message": str(e),
            "success": False
        }), 500


if __name__ == '__main__':
    logger.info("Starting Noumi AI API server...")
    app.run(host='0.0.0.0', port=5001, debug=True) 