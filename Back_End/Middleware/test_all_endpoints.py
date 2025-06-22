#!/usr/bin/env python3
"""
Comprehensive test script for all Noumi API endpoints
Tests all endpoints according to the OpenAPI specification
"""

import requests
import json
from datetime import date, datetime

BASE_URL = "http://127.0.0.1:8000"


def get_auth_token():
    """Get authentication token for testing"""
    print("🔐 Getting authentication token...")
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        token = response.json()["token"]
        print(f"✅ Got token: {token}")
        return token
    else:
        print(f"❌ Failed to get token: {response.text}")
        return None


def test_endpoint(method, endpoint, data=None, token=None, description=""):
    """Test a single endpoint"""
    print(f"\n🔍 Testing {method} {endpoint}")
    print(f"📝 {description}")
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", 
                                   json=data, headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ Success!")
            print(f"Response: {json.dumps(result, indent=2, default=str)}")
            return result
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None


def main():
    """Run comprehensive API tests"""
    print("🚀 Testing Noumi API - All Endpoints")
    print("=" * 60)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    print("\n" + "=" * 60)
    print("🔧 TESTING OPENAPI SPECIFICATION ENDPOINTS")
    print("=" * 60)
    
    # Test 1: Submit Quiz Data
    quiz_data = {
        "goal_name": "Emergency Fund",
        "goal_description": "Build a 6-month emergency fund for financial security",
        "goal_amount": 10000.00,
        "target_date": "2024-12-31",
        "net_monthly_income": 5000.00
    }
    test_endpoint("POST", "/quiz", quiz_data, token, 
                 "Submit quiz data with financial goals and income")
    
    # Test 2: Plaid Connection
    plaid_data = {
        "public_token": "public-sandbox-12345"
    }
    test_endpoint("POST", "/plaid/connect", plaid_data, token,
                 "Initiate Plaid connection and fetch account data")
    
    # Test 3: Get Yearly Anomaly Counts
    test_endpoint("GET", "/anomalies/yearly", None, token,
                 "Get yearly anomaly counts (monthly breakdown)")
    
    # Test 4: Get Spending Trends
    test_endpoint("GET", "/trends", None, token,
                 "Get spending trends from LLM analysis")
    
    # Test 5: Get Spending Categories
    test_endpoint("GET", "/spending/categories", None, token,
                 "Get spending breakdown by category")
    
    # Test 6: Get Computed Goal Data
    test_endpoint("GET", "/goal/computed", None, token,
                 "Get computed goal data from quiz responses")
    
    # Test 7: Get User Habits
    test_endpoint("GET", "/habits", None, token,
                 "Get LLM-suggested user habits")
    
    # Test 8: Get Weekly Streak
    test_endpoint("GET", "/streak/weekly", None, token,
                 "Get weekly streak of no anomalies")
    
    # Test 9: Get Spending Status
    test_endpoint("GET", "/spending/status", None, token,
                 "Get current financial status for home screen")
    
    # Test 10: Get Weekly Savings Data
    test_endpoint("GET", "/savings/weekly", None, token,
                 "Get weekly savings comparison data")
    
    # Test 11: Get Longest Streak
    test_endpoint("GET", "/streak/longest", None, token,
                 "Get longest no-anomaly streak for the year")
    
    # Test 12: Get Total Amount Spent
    test_endpoint("GET", "/spending/total", None, token,
                 "Get total amount spent so far this year")
    
    print("\n" + "=" * 60)
    print("🔧 TESTING WEEKLY PLAN & RECAP ENDPOINTS")
    print("=" * 60)
    
    # Test 13: Get Weekly Plan (LLM Generated)
    weekly_plan = test_endpoint("GET", "/plans/weekly", None, token,
                               "Get LLM-generated weekly plan")
    
    # Test 14: Create New Weekly Plan
    plan_request = {
        "user_preferences": {
            "risk_tolerance": "aggressive",
            "savings_goals": {"primary_goal": "Vacation fund"}
        },
        "force_regenerate": True
    }
    test_endpoint("POST", "/plans/weekly", plan_request, token,
                 "Create new weekly plan with custom preferences")
    
    # Test 15: Get Weekly Recap (LLM Generated)
    test_endpoint("GET", "/recaps/weekly", None, token,
                 "Get LLM-generated weekly recap")
    
    # Test 16: Create Weekly Recap with Real Data
    if weekly_plan:
        recap_request = {
            "weekly_plan": weekly_plan,
            "actual_transactions": [
                {
                    "transaction_id": "test_1",
                    "amount": -75.50,
                    "description": "Grocery shopping",
                    "category": "Food & Dining",
                    "date": "2025-06-21"
                },
                {
                    "transaction_id": "test_2",
                    "amount": -25.00,
                    "description": "Gas station",
                    "category": "Transportation", 
                    "date": "2025-06-22"
                }
            ]
        }
        test_endpoint("POST", "/recaps/weekly", recap_request, token,
                     "Create weekly recap with actual transaction data")
    
    print("\n" + "=" * 60)
    print("🔧 TESTING AUTHENTICATION ENDPOINTS")
    print("=" * 60)
    
    # Test Authentication Endpoints
    test_endpoint("GET", "/auth/me", None, token,
                 "Get current user information")
    
    print("\n" + "=" * 60)
    print("🔧 TESTING HEALTH ENDPOINTS")
    print("=" * 60)
    
    # Test Health Endpoints
    test_endpoint("GET", "/", None, None,
                 "Root endpoint health check")
    
    test_endpoint("GET", "/health", None, None,
                 "Health check endpoint")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED!")
    print("📚 API Documentation available at:")
    print(f"   - Swagger UI: {BASE_URL}/docs")
    print(f"   - ReDoc: {BASE_URL}/redoc")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API server.")
        print("Make sure the server is running on http://127.0.0.1:8000")
        print("Run: cd Back_End/Middleware && python main.py") 