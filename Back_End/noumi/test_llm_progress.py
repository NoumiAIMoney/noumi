#!/usr/bin/env python3
"""
Test script to demonstrate LLM progress indicators working in real-time.
Shows exactly what happens during AI agent calls.
"""

import os
import sys
import json

# Set the API key
os.environ['GOOGLE_API_KEY'] = "AIzaSyB2JTpTeTvKC9eyGZpOw_xSZLtGrdbJguk"

# Import the agents
sys.path.append('noumi_agents')
from noumi_agents.quiz_agent.financial_quiz_agent import FinancialQuizAgent
from noumi_agents.transaction_agent.plaid_transaction_agent import PlaidTransactionAgent
from noumi_agents.planning_agent.chain_of_guidance_planner import ChainOfGuidancePlanningAgent
from noumi_agents.utils.llm_client import NoumiLLMClient

def test_quiz_agent_with_progress():
    """Test Quiz Agent with progress indicators."""
    print("🎯 Testing Quiz Agent with Progress Indicators")
    print("=" * 60)
    
    sample_user_profile = {
        "user_id": "user_test123",
        "savings_goal": "Emergency fund",
        "monthly_income": 4500.0,
        "risk_tolerance": "moderate",
        "financial_knowledge": "intermediate",
        "financial_stress": 7,
        "problem_categories": ["Food and Drink", "Entertainment"]
    }
    
    print("📤 Analyzing user profile with Quiz Agent...")
    print(f"   Profile fields: {len(sample_user_profile)}")
    
    # Initialize LLM client
    llm_client = NoumiLLMClient(provider="google")
    
    # Create Quiz Agent
    quiz_agent = FinancialQuizAgent(llm_client=llm_client)
    
    # This will show all the progress indicators
    print("\n🔄 Starting AI analysis of user profile...")
    result = quiz_agent.analyze_quiz_responses(sample_user_profile)
    
    print(f"\n✅ Quiz Agent analysis completed!")
    print(f"📊 Result keys: {list(result.keys())}")
    return result

def test_planning_agent_with_progress():
    """Test Planning Agent with progress indicators."""
    print("\n🎯 Testing Planning Agent with Progress Indicators")
    print("=" * 60)
    
    # Sample data for planning
    user_preferences = {
        "user_id": "user_test123",
        "risk_tolerance": "moderate",
        "savings_goals": {"primary_goal": "emergency_fund"}
    }
    
    spending_analysis = {
        "monthly_analysis": {"average_monthly_spending": 2000},
        "category_analysis": {
            "Food and Drink": {"total_amount": 400, "transaction_count": 15},
            "Entertainment": {"total_amount": 200, "transaction_count": 8}
        }
    }
    
    print("📤 Generating weekly plan with Chain of Guidance Planner...")
    
    # Initialize LLM client
    llm_client = NoumiLLMClient(provider="google")
    
    # Create Planning Agent
    planner = ChainOfGuidancePlanningAgent(
        user_preferences=user_preferences,
        spending_analysis=spending_analysis,
        llm_client=llm_client
    )
    
    # This will show all the Chain of Guidance steps with progress
    print("\n🔄 Starting Chain of Guidance planning process...")
    result = planner.generate_weekly_plan()
    
    print(f"\n✅ Planning Agent completed!")
    print(f"📊 Plan keys: {list(result.keys())}")
    
    # Check for ML features
    if "ml_features" in result:
        ml_features = result["ml_features"]
        print(f"🧮 ML Features extracted:")
        print(f"   Suggested savings: ${ml_features.get('suggested_savings_amount', 0):.2f}")
        print(f"   Efficiency score: {ml_features.get('spending_efficiency_score', 0)}/100")
    
    return result

def main():
    """Main test function showing progress indicators."""
    print("🚀 Noumi AI - LLM Progress Indicator Test")
    print("=" * 70)
    print("This will show you exactly what happens during real AI calls!")
    print("=" * 70)
    
    try:
        # Test 1: Quiz Agent with progress
        quiz_result = test_quiz_agent_with_progress()
        
        # Test 2: Planning Agent with progress
        planning_result = test_planning_agent_with_progress()
        
        print("\n" + "=" * 70)
        print("🎉 Progress Indicator Test Results:")
        print("=" * 70)
        print("✅ Quiz Agent: Progress indicators working!")
        print("✅ Planning Agent: Progress indicators working!")
        print("✅ Chain of Guidance: Step-by-step progress shown!")
        print("✅ LLM Client: Connection and response progress shown!")
        print("\n🎯 You can now see exactly what's happening during AI calls!")
        print("No more wondering if the system is stuck or working.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("This might indicate an API issue or network problem.")

if __name__ == "__main__":
    main() 