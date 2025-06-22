#!/usr/bin/env python3
"""
Quick test to verify real LLM calls are working instead of demo mode.
"""

import os
import sys

# Set the API key
os.environ['GOOGLE_API_KEY'] = "AIzaSyB2JTpTeTvKC9eyGZpOw_xSZLtGrdbJguk"

# Import the LLM client
sys.path.append('noumi_agents/utils')
from llm_client import NoumiLLMClient

def test_real_llm():
    """Test if real LLM calls are working."""
    print("🧪 Testing Real LLM Calls")
    print("=" * 50)
    
    # Initialize LLM client
    client = NoumiLLMClient(provider="google")
    
    if not client.client:
        print("❌ LLM client not available - still in demo mode")
        return False
    
    print("✅ LLM client initialized successfully!")
    
    # Test a simple query
    test_prompt = "Generate a simple financial tip in 1 sentence."
    system_role = "You are a helpful financial advisor."
    
    print(f"🤖 Testing query: {test_prompt}")
    
    try:
        response = client.query_financial_planner(
            content=test_prompt,
            system_role=system_role,
            return_json=False
        )
        
        print(f"✅ Real LLM Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ LLM query failed: {e}")
        return False

def test_json_response():
    """Test LLM JSON response."""
    print("\n🧪 Testing JSON Response")
    print("=" * 50)
    
    client = NoumiLLMClient(provider="google")
    
    test_prompt = "Create a simple savings goal with amount and timeline."
    system_role = """You are a financial planner. Return JSON with exactly:
    {"goal": "goal_name", "amount": 1000, "timeline": "6 months"}"""
    
    try:
        response = client.query_financial_planner(
            content=test_prompt,
            system_role=system_role,
            return_json=True
        )
        
        print(f"✅ JSON Response: {response}")
        print(f"✅ Type: {type(response)}")
        
        if isinstance(response, dict):
            print("✅ Successfully parsed as JSON!")
            return True
        else:
            print("⚠️  Response not parsed as JSON")
            return False
            
    except Exception as e:
        print(f"❌ JSON query failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Noumi AI - Real LLM Test")
    print("=" * 60)
    
    # Test 1: Basic LLM call
    basic_test = test_real_llm()
    
    # Test 2: JSON response
    json_test = test_json_response()
    
    print("\n" + "=" * 60)
    print("🎯 Test Results:")
    print(f"✅ Basic LLM Call: {'PASS' if basic_test else 'FAIL'}")
    print(f"✅ JSON Response: {'PASS' if json_test else 'FAIL'}")
    
    if basic_test and json_test:
        print("\n🎉 SUCCESS: Real LLM calls are working!")
        print("Your API examples will now use actual AI instead of demo mode.")
    else:
        print("\n❌ FAILURE: Still using demo mode.")
        print("Check your API key configuration.") 