# Noumi AI API Usage Guide

## Overview

The Noumi AI API provides REST endpoints for financial planning and performance analysis. The API accepts JSON inputs and returns structured JSON responses with ML features.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_api.txt
```

### 2. Start the API Server

```bash
python noumi_api.py
```

The server will start on `http://localhost:5000`

### 3. Test with Examples

```bash
python api_examples.py
```

---

## API Endpoints

### Health Check

**GET** `/api/health`

Check if the API is running.

```bash
curl http://localhost:5000/api/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Noumi AI API",
  "version": "1.0.0",
  "timestamp": "2024-06-16T00:12:34.567Z"
}
```

---

### Generate Weekly Plan

**POST** `/api/generate-weekly-plan`

Generate a weekly financial plan from user profile and historical transactions.

**Input JSON:**
```json
{
  "user_profile": {
    "user_id": "user_12345",
    "savings_goal": "Emergency fund",
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
```

**Response JSON:**
```json
{
  "success": true,
  "weekly_plan": {
    "week_start_date": "2024-06-17",
    "ml_features": {
      "suggested_savings_amount": 125.50,
      "spending_efficiency_score": 78
    },
    "savings_target": {
      "amount": 125.50,
      "currency": "USD"
    },
    "spending_limits": {
      "Food and Drink": {
        "daily_limit": 25.00,
        "weekly_limit": 175.00
      }
    },
    "daily_recommendations": [...],
    "tracking_metrics": [...],
    "weekly_challenges": [...],
    "success_tips": [...]
  },
  "processing_metadata": {
    "user_id": "user_12345",
    "transactions_processed": 6,
    "plan_generated_at": "2024-06-16T00:12:34.567Z",
    "ml_features_available": true
  }
}
```

**Key ML Features Extracted:**
- `ml_features.suggested_savings_amount` (USD)
- `ml_features.spending_efficiency_score` (0-100)

---

### Generate Weekly Recap

**POST** `/api/generate-weekly-recap`

Generate performance analysis from weekly plan and actual transactions.

**Input JSON:**
```json
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
```

**Response JSON:**
```json
{
  "success": true,
  "weekly_recap": {
    "recap_metadata": {
      "week_period": "2024-06-17 to 2024-06-23",
      "analysis_timestamp": "2024-06-24T00:12:34.567Z",
      "transaction_count": 5
    },
    "spending_performance": {
      "total_planned_spending": 420.00,
      "total_actual_spending": 387.45,
      "spending_adherence_rate": 0.925,
      "over_budget": false,
      "budget_variance_percentage": -7.75
    },
    "performance_scores": {
      "overall_performance_score": 87.3,
      "spending_adherence_score": 92.5,
      "performance_grade": "B+"
    },
    "ai_insights": {...},
    "recommendations": [...]
  },
  "processing_metadata": {
    "actual_transactions_processed": 5,
    "recap_generated_at": "2024-06-16T00:12:34.567Z",
    "performance_features_available": true
  }
}
```

**Key Performance ML Features:**
- `performance_scores.overall_performance_score` (0-100)
- `spending_performance.spending_adherence_rate` (0-1)
- `spending_performance.budget_variance_percentage` (+/-)

---

### Extract ML Features

**POST** `/api/extract-ml-features`

Extract ML-ready features from plan and recap responses.

**Input JSON:**
```json
{
  "weekly_plan": { /* plan object */ },
  "weekly_recap": { /* recap object (optional) */ }
}
```

**Response JSON:**
```json
{
  "success": true,
  "ml_features": {
    "planning_features": {
      "suggested_savings_amount": 125.50,
      "spending_efficiency_score": 78,
      "total_weekly_budget": 420.00,
      "savings_target": 125.50
    },
    "performance_features": {
      "overall_performance_score": 87.3,
      "spending_adherence_rate": 0.925,
      "budget_variance_percentage": -7.75,
      "categories_over_budget": 1,
      "performance_grade": "B+"
    },
    "extraction_metadata": {
      "extraction_timestamp": "2024-06-16T00:12:34.567Z",
      "planning_features_available": true,
      "performance_features_available": true
    }
  }
}
```

