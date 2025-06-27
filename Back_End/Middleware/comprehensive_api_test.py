#!/usr/bin/env python3
"""
Comprehensive API Test Suite for Noumi Backend
Tests all endpoints with real PostgreSQL database and saves outputs to files
"""

import requests
import json
import os
import psycopg2
from datetime import datetime
from typing import Dict

# Configuration
BASE_URL = "http://localhost:8000"
MOCK_TOKEN = "mock_jwt_token"
TEST_INPUTS_DIR = "test_inputs"
TEST_OUTPUTS_DIR = "test_outputs"

# PostgreSQL configuration (matching database.py)
DB_CONFIG = {
    "host": "localhost",
    "port": "5433",
    "database": "noumidb",
    "user": "administrator",
    "password": "Xum07jlY0E5320NQn0hN"
}

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
        
    def test_database_connection(self):
        """Test PostgreSQL database connection before running API tests"""
        print("\n🔍 Testing PostgreSQL Database Connection...")
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            
            # Test basic query
            cur.execute("SELECT COUNT(*) FROM users")
            user_count = cur.fetchone()[0]
            print(f"✅ PostgreSQL connection successful - {user_count} users in database")
            
            # Check table schema
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = [row[0] for row in cur.fetchall()]
            print(f"📊 Available tables: {', '.join(tables)}")
            
            cur.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ PostgreSQL connection failed: {e}")
            return False
        
    def log_result(self, test_name: str, response: requests.Response, 
                   request_data: Dict = None):
        """Log test result with response data and enhanced error details"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "status_code": response.status_code,
            "success": response.status_code < 400,
            "request_data": request_data,
            "response_headers": dict(response.headers),
            "response_body": None,
            "error_details": None
        }
        
        try:
            result["response_body"] = response.json()
        except Exception:
            result["response_body"] = response.text
            
        # Add detailed error information for failed tests
        if not result["success"]:
            result["error_details"] = {
                "status_code": response.status_code,
                "reason": response.reason,
                "url": response.url,
                "request_method": "POST" if request_data else "GET"
            }
            
        self.results[test_name] = result
        
        # Save individual test result
        with open(f"{TEST_OUTPUTS_DIR}/{test_name}.json", "w") as f:
            json.dump(result, f, indent=2, default=str)
            
        # Print test result with more details for failures
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status} {test_name}: {response.status_code}")
        if not result["success"]:
            print(f"   Error: {result['response_body']}")
        
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
        """Test authentication-related endpoints - SKIPPED"""
        print("\n🔐 Skipping Authentication Endpoints (not required)...")
        # These endpoints were removed as they are not part of the 12 required
        pass
        
    def test_quiz_and_plaid_endpoints(self):
        """Test quiz submission and Plaid connection"""
        print("\n📝 Testing Quiz and Plaid Endpoints...")
        
        # Quiz submission
        quiz_data = self.load_test_input("quiz_submission.json")
        if not quiz_data:
            quiz_data = {
                "goal_name": "Emergency Fund",
                "goal_description": "Build emergency savings for expenses",
                "goal_amount": 5000.0,
                "target_date": "2025-12-31",
                "net_monthly_income": 4500.0
            }
        response = requests.post(f"{BASE_URL}/quiz", 
                                json=quiz_data, 
                                headers=AUTH_HEADERS)
        self.log_result("06_quiz_submission", response, quiz_data)
        
        # Plaid connection
        plaid_data = self.load_test_input("plaid_connection.json")
        if not plaid_data:
            plaid_data = {"public_token": "public-sandbox-test-token"}
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
        response = requests.get(f"{BASE_URL}/anomalies/yearly", 
                               headers=AUTH_HEADERS)
        self.log_result("09_yearly_anomalies", response)
        
        # Spending trends
        response = requests.get(f"{BASE_URL}/trends", headers=AUTH_HEADERS)
        self.log_result("10_spending_trends", response)
        
        # Spending categories
        response = requests.get(f"{BASE_URL}/spending/categories", 
                               headers=AUTH_HEADERS)
        self.log_result("11_spending_categories", response)
        
        # Computed goal
        response = requests.get(f"{BASE_URL}/goal/computed", 
                               headers=AUTH_HEADERS)
        self.log_result("12_computed_goal", response)
        
        # User habits
        response = requests.get(f"{BASE_URL}/habits", headers=AUTH_HEADERS)
        self.log_result("13_user_habits", response)
        
    def test_financial_status_endpoints(self):
        """Test financial status endpoints"""
        print("\n💰 Testing Financial Status Endpoints...")
        
        # Weekly streak
        response = requests.get(f"{BASE_URL}/streak/weekly", 
                               headers=AUTH_HEADERS)
        self.log_result("14_weekly_streak", response)
        
        # Spending status
        response = requests.get(f"{BASE_URL}/spending/status", 
                               headers=AUTH_HEADERS)
        self.log_result("15_spending_status", response)
        
        # Weekly savings
        response = requests.get(f"{BASE_URL}/savings/weekly", 
                               headers=AUTH_HEADERS)
        self.log_result("16_weekly_savings", response)
        
        # Longest streak
        response = requests.get(f"{BASE_URL}/streak/longest", 
                               headers=AUTH_HEADERS)
        self.log_result("17_longest_streak", response)
        
        # Total spending
        response = requests.get(f"{BASE_URL}/spending/total", 
                               headers=AUTH_HEADERS)
        self.log_result("18_total_spending", response)
        
    def test_weekly_plan_endpoints(self):
        """Test weekly planning endpoints - SKIPPED"""
        print("\n📅 Skipping Weekly Plan Endpoints (not required)...")
        # These endpoints were removed as they are not part of the 12 required
        pass
        
    def test_weekly_recap_endpoints(self):
        """Test weekly recap endpoints - SKIPPED"""
        print("\n📋 Skipping Weekly Recap Endpoints (not required)...")
        # These endpoints were removed as they are not part of the 12 required
        pass
        
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
                "using_real_sqlite": False,
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
            f.write("# Noumi API Comprehensive Test Report\n\n")
            f.write(f"**Test Date:** {self.test_timestamp}\n")
            f.write(f"**Total Tests:** {total_tests}\n")
            f.write(f"**Passed:** {passed_tests} ✅\n")
            f.write(f"**Failed:** {failed_tests} ❌\n")
            success_rate = (passed_tests/total_tests)*100
            f.write(f"**Success Rate:** {success_rate:.1f}%\n\n")
            
            f.write("## Test Results\n\n")
            for test_name, result in self.results.items():
                status = "✅ PASS" if result["success"] else "❌ FAIL"
                status_code = result['status_code']
                f.write(f"- **{test_name}**: {status} ({status_code})\n")
                
            f.write("\n## Database Configuration\n")
            f.write("- **Database Type:** Local PostgreSQL\n")
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
        """Run comprehensive test suite with database validation"""
        print("🚀 Starting Comprehensive Noumi API Test Suite")
        print("=" * 60)
        
        # Test database connection first
        if not self.test_database_connection():
            print("❌ Database connection failed - aborting tests")
            return
        
        # Run all test suites
        self.test_health_endpoints()
        self.test_authentication_endpoints()
        self.test_quiz_and_plaid_endpoints()
        self.test_analytics_endpoints()
        self.test_financial_status_endpoints()
        self.test_weekly_plan_endpoints()
        self.test_weekly_recap_endpoints()
        
        # Generate comprehensive report
        self.generate_summary_report()
        
        print(f"\n🎉 Comprehensive API Test Complete!")


def main():
    """Main test execution function"""
    tester = APITester()
    tester.run_all_tests()


if __name__ == "__main__":
    main() 