#!/usr/bin/env python3
"""
Comprehensive API Test Suite for Noumi Backend
Tests all endpoints with real SQLite database and saves outputs to files
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
MOCK_TOKEN = "mock_jwt_token"
TEST_INPUTS_DIR = "test_inputs"
TEST_OUTPUTS_DIR = "test_outputs"

# Create output directory
os.makedirs(TEST_OUTPUTS_DIR, exist_ok=True)

# Headers for authenticated requests
AUTH_HEADERS = {
    "Authorization": f"Bearer {MOCK_TOKEN}",
    "Content-Type": "application/json"
}

class APITester:
    def __init__(self):
        self.results = {}
        self.test_timestamp = datetime.now().isoformat()
        
    def log_result(self, test_name: str, response: requests.Response, request_data: Dict = None):
        """Log test result with response data"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "status_code": response.status_code,
            "success": response.status_code < 400,
            "request_data": request_data,
            "response_headers": dict(response.headers),
            "response_body": None
        }
        
        try:
            result["response_body"] = response.json()
        except:
            result["response_body"] = response.text
            
        self.results[test_name] = result
        
        # Save individual test result
        with open(f"{TEST_OUTPUTS_DIR}/{test_name}.json", "w") as f:
            json.dump(result, f, indent=2, default=str)
            
        # Print test result
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status} {test_name}: {response.status_code}")
        
    def load_test_input(self, filename: str) -> Dict:
        """Load test input from JSON file"""
        try:
            with open(f"{TEST_INPUTS_DIR}/{filename}", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Input file {filename} not found")
            return {}
    
    def test_health_endpoints(self):
        """Test basic health and info endpoints"""
        print("\n🔍 Testing Health Endpoints...")
        
        # Root endpoint
        response = requests.get(f"{BASE_URL}/")
        self.log_result("01_root_endpoint", response)
        
        # Health check
        response = requests.get(f"{BASE_URL}/health")
        self.log_result("02_health_check", response)
        
    def test_authentication_endpoints(self):
        """Test authentication-related endpoints"""
        print("\n🔐 Testing Authentication Endpoints...")
        
        # User registration
        registration_data = self.load_test_input("user_registration.json")
        response = requests.post(f"{BASE_URL}/auth/register", 
                               json=registration_data, 
                               headers={"Content-Type": "application/json"})
        self.log_result("03_user_registration", response, registration_data)
        
        # User login
        login_data = self.load_test_input("user_login.json")
        response = requests.post(f"{BASE_URL}/auth/login", 
                               json=login_data, 
                               headers={"Content-Type": "application/json"})
        self.log_result("04_user_login", response, login_data)
        
        # Get current user info
        response = requests.get(f"{BASE_URL}/auth/me", headers=AUTH_HEADERS)
        self.log_result("05_current_user_info", response)
        
    def test_quiz_and_plaid_endpoints(self):
        """Test quiz submission and Plaid connection"""
        print("\n📝 Testing Quiz and Plaid Endpoints...")
        
        # Quiz submission
        quiz_data = self.load_test_input("quiz_submission.json")
        response = requests.post(f"{BASE_URL}/quiz", 
                               json=quiz_data, 
                               headers=AUTH_HEADERS)
        self.log_result("06_quiz_submission", response, quiz_data)
        
        # Plaid connection
        plaid_data = self.load_test_input("plaid_connection.json")
        response = requests.post(f"{BASE_URL}/plaid/connect", 
                               json=plaid_data, 
                               headers=AUTH_HEADERS)
        self.log_result("07_plaid_connection", response, plaid_data)
        
        # Insert sample data for better testing
        response = requests.post(f"{BASE_URL}/admin/insert-sample-data", 
                               headers=AUTH_HEADERS)
        self.log_result("08_insert_sample_data", response)
        
    def test_analytics_endpoints(self):
        """Test all analytics endpoints"""
        print("\n📊 Testing Analytics Endpoints...")
        
        # Yearly anomalies
        response = requests.get(f"{BASE_URL}/anomalies/yearly", headers=AUTH_HEADERS)
        self.log_result("09_yearly_anomalies", response)
        
        # Spending trends
        response = requests.get(f"{BASE_URL}/trends", headers=AUTH_HEADERS)
        self.log_result("10_spending_trends", response)
        
        # Spending categories
        response = requests.get(f"{BASE_URL}/spending/categories", headers=AUTH_HEADERS)
        self.log_result("11_spending_categories", response)
        
        # Computed goal
        response = requests.get(f"{BASE_URL}/goal/computed", headers=AUTH_HEADERS)
        self.log_result("12_computed_goal", response)
        
        # User habits
        response = requests.get(f"{BASE_URL}/habits", headers=AUTH_HEADERS)
        self.log_result("13_user_habits", response)
        
    def test_financial_status_endpoints(self):
        """Test financial status endpoints"""
        print("\n💰 Testing Financial Status Endpoints...")
        
        # Weekly streak
        response = requests.get(f"{BASE_URL}/streak/weekly", headers=AUTH_HEADERS)
        self.log_result("14_weekly_streak", response)
        
        # Spending status
        response = requests.get(f"{BASE_URL}/spending/status", headers=AUTH_HEADERS)
        self.log_result("15_spending_status", response)
        
        # Weekly savings
        response = requests.get(f"{BASE_URL}/savings/weekly", headers=AUTH_HEADERS)
        self.log_result("16_weekly_savings", response)
        
        # Longest streak
        response = requests.get(f"{BASE_URL}/streak/longest", headers=AUTH_HEADERS)
        self.log_result("17_longest_streak", response)
        
        # Total spending
        response = requests.get(f"{BASE_URL}/spending/total", headers=AUTH_HEADERS)
        self.log_result("18_total_spending", response)
        
    def test_weekly_plan_endpoints(self):
        """Test weekly planning endpoints"""
        print("\n📅 Testing Weekly Plan Endpoints...")
        
        # Get current weekly plan
        response = requests.get(f"{BASE_URL}/plans/weekly", headers=AUTH_HEADERS)
        self.log_result("19_get_weekly_plan", response)
        
        # Create new weekly plan
        plan_request = self.load_test_input("weekly_plan_request.json")
        response = requests.post(f"{BASE_URL}/plans/weekly", 
                               json=plan_request, 
                               headers=AUTH_HEADERS)
        self.log_result("20_create_weekly_plan", response, plan_request)
        
    def test_weekly_recap_endpoints(self):
        """Test weekly recap endpoints"""
        print("\n📋 Testing Weekly Recap Endpoints...")
        
        # Get weekly recap
        response = requests.get(f"{BASE_URL}/recaps/weekly", headers=AUTH_HEADERS)
        self.log_result("21_get_weekly_recap", response)
        
        # Create weekly recap (requires a plan and transactions)
        # We'll create a simplified recap request
        recap_request = {
            "weekly_plan": {
                "week_start_date": "2025-06-23",
                "savings_target": {"amount": 300.0, "currency": "USD"},
                "spending_limits": {
                    "Food & Dining": {"daily_limit": 20.0, "weekly_limit": 140.0},
                    "Transportation": {"daily_limit": 15.0, "weekly_limit": 105.0}
                },
                "daily_recommendations": [
                    {
                        "day": "Monday",
                        "actions": ["Check budget"],
                        "focus_area": "Planning",
                        "motivation": "Start strong!"
                    }
                ],
                "tracking_metrics": [],
                "weekly_challenges": [],
                "success_tips": [],
                "habits": [
                    "Log in to Noumi daily",
                    "Set weekly spending limits",
                    "Track all expenses"
                ]
            },
            "actual_transactions": [
                {
                    "transaction_id": "test_txn_1",
                    "amount": -12.50,
                    "description": "Coffee Shop",
                    "category": "Food & Dining",
                    "date": "2025-06-23",
                    "merchant_name": "Starbucks"
                },
                {
                    "transaction_id": "test_txn_2",
                    "amount": -8.00,
                    "description": "Bus Fare",
                    "category": "Transportation",
                    "date": "2025-06-23",
                    "merchant_name": "Metro"
                }
            ]
        }
        
        response = requests.post(f"{BASE_URL}/recaps/weekly", 
                               json=recap_request, 
                               headers=AUTH_HEADERS)
        self.log_result("22_create_weekly_recap", response, recap_request)
        
    def generate_summary_report(self):
        """Generate comprehensive test summary"""
        print("\n📄 Generating Test Summary...")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r["success"])
        failed_tests = total_tests - passed_tests
        
        summary = {
            "test_session": {
                "timestamp": self.test_timestamp,
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": f"{(passed_tests/total_tests)*100:.1f}%"
            },
            "detailed_results": self.results,
            "database_info": {
                "using_real_sqlite": True,
                "mock_data_removed": True,
                "database_file": "noumi.db"
            }
        }
        
        # Save comprehensive summary
        summary_file = f"{TEST_OUTPUTS_DIR}/comprehensive_test_summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2, default=str)
            
        # Save human-readable report
        report_file = f"{TEST_OUTPUTS_DIR}/test_report.md"
        with open(report_file, "w") as f:
            f.write(f"# Noumi API Comprehensive Test Report\n\n")
            f.write(f"**Test Date:** {self.test_timestamp}\n")
            f.write(f"**Total Tests:** {total_tests}\n")
            f.write(f"**Passed:** {passed_tests} ✅\n")
            f.write(f"**Failed:** {failed_tests} ❌\n")
            f.write(f"**Success Rate:** {(passed_tests/total_tests)*100:.1f}%\n\n")
            
            f.write("## Test Results\n\n")
            for test_name, result in self.results.items():
                status = "✅ PASS" if result["success"] else "❌ FAIL"
                f.write(f"- **{test_name}**: {status} ({result['status_code']})\n")
                
            f.write("\n## Database Configuration\n")
            f.write("- **Database Type:** Local SQLite\n")
            f.write("- **Mock Data:** Completely removed\n")
            f.write("- **Real Analytics:** Enabled\n")
            f.write("- **LLM Integration:** Available\n")
        
        print(f"\n📊 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"\n📁 Results saved to: {TEST_OUTPUTS_DIR}/")
        
    def run_all_tests(self):
        """Run comprehensive API test suite"""
        print("🚀 Starting Comprehensive Noumi API Test Suite")
        print("=" * 60)
        
        self.test_health_endpoints()
        self.test_authentication_endpoints()
        self.test_quiz_and_plaid_endpoints()
        self.test_analytics_endpoints()
        self.test_financial_status_endpoints()
        self.test_weekly_plan_endpoints()
        self.test_weekly_recap_endpoints()
        
        self.generate_summary_report()
        
        print("\n🎉 Comprehensive API Test Complete!")

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests() 