---

## Python Client Usage

### Installation

```python
import requests
import json

class NoumiAPIClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
    
    def generate_weekly_plan(self, user_profile, transactions):
        """Generate weekly plan via API."""
        url = f"{self.base_url}/api/generate-weekly-plan"
        payload = {
            "user_profile": user_profile,
            "transactions": transactions
        }
        response = requests.post(url, json=payload)
        return response.json() if response.status_code == 200 else None
    
    def generate_weekly_recap(self, weekly_plan, actual_transactions):
        """Generate weekly recap via API."""
        url = f"{self.base_url}/api/generate-weekly-recap"
        payload = {
            "weekly_plan": weekly_plan,
            "actual_transactions": actual_transactions
        }
        response = requests.post(url, json=payload)
        return response.json() if response.status_code == 200 else None
```

### Example Usage

```python
# Initialize client
client = NoumiAPIClient()

# 1. Generate weekly plan
user_profile = {
    "user_id": "user_12345",
    "savings_goal": "Emergency fund",
    "monthly_income": 4500.0,
    "risk_tolerance": "moderate",
    "financial_knowledge": "intermediate"
}

transactions = [
    {
        "transaction_id": "txn_001",
        "amount": -127.89,
        "description": "WHOLE FOODS MARKET",
        "category": ["Food and Drink"],
        "date": "2024-06-01"
    }
]

result = client.generate_weekly_plan(user_profile, transactions)
if result and result["success"]:
    weekly_plan = result["weekly_plan"]
    
    # Extract ML features
    ml_features = weekly_plan["ml_features"]
    suggested_savings = ml_features["suggested_savings_amount"]
    efficiency_score = ml_features["spending_efficiency_score"]
    
    print(f"Suggested savings: ${suggested_savings}")
    print(f"Efficiency score: {efficiency_score}/100")

# 2. Generate weekly recap (after user spends during the week)
actual_transactions = [
    {
        "transaction_id": "actual_001",
        "amount": -18.50,
        "description": "COFFEE SHOP",
        "category": "Food and Drink",
        "date": "2024-06-18"
    }
]

recap_result = client.generate_weekly_recap(weekly_plan, actual_transactions)
if recap_result and recap_result["success"]:
    weekly_recap = recap_result["weekly_recap"]
    
    # Extract performance metrics
    performance = weekly_recap["performance_scores"]
    overall_score = performance["overall_performance_score"]
    grade = performance["performance_grade"]
    
    print(f"Performance: {overall_score}/100 (Grade: {grade})")
```

---

## JavaScript/Node.js Usage

```javascript
const axios = require('axios');

class NoumiAPIClient {
    constructor(baseUrl = 'http://localhost:5000') {
        this.baseUrl = baseUrl;
    }
    
    async generateWeeklyPlan(userProfile, transactions) {
        try {
            const response = await axios.post(`${this.baseUrl}/api/generate-weekly-plan`, {
                user_profile: userProfile,
                transactions: transactions
            });
            return response.data;
        } catch (error) {
            console.error('Error generating weekly plan:', error);
            return null;
        }
    }
    
    async generateWeeklyRecap(weeklyPlan, actualTransactions) {
        try {
            const response = await axios.post(`${this.baseUrl}/api/generate-weekly-recap`, {
                weekly_plan: weeklyPlan,
                actual_transactions: actualTransactions
            });
            return response.data;
        } catch (error) {
            console.error('Error generating weekly recap:', error);
            return null;
        }
    }
}

// Example usage
const client = new NoumiAPIClient();

const userProfile = {
    user_id: "user_12345",
    savings_goal: "Emergency fund",
    monthly_income: 4500.0,
    risk_tolerance: "moderate",
    financial_knowledge: "intermediate"
};

const transactions = [
    {
        transaction_id: "txn_001",
        amount: -127.89,
        description: "WHOLE FOODS MARKET",
        category: ["Food and Drink"],
        date: "2024-06-01"
    }
];

// Generate weekly plan
client.generateWeeklyPlan(userProfile, transactions)
    .then(result => {
        if (result && result.success) {
            const weeklyPlan = result.weekly_plan;
            const mlFeatures = weeklyPlan.ml_features;
            
            console.log(`Suggested savings: $${mlFeatures.suggested_savings_amount}`);
            console.log(`Efficiency score: ${mlFeatures.spending_efficiency_score}/100`);
        }
    });
```

