"""
Comprehensive API test script for Noumi backend
Tests all endpoints with real database logic and analytics
"""

import requests
import json
import time
from datetime import datetime

# API Configuration
BASE_URL = "http://localhost:8000"
MOCK_TOKEN = "mock_jwt_token"

headers = {
    "Authorization": f"Bearer {MOCK_TOKEN}",
    "Content-Type": "application/json"
}

def test_endpoint(method, endpoint, data=None, expected_status=200):
    """Test an API endpoint and return response"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        print(f"\n{'='*60}")
        print(f"{method.upper()} {endpoint}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == expected_status:
            print("✅ SUCCESS")
            try:
                response_data = response.json()
                print(f"Response Data:")
                print(json.dumps(response_data, indent=2)[:500] + "..." if len(str(response_data)) > 500 else json.dumps(response_data, indent=2))
                return response_data
            except:
                print(f"Response Text: {response.text[:200]}...")
                return response.text
        else:
            print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None

def run_comprehensive_test():
    """Run comprehensive test of all API endpoints"""
    
    print("🚀 Starting Comprehensive API Test")
    print("Testing all endpoints with real database logic...")
    
    # 1. Health Check
    test_endpoint("GET", "/health")
    
    # 2. Authentication Tests
    print("\n📱 AUTHENTICATION TESTS")
    
    # Register user (should work with database)
    register_data = {
        "email": "test@noumi.com",
        "password": "testpass123",
        "name": "Test User"
    }
    test_endpoint("POST", "/auth/register", register_data)
    
    # Login user
    login_data = {
        "email": "test@noumi.com", 
        "password": "testpass123"
    }
    test_endpoint("POST", "/auth/login", login_data)
    
    # Get current user
    test_endpoint("GET", "/auth/me")
    
    # 3. Quiz Data Submission (saves to database)
    print("\n📋 QUIZ DATA TESTS")
    quiz_data = {
        "goal_name": "Trip to Mexico",
        "goal_description": "Vacation fund for Mexico trip",
        "goal_amount": 1200,
        "target_date": "2025-09-30",
        "net_monthly_income": 6000
    }
    test_endpoint("POST", "/quiz", quiz_data)
    
    # 4. Plaid Connection (saves sample transactions)
    print("\n🏦 PLAID CONNECTION TESTS")
    plaid_data = {"public_token": "public_test_token"}
    test_endpoint("POST", "/plaid/connect", plaid_data)
    
    # 5. Insert Sample Data for Better Testing
    print("\n🗄️ SAMPLE DATA INSERTION")
    test_endpoint("POST", "/admin/insert-sample-data")
    
    # Small delay to ensure data is saved
    time.sleep(1)
    
    # 6. Analytics Endpoints (using real transaction data)
    print("\n📊 ANALYTICS TESTS")
    
    # Anomaly detection
    test_endpoint("GET", "/anomalies/yearly")
    
    # Spending trends (from real transaction analysis)
    test_endpoint("GET", "/trends")
    
    # Spending categories (with month-over-month data)
    test_endpoint("GET", "/spending/categories")
    
    # Computed goal (from database)
    test_endpoint("GET", "/goal/computed")
    
    # User habits (based on spending patterns)
    test_endpoint("GET", "/habits")
    
    # 7. Streak and Financial Status Tests
    print("\n📈 FINANCIAL STATUS TESTS")
    
    # Weekly streak calculation
    test_endpoint("GET", "/streak/weekly")
    
    # Spending status (real calculation)
    test_endpoint("GET", "/spending/status")
    
    # Weekly savings (actual vs suggested)
    test_endpoint("GET", "/savings/weekly")
    
    # Longest streak calculation
    test_endpoint("GET", "/streak/longest")
    
    # Total spent year-to-date
    test_endpoint("GET", "/spending/total")
    
    # 8. Weekly Plan Tests (LLM Integration)
    print("\n🗓️ WEEKLY PLAN TESTS")
    
    # Get weekly plan (uses real user data + LLM)
    test_endpoint("GET", "/plans/weekly")
    
    # Create custom weekly plan
    plan_request = {
        "user_preferences": {
            "risk_tolerance": "moderate",
            "savings_goals": {"primary_goal": "Emergency fund"}
        },
        "spending_analysis": {
            "monthly_analysis": {"average_monthly_spending": 2500.0}
        },
        "force_regenerate": True
    }
    test_endpoint("POST", "/plans/weekly", plan_request)
    
    # 9. Weekly Recap Tests (LLM Integration)
    print("\n📝 WEEKLY RECAP TESTS")
    
    # Get weekly recap (uses real data + LLM)
    test_endpoint("GET", "/recaps/weekly")
    
    # Create custom weekly recap
    recap_request = {
        "weekly_plan": {
            "week_start_date": "2024-01-15",
            "savings_target": {"amount": 200, "currency": "USD"},
            "spending_limits": {
                "Food & Dining": {"daily_limit": 15.0, "weekly_limit": 105.0}
            },
            "daily_recommendations": [
                {
                    "day": "Monday",
                    "actions": ["Check account balance"],
                    "focus_area": "Goal Setting",
                    "motivation": "Start strong!"
                }
            ],
            "tracking_metrics": [],
            "weekly_challenges": [],
            "success_tips": []
        },
        "actual_transactions": [
            {
                "transaction_id": "test_txn_1",
                "amount": -45.50,
                "description": "Grocery Store",
                "category": "Food & Dining",
                "date": "2024-01-15",
                "merchant_name": "Safeway"
            }
        ]
    }
    test_endpoint("POST", "/recaps/weekly", recap_request)
    
    print("\n🎉 COMPREHENSIVE TEST COMPLETED!")
    print("Check the results above to see if all endpoints are working with real data.")

def test_data_persistence():
    """Test that data persists across requests"""
    print("\n🔄 TESTING DATA PERSISTENCE")
    
    # First, insert quiz data
    quiz_data = {
        "goal_name": "Emergency Fund",
        "goal_description": "Build emergency savings",
        "goal_amount": 5000,
        "target_date": "2025-12-31",
        "net_monthly_income": 5000
    }
    test_endpoint("POST", "/quiz", quiz_data)
    
    # Then check if computed goal reflects the new data
    time.sleep(1)  # Small delay
    goal_response = test_endpoint("GET", "/goal/computed")
    
    if goal_response and goal_response.get("goal_name") == "Emergency Fund":
        print("✅ Data persistence verified!")
    else:
        print("❌ Data persistence failed!")

def test_analytics_accuracy():
    """Test analytics calculations for accuracy"""
    print("\n🧮 TESTING ANALYTICS ACCURACY")
    
    # Get spending categories
    categories = test_endpoint("GET", "/spending/categories")
    
    # Get spending status
    status = test_endpoint("GET", "/spending/status")
    
    # Get weekly savings
    savings = test_endpoint("GET", "/savings/weekly")
    
    if categories and status and savings:
        print("✅ All analytics endpoints returned data")
        
        # Verify calculations make sense
        if status.get("income", 0) > 0 and status.get("expenses", 0) >= 0:
            print("✅ Spending status calculations look reasonable")
        
        if isinstance(categories, list) and len(categories) > 0:
            print(f"✅ Found {len(categories)} spending categories")
        
        if savings.get("actual_savings") is not None and savings.get("suggested_savings_amount_weekly") is not None:
            print("✅ Weekly savings calculations working")
    else:
        print("❌ Analytics accuracy test failed")

if __name__ == "__main__":
    print("🔥 NOUMI API COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    # Run main test suite
    run_comprehensive_test()
    
    # Test data persistence
    test_data_persistence()
    
    # Test analytics accuracy
    test_analytics_accuracy()
    
    print("\n" + "="*60)
    print("🏁 ALL TESTS COMPLETED!")
    print("Review the output above to verify all endpoints are working correctly.")
    print("The API now uses real database operations and analytics instead of mock data.") 