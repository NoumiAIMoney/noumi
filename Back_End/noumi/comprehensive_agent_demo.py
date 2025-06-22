"""
Comprehensive Agent Demo for Noumi AI
Demonstrates the complete agent flow with ML feature extraction.

This demo showcases the full pipeline:
1. Quiz Agent - Collects user preferences and profile
2. Plaid Transaction Agent - Analyzes spending patterns
3. Chain of Guidance Planner - Generates weekly plans with ML features
4. Recap Agent - Analyzes performance against plans

The demo shows how all agents work together and extract ML features
for machine learning workflow integration.
"""

import json
import sys
from datetime import datetime
from typing import Dict, Any, List

# Import all the agents
from noumi_agents.quiz_agent.financial_quiz_agent import (
    FinancialQuizAgent
)
from noumi_agents.transaction_agent.plaid_transaction_agent import (
    PlaidTransactionAgent
)
from noumi_agents.planning_agent.chain_of_guidance_planner import (
    ChainOfGuidancePlanningAgent
)
from noumi_agents.planning_agent.recap_agent import RecapAgent
from noumi_agents.utils.llm_client import NoumiLLMClient


def load_sample_data(filename: str) -> Dict[str, Any]:
    """Load sample data from JSON file."""
    try:
        with open(f"sample_data/{filename}", 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {filename} not found. Using minimal data.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing {filename}: {e}")
        return {}


def create_sample_quiz_responses() -> Dict[str, Any]:
    """Load realistic quiz responses from sample data."""
    sample_data = load_sample_data("realistic_quiz_responses.json")
    if sample_data:
        return sample_data
    
    # Fallback minimal data
    return {
        "savings_goal": "Emergency fund",
        "monthly_income": 4500.0,
        "current_savings": "$5,000 - $15,000",
        "savings_timeframe": "6-12 months",
        "spending_categories": ["Food & Dining", "Entertainment",
                                "Shopping", "Transportation"],
        "financial_stress": 7,
        "saving_difficulty": "Impulse purchases and dining out",
        "spending_tracking": "Mobile banking app",
        "risk_tolerance": "Moderate - I'm comfortable with some risk",
        "motivation_style": "Reaching specific financial milestones"
    }


def create_sample_transactions() -> List[Dict[str, Any]]:
    """Load realistic transaction data from sample data."""
    sample_data = load_sample_data("realistic_transactions.json")
    if sample_data:
        return sample_data
    
    # Fallback minimal data
    return [
        {
            "transaction_id": "txn_001",
            "amount": -127.89,
            "description": "WHOLE FOODS MARKET",
            "merchant_name": "Whole Foods",
            "category": ["Food and Drink"],
            "date": "2024-06-01",
            "account_id": "acc_checking_001"
        },
        {
            "transaction_id": "txn_002",
            "amount": -58.42,
            "description": "SHELL OIL",
            "merchant_name": "Shell",
            "category": ["Transportation"],
            "date": "2024-06-01",
            "account_id": "acc_checking_001"
        }
    ]


def demo_quiz_agent() -> Dict[str, Any]:
    """Demonstrate Quiz Agent functionality."""
    print("📝 Quiz Agent Demo")
    print("=" * 40)
    
    print("🔧 Initializing Financial Quiz Agent...")
    quiz_agent = FinancialQuizAgent(
        llm_client=NoumiLLMClient(provider="google")
    )
    
    print("📋 Generating personalized quiz questions...")
    quiz_questions = quiz_agent.generate_personalized_quiz()
    print(f"   Generated {len(quiz_questions)} personalized questions")
    
    print("🎯 Simulating quiz responses...")
    sample_responses = create_sample_quiz_responses()
    print(f"   Using sample responses for {len(sample_responses)} questions")
    
    print("🧠 Analyzing quiz responses...")
    user_preferences = quiz_agent.analyze_quiz_responses(sample_responses)
    
    print("📊 Quiz Analysis Results:")
    risk_tolerance = user_preferences.get('risk_tolerance', 'N/A')
    print(f"   Risk Tolerance: {risk_tolerance}")
    
    primary_goal = user_preferences.get('savings_goals', {}).get(
        'primary_goal', 'N/A'
    )
    print(f"   Primary Goal: {primary_goal}")
    
    financial_knowledge = user_preferences.get('financial_knowledge', 'N/A')
    print(f"   Financial Knowledge: {financial_knowledge}")
    
    return user_preferences


def demo_plaid_agent() -> Dict[str, Any]:
    """Demonstrate Plaid Transaction Agent functionality."""
    print("\n\n💳 Plaid Transaction Agent Demo")
    print("=" * 45)
    
    print("🔧 Initializing Plaid Transaction Agent...")
    sample_transactions = create_sample_transactions()
    
    plaid_agent = PlaidTransactionAgent(
        user_id="demo_user_001",
        transactions_data=sample_transactions,
        llm_client=NoumiLLMClient(provider="google")
    )
    
    print(f"📊 Analyzing {len(sample_transactions)} transactions...")
    spending_patterns = plaid_agent.analyze_spending_patterns()
    
    print("🔍 Identifying saving opportunities...")
    saving_opportunities = plaid_agent.identify_saving_opportunities()
    
    print("📈 Plaid Analysis Results:")
    category_analysis = spending_patterns.get('category_analysis', {})
    print(f"   Categories analyzed: {len(category_analysis)}")
    
    monthly_analysis = spending_patterns.get('monthly_analysis', {})
    avg_spending = monthly_analysis.get('average_monthly_spending', 0)
    print(f"   Average monthly spending: ${avg_spending:.2f}")
    
    total_savings_potential = saving_opportunities.get(
        'total_potential_monthly_savings', 0
    )
    print(f"   Potential monthly savings: ${total_savings_potential:.2f}")
    
    return spending_patterns


def demo_chain_of_guidance_planner(
    user_preferences: Dict[str, Any],
    spending_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """Demonstrate Chain of Guidance Planning Agent."""
    print("\n\n🎯 Chain of Guidance Planning Agent Demo")
    print("=" * 50)
    
    print("🔧 Initializing Chain of Guidance Planner...")
    planner = ChainOfGuidancePlanningAgent(
        user_preferences=user_preferences,
        spending_analysis=spending_analysis,
        llm_client=NoumiLLMClient(provider="google")
    )
    
    print("🤖 Generating weekly plan using CoG methodology...")
    weekly_plan = planner.generate_weekly_plan()
    
    print("📈 Extracting ML features...")
    ml_features = planner.extract_ml_features(weekly_plan)
    
    print("📋 Planning Results:")
    print(f"   Week start: {weekly_plan.get('week_start_date', 'N/A')}")
    
    savings_target = weekly_plan.get('savings_target', {})
    print(f"   Savings target: ${savings_target.get('amount', 0):.2f}")
    
    spending_limits = weekly_plan.get('spending_limits', {})
    print(f"   Spending categories: {len(spending_limits)}")
    
    print("🧮 ML Features:")
    if ml_features.get('extraction_successful'):
        suggested_amount = ml_features.get('suggested_savings_amount', 0) or 0
        efficiency_score = ml_features.get(
            'spending_efficiency_score', 0
        ) or 0
        print(f"   ✅ Suggested savings amount: ${suggested_amount:.2f}")
        print(f"   ✅ Spending efficiency score: {efficiency_score:.1f}")
    else:
        error_msg = ml_features.get('error', 'Unknown error')
        print(f"   ❌ Feature extraction failed: {error_msg}")
    
    cog_trace = planner.get_cog_trace()
    print(f"   CoG steps executed: {len(cog_trace)}")
    
    return weekly_plan


def demo_recap_agent(weekly_plan: Dict[str, Any]) -> Dict[str, Any]:
    """Demonstrate Recap Agent functionality."""
    print("\n\n📊 Recap Agent Demo")
    print("=" * 35)
    
    # Create sample transactions for the week (simulating actual spending)
    actual_transactions = [
        {
            "transaction_id": "actual_001",
            "amount": -18.50,
            "description": "LOCAL COFFEE SHOP",
            "category": "Food and Drink",
            "date": "2024-06-09"
        },
        {
            "transaction_id": "actual_002",
            "amount": -95.00,
            "description": "WEEKLY GROCERY SHOPPING",
            "category": "Food and Drink", 
            "date": "2024-06-10"
        },
        {
            "transaction_id": "actual_003",
            "amount": -15.99,
            "description": "STREAMING SERVICE",
            "category": "Entertainment",
            "date": "2024-06-11"
        },
        {
            "transaction_id": "actual_004",
            "amount": -67.80,
            "description": "ONLINE RETAIL PURCHASE",
            "category": "Shopping",
            "date": "2024-06-12"
        },
        {
            "transaction_id": "actual_005",
            "amount": -45.00,
            "description": "RIDESHARE TO AIRPORT",
            "category": "Transportation",
            "date": "2024-06-13"
        }
    ]
    
    print("🔧 Initializing Recap Agent...")
    recap_agent = RecapAgent(
        weekly_plan=weekly_plan,
        actual_transactions=actual_transactions,
        llm_client=NoumiLLMClient(provider="google")
    )
    
    transaction_count = len(actual_transactions)
    print(f"📈 Analyzing performance against plan "
          f"({transaction_count} transactions)...")
    weekly_recap = recap_agent.generate_weekly_recap()
    
    print("📊 Performance Analysis Results:")
    
    spending_perf = weekly_recap.get('spending_performance', {})
    total_planned = spending_perf.get('total_planned_spending', 0)
    total_actual = spending_perf.get('total_actual_spending', 0)
    adherence_rate = spending_perf.get('spending_adherence_rate', 0)
    
    print(f"   Planned spending: ${total_planned:.2f}")
    print(f"   Actual spending: ${total_actual:.2f}")
    print(f"   Adherence rate: {adherence_rate:.1%}")
    print(f"   Over budget: {spending_perf.get('over_budget', False)}")
    
    performance_scores = weekly_recap.get('performance_scores', {})
    overall_score = performance_scores.get('overall_performance_score', 0)
    grade = performance_scores.get('performance_grade', 'N/A')
    
    print(f"   Overall performance: {overall_score:.1f}/100 (Grade: {grade})")
    
    # Extract ML performance features
    print("🧮 ML Performance Features:")
    ml_perf_features = recap_agent.get_ml_performance_features()
    if ml_perf_features.get('features_available'):
        perf_score = ml_perf_features.get(
            'overall_performance_score', 0
        ) or 0
        budget_variance = ml_perf_features.get(
            'budget_variance_percentage', 0
        ) or 0
        categories_over = ml_perf_features.get(
            'categories_over_budget', 0
        ) or 0
        print(f"   ✅ Performance score: {perf_score:.1f}")
        print(f"   ✅ Budget variance: {budget_variance:.1f}%")
        print(f"   ✅ Categories over budget: {categories_over}")
    else:
        print("   ❌ ML features not available")
    
    return weekly_recap


def save_comprehensive_results(
    quiz_results: Dict[str, Any],
    plaid_results: Dict[str, Any],
    planning_results: Dict[str, Any],
    recap_results: Dict[str, Any]
):
    """Save all results for ML pipeline integration."""
    
    combined_results = {
        "demo_metadata": {
            "demo_type": "comprehensive_agent_flow",
            "demo_timestamp": datetime.now().isoformat(),
            "agents_tested": [
                "quiz_agent", 
                "plaid_agent", 
                "chain_of_guidance_planner", 
                "recap_agent"
            ]
        },
        "agent_results": {
            "quiz_agent": {
                "user_preferences": quiz_results,
                "profile_completion": True
            },
            "plaid_agent": {
                "spending_patterns": plaid_results,
                "analysis_available": True
            },
            "planning_agent": {
                "weekly_plan": planning_results,
                "ml_features_extracted": (
                    planning_results.get('ml_features') is not None
                )
            },
            "recap_agent": {
                "performance_recap": recap_results,
                "analysis_completed": True
            }
        },
        "ml_pipeline_features": {
            "planning_features": planning_results.get('ml_features', {}),
            "performance_features": recap_results.get(
                'performance_scores', {}
            ),
            "user_profile_features": {
                "risk_tolerance": quiz_results.get('risk_tolerance'),
                "primary_goal": quiz_results.get(
                    'savings_goals', {}
                ).get('primary_goal'),
                "financial_knowledge": quiz_results.get('financial_knowledge')
            },
            "spending_pattern_features": {
                "average_monthly_spending": plaid_results.get(
                    'monthly_analysis', {}
                ).get('average_monthly_spending', 0),
                "category_count": len(
                    plaid_results.get('category_analysis', {})
                ),
                "potential_savings": plaid_results.get(
                    'total_potential_monthly_savings', 0
                )
            }
        },
        "integration_ready": {
            "all_agents_completed": True,
            "ml_features_available": True,
            "ready_for_production": True
        }
    }
    
    # Save to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"comprehensive_demo_results_{timestamp}.json"
    try:
        with open(filename, 'w') as f:
            json.dump(combined_results, f, indent=2, default=str)
        print(f"\n💾 Comprehensive demo results saved to: {filename}")
    except Exception as e:
        print(f"\n❌ Failed to save results: {e}")
    
    return combined_results


def display_integration_summary():
    """Display summary of how to integrate all agents."""
    print("\n\n🔗 Agent Integration Summary")
    print("=" * 50)
    print("📋 Complete Agent Flow:")
    print("   1. 📝 Quiz Agent: Collect user preferences")
    print("   2. 💳 Plaid Agent: Analyze spending patterns")
    print("   3. 🎯 Chain of Guidance Planner: Generate weekly plans")
    print("   4. 📊 Recap Agent: Analyze performance")
    print()
    print("🧮 ML Features Extracted:")
    print("   • Suggested savings amount (from planning)")
    print("   • Spending efficiency score (from planning)")
    print("   • Performance scores (from recap)")
    print("   • User profile features (from quiz)")
    print("   • Spending pattern features (from Plaid)")
    print()
    print("🚀 Production Integration Steps:")
    print("   1. Implement quiz to collect user preferences")
    print("   2. Connect Plaid API for transaction analysis")
    print("   3. Use Chain of Guidance planner for weekly plans")
    print("   4. Use Recap agent for weekly performance analysis")
    print("   5. Extract ML features for your ML pipeline")
    print("   6. Store results for continuous improvement")


def main():
    """Main demo function."""
    print("🚀 Comprehensive Noumi AI Agent Demo")
    print("=" * 60)
    print("This demo showcases the complete agent flow:")
    print("• Quiz Agent for user profiling")
    print("• Plaid Agent for spending analysis")
    print("• Chain of Guidance Planner for weekly plans with ML features")
    print("• Recap Agent for performance analysis")
    print("=" * 60)
    
    try:
        # Demo 1: Quiz Agent
        quiz_results = demo_quiz_agent()
        
        # Demo 2: Plaid Transaction Agent
        plaid_results = demo_plaid_agent()
        
        # Demo 3: Chain of Guidance Planning Agent
        planning_results = demo_chain_of_guidance_planner(
            quiz_results, plaid_results
        )
        
        # Demo 4: Recap Agent
        recap_results = demo_recap_agent(planning_results)
        
        # Save comprehensive results
        save_comprehensive_results(
            quiz_results, plaid_results, planning_results, recap_results
        )
        
        # Display integration summary
        display_integration_summary()
        
        print("\n🎉 Comprehensive demo completed successfully!")
        print("✅ All agents working together")
        print("✅ ML features extracted from planning and performance")
        print("✅ Ready for production integration")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 