---

## cURL Examples

### Generate Weekly Plan

```bash
curl -X POST http://localhost:5000/api/generate-weekly-plan \
  -H "Content-Type: application/json" \
  -d '{
    "user_profile": {
      "user_id": "user_12345",
      "savings_goal": "Emergency fund",
      "monthly_income": 4500.0,
      "risk_tolerance": "moderate",
      "financial_knowledge": "intermediate"
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
  }'
```

### Generate Weekly Recap

```bash
curl -X POST http://localhost:5000/api/generate-weekly-recap \
  -H "Content-Type: application/json" \
  -d '{
    "weekly_plan": {
      "week_start_date": "2024-06-17",
      "ml_features": {
        "suggested_savings_amount": 125.50,
        "spending_efficiency_score": 78
      },
      "spending_limits": {
        "Food and Drink": {"weekly_limit": 175.00}
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
  }'
```

---

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Error description",
  "message": "Detailed error message",
  "success": false
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `400`: Bad Request (invalid JSON, missing fields)
- `500`: Internal Server Error

**Example Error Response:**
```json
{
  "error": "Missing 'user_profile' in request",
  "success": false
}
```

---

## ML Feature Integration

### Primary ML Features

**From Weekly Plan:**
- `suggested_savings_amount`: Target weekly savings (USD)
- `spending_efficiency_score`: Optimization score (0-100)

**From Weekly Recap:**
- `overall_performance_score`: Performance rating (0-100)
- `spending_adherence_rate`: Budget adherence (0-1)
- `budget_variance_percentage`: Over/under budget (+/-)

### Feature Extraction Pattern

```python
def extract_for_ml_pipeline(plan_response, recap_response):
    """Extract features for ML pipeline."""
    
    # Planning features
    planning_features = {
        'suggested_savings': plan_response['weekly_plan']['ml_features']['suggested_savings_amount'],
        'efficiency_score': plan_response['weekly_plan']['ml_features']['spending_efficiency_score'],
        'weekly_budget': sum(
            cat['weekly_limit'] 
            for cat in plan_response['weekly_plan']['spending_limits'].values()
        )
    }
    
    # Performance features (if recap available)
    performance_features = {}
    if recap_response:
        recap = recap_response['weekly_recap']
        performance_features = {
            'performance_score': recap['performance_scores']['overall_performance_score'],
            'adherence_rate': recap['spending_performance']['spending_adherence_rate'],
            'variance_pct': recap['spending_performance']['budget_variance_percentage'],
            'performance_grade': recap['performance_scores']['performance_grade']
        }
    
    return {
        'planning_features': planning_features,
        'performance_features': performance_features,
        'extraction_timestamp': datetime.now().isoformat()
    }
```

---

## Production Deployment

### Environment Variables

```bash
export FLASK_ENV=production
export FLASK_DEBUG=False
export PORT=5000
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements_api.txt .
RUN pip install -r requirements_api.txt

COPY . .
EXPOSE 5000

CMD ["python", "noumi_api.py"]
```

### Health Monitoring

Monitor the `/api/health` endpoint for service availability:

```bash
curl http://localhost:5000/api/health
```

---

## Testing

Run the comprehensive API test:

```bash
python api_examples.py
```

This will test all endpoints and save results to `api_demo_results_[timestamp].json`.

---

## Next Steps

1. **Start the API server**: `python noumi_api.py`
2. **Test with examples**: `python api_examples.py`
3. **Integrate into your application** using the client examples
4. **Extract ML features** for your machine learning pipeline
5. **Deploy to production** using the deployment guide

The API is now ready for production integration with your financial planning application! 🚀 