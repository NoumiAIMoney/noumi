"""
Example API Usage for Noumi AI
Demonstrates how to call the API endpoints with real JSON data.
"""

import requests
import json
from datetime import datetime


class NoumiAPIClient:
    """Client for interacting with Noumi AI API."""
    
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
    
    def generate_weekly_plan(self, user_profile, transactions):
        """Generate weekly plan via API."""
        url = f"{self.base_url}/api/generate-weekly-plan"
        payload = {
            "user_profile": user_profile,
            "transactions": transactions
        }
        
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
    
    def generate_weekly_recap(self, weekly_plan, actual_transactions):
        """Generate weekly recap via API."""
        url = f"{self.base_url}/api/generate-weekly-recap"
        payload = {
            "weekly_plan": weekly_plan,
            "actual_transactions": actual_transactions
        }
        
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
    
    def extract_ml_features(self, weekly_plan, weekly_recap=None):
        """Extract ML features via API."""
        url = f"{self.base_url}/api/extract-ml-features"
        payload = {"weekly_plan": weekly_plan}
        if weekly_recap:
            payload["weekly_recap"] = weekly_recap
            
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None


def create_sample_user_profile():
    """Create sample user profile JSON."""
    return {
        "user_id": "user_12345",
        "savings_goal": "Emergency fund",
        "monthly_income": 4500.0,
        "current_savings": "$5,000 - $15,000", 
        "savings_timeframe": "6-12 months",
        "spending_categories": [
            "Food & Dining",
            "Entertainment", 
            "Shopping",
            "Transportation",
            "Healthcare",
            "Bills & Utilities"
        ],
        "financial_stress": 7,
        "saving_difficulty": "Impulse purchases and dining out",
        "spending_tracking": "Mobile banking app",
        "risk_tolerance": "moderate",
        "financial_knowledge": "intermediate",
        "motivation_style": "Reaching specific financial milestones",
        "primary_concern": "Building emergency fund",
        "preferred_savings_frequency": "Weekly automatic transfers",
        "budget_experience": "I've tried budgeting before with mixed success",
        "spending_personality": "Planner with occasional impulse spending",
        "debt_situation": "Some credit card debt",
        "retirement_planning": "Contributing to 401k with company match",
        "family_status": "Single, no dependents",
        "housing_situation": "Renting apartment",
        "problem_categories": ["Food and Drink", "Entertainment"]
    }


def create_sample_transactions():
    """Create sample transactions JSON."""
    return [
        {
            "transaction_id": "txn_grocery_001",
            "amount": -127.89,
            "description": "WHOLE FOODS MARKET #10253",
            "merchant_name": "Whole Foods Market",
            "category": ["Food and Drink"],
            "date": "2024-06-01",
            "account_id": "acc_checking_001"
        },
        {
            "transaction_id": "txn_gas_001", 
            "amount": -58.42,
            "description": "SHELL OIL 375291847",
            "merchant_name": "Shell",
            "category": ["Transportation"],
            "date": "2024-06-01",
            "account_id": "acc_checking_001"
        },
        {
            "transaction_id": "txn_coffee_001",
            "amount": -5.75,
            "description": "STARBUCKS STORE #15829",
            "merchant_name": "Starbucks",
            "category": ["Food and Drink"],
            "date": "2024-06-02",
            "account_id": "acc_checking_001"
        },
        {
            "transaction_id": "txn_subscription_001",
            "amount": -16.99,
            "description": "NETFLIX.COM NETFLIX.COM CA",
            "merchant_name": "Netflix",
            "category": ["Entertainment"],
            "date": "2024-06-02",
            "account_id": "acc_checking_001"
        },
        {
            "transaction_id": "txn_lunch_001",
            "amount": -14.50,
            "description": "CHIPOTLE 2953",
            "merchant_name": "Chipotle Mexican Grill",
            "category": ["Food and Drink"],
            "date": "2024-06-03",
            "account_id": "acc_checking_001"
        },
        {
            "transaction_id": "txn_salary_001",
            "amount": 3500.00,
            "description": "PAYROLL DEPOSIT ACME CORP",
            "merchant_name": "ACME Corporation",
            "category": ["Payroll"],
            "date": "2024-06-01",
            "account_id": "acc_checking_001"
        }
    ]


def create_sample_actual_transactions():
    """Create sample actual transactions for recap."""
    return [
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


def demo_weekly_plan_api():
    """Demonstrate weekly plan generation API."""
    print("🎯 Testing Weekly Plan Generation API")
    print("=" * 50)
    
    # Initialize client
    client = NoumiAPIClient()
    
    # Create sample data
    user_profile = create_sample_user_profile()
    transactions = create_sample_transactions()
    
    print(f"📤 Sending request for user: {user_profile['user_id']}")
    print(f"   User profile fields: {len(user_profile)}")
    print(f"   Transactions: {len(transactions)}")
    
    # Call API
    result = client.generate_weekly_plan(user_profile, transactions)
    
    if result and result.get("success"):
        weekly_plan = result["weekly_plan"]
        metadata = result["processing_metadata"]
        
        print("✅ Weekly Plan Generated Successfully!")
        print(f"   Week start: {weekly_plan.get('week_start_date')}")
        print(f"   Transactions processed: {metadata['transactions_processed']}")
        print(f"   ML features available: {metadata['ml_features_available']}")
        
        # Extract ML features
        ml_features = weekly_plan.get("ml_features", {})
        if ml_features:
            print("🧮 ML Features Extracted:")
            print(f"   Suggested savings: ${ml_features.get('suggested_savings_amount', 0):.2f}")
            print(f"   Efficiency score: {ml_features.get('spending_efficiency_score', 0)}/100")
        
        # Show spending limits
        spending_limits = weekly_plan.get("spending_limits", {})
        print("💰 Weekly Spending Limits:")
        for category, limits in spending_limits.items():
            print(f"   {category}: ${limits.get('weekly_limit', 0):.2f}")
        
        return weekly_plan
    else:
        print("❌ Failed to generate weekly plan")
        return None


def demo_weekly_recap_api(weekly_plan):
    """Demonstrate weekly recap generation API."""
    print("\n📊 Testing Weekly Recap Generation API")
    print("=" * 50)
    
    # Initialize client
    client = NoumiAPIClient()
    
    # Create actual transactions
    actual_transactions = create_sample_actual_transactions()
    
    print(f"📤 Sending recap request")
    print(f"   Weekly plan provided: {'✅' if weekly_plan else '❌'}")
    print(f"   Actual transactions: {len(actual_transactions)}")
    
    # Call API
    result = client.generate_weekly_recap(weekly_plan, actual_transactions)
    
    if result and result.get("success"):
        weekly_recap = result["weekly_recap"]
        metadata = result["processing_metadata"]
        
        print("✅ Weekly Recap Generated Successfully!")
        print(f"   Transactions processed: {metadata['actual_transactions_processed']}")
        print(f"   Performance features available: {metadata['performance_features_available']}")
        
        # Show performance scores
        performance_scores = weekly_recap.get("performance_scores", {})
        if performance_scores:
            print("📈 Performance Scores:")
            print(f"   Overall: {performance_scores.get('overall_performance_score', 0):.1f}/100")
            print(f"   Grade: {performance_scores.get('performance_grade', 'N/A')}")
            print(f"   Adherence: {performance_scores.get('spending_adherence_score', 0):.1f}%")
        
        # Show spending performance
        spending_perf = weekly_recap.get("spending_performance", {})
        if spending_perf:
            print("💸 Spending Performance:")
            print(f"   Planned: ${spending_perf.get('total_planned_spending', 0):.2f}")
            print(f"   Actual: ${spending_perf.get('total_actual_spending', 0):.2f}")
            print(f"   Over budget: {spending_perf.get('over_budget', False)}")
        
        return weekly_recap
    else:
        print("❌ Failed to generate weekly recap")
        return None


def demo_ml_features_extraction(weekly_plan, weekly_recap):
    """Demonstrate ML features extraction API."""
    print("\n🧮 Testing ML Features Extraction API")
    print("=" * 50)
    
    # Initialize client
    client = NoumiAPIClient()
    
    print(f"📤 Extracting ML features")
    print(f"   Weekly plan provided: {'✅' if weekly_plan else '❌'}")
    print(f"   Weekly recap provided: {'✅' if weekly_recap else '❌'}")
    
    # Call API
    result = client.extract_ml_features(weekly_plan, weekly_recap)
    
    if result and result.get("success"):
        ml_features = result["ml_features"]
        metadata = ml_features["extraction_metadata"]
        
        print("✅ ML Features Extracted Successfully!")
        print(f"   Planning features available: {metadata['planning_features_available']}")
        print(f"   Performance features available: {metadata['performance_features_available']}")
        
        # Show planning features
        planning_features = ml_features.get("planning_features", {})
        print("🎯 Planning ML Features:")
        if planning_features:
            savings = planning_features.get('suggested_savings_amount')
            efficiency = planning_features.get('spending_efficiency_score')
            budget = planning_features.get('total_weekly_budget')
            
            if savings is not None:
                print(f"   Suggested savings: ${savings:.2f}")
            else:
                print("   Suggested savings: Not available")
                
            if efficiency is not None:
                print(f"   Efficiency score: {efficiency}/100")
            else:
                print("   Efficiency score: Not available")
                
            if budget is not None:
                print(f"   Total weekly budget: ${budget:.2f}")
            else:
                print("   Total weekly budget: Not available")
        else:
            print("   No planning features available")
        
        # Show performance features
        performance_features = ml_features.get("performance_features", {})
        if performance_features:
            print("📊 Performance ML Features:")
            score = performance_features.get('overall_performance_score')
            adherence = performance_features.get('spending_adherence_rate')
            variance = performance_features.get('budget_variance_percentage')
            over_budget = performance_features.get('categories_over_budget')
            
            if score is not None:
                print(f"   Performance score: {score:.1f}/100")
            else:
                print("   Performance score: Not available")
                
            if adherence is not None:
                print(f"   Adherence rate: {adherence:.3f}")
            else:
                print("   Adherence rate: Not available")
                
            if variance is not None:
                print(f"   Budget variance: {variance:.1f}%")
            else:
                print("   Budget variance: Not available")
                
            if over_budget is not None:
                print(f"   Categories over budget: {over_budget}")
            else:
                print("   Categories over budget: Not available")
        else:
            print("📊 Performance ML Features:")
            print("   No performance features available")
        
        return ml_features
    else:
        print("❌ Failed to extract ML features")
        return None


def save_results_to_file(weekly_plan, weekly_recap, ml_features):
    """Save all results to a JSON file."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"api_demo_results_{timestamp}.json"
    
    results = {
        "demo_metadata": {
            "demo_type": "api_endpoints_test",
            "demo_timestamp": datetime.now().isoformat(),
            "endpoints_tested": [
                "/api/generate-weekly-plan",
                "/api/generate-weekly-recap", 
                "/api/extract-ml-features"
            ]
        },
        "results": {
            "weekly_plan": weekly_plan,
            "weekly_recap": weekly_recap,
            "ml_features": ml_features
        },
        "integration_ready": {
            "api_endpoints_working": True,
            "ml_features_extracted": ml_features is not None,
            "complete_flow_tested": all([weekly_plan, weekly_recap, ml_features])
        }
    }
    
    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n💾 Results saved to: {filename}")
    except Exception as e:
        print(f"\n❌ Failed to save results: {e}")


def main():
    """Main demo function."""
    print("🚀 Noumi AI API Demo")
    print("=" * 60)
    print("Testing the complete API flow:")
    print("1. Generate weekly plan from user profile + transactions")
    print("2. Generate weekly recap from plan + actual transactions") 
    print("3. Extract ML features from results")
    print("=" * 60)
    
    try:
        # Test 1: Generate weekly plan
        weekly_plan = demo_weekly_plan_api()
        
        # Test 2: Generate weekly recap (if plan successful)
        weekly_recap = None
        if weekly_plan:
            weekly_recap = demo_weekly_recap_api(weekly_plan)
        
        # Test 3: Extract ML features (if we have plan)
        ml_features = None
        if weekly_plan:
            ml_features = demo_ml_features_extraction(weekly_plan, weekly_recap)
        
        # Save results
        save_results_to_file(weekly_plan, weekly_recap, ml_features)
        
        # Final summary
        print("\n🎉 API Demo Summary")
        print("=" * 30)
        print(f"✅ Weekly Plan Generated: {'Yes' if weekly_plan else 'No'}")
        print(f"✅ Weekly Recap Generated: {'Yes' if weekly_recap else 'No'}")
        print(f"✅ ML Features Extracted: {'Yes' if ml_features else 'No'}")
        
        if all([weekly_plan, weekly_recap, ml_features]):
            print("\n🚀 All API endpoints working! Ready for production integration.")
        else:
            print("\n⚠️  Some endpoints failed. Check server logs.")
            
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")


if __name__ == "__main__":
    main() 