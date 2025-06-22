# JSON Format Reference - Noumi AI Agents

## Quick Access Guide

### Key ML Features to Extract:
- **Planning Agent**: `ml_features.suggested_savings_amount`, `ml_features.spending_efficiency_score`
- **Recap Agent**: `performance_scores.overall_performance_score`, `spending_performance.spending_adherence_rate`
- **Quiz Agent**: `risk_tolerance`, `financial_knowledge`, `motivation_factors.stress_level`
- **Plaid Agent**: `monthly_analysis.average_monthly_spending`, `category_analysis`

---

## 1. Quiz Agent Response Format

```json
{
  "user_id": "user_12345",
  "risk_tolerance": "moderate",
  "financial_knowledge": "intermediate", 
  "savings_goals": {
    "primary_goal": "emergency_fund",
    "target_amount": 10000,
    "timeline": "6-12 months"
  },
  "spending_patterns": {
    "problem_categories": ["Food and Drink", "Entertainment"],
    "strong_categories": ["Bills & Utilities"],
    "spending_personality": "planner"
  },
  "motivation_factors": {
    "primary_motivation": "milestones",
    "stress_level": 7,
    "confidence_level": 6
  },
  "preferences": {
    "tracking_method": "Mobile banking app",
    "notification_frequency": "weekly",
    "savings_frequency": "weekly"
  },
  "profile_completeness": 85,
  "analysis_timestamp": "2024-06-16T00:12:34.567Z"
}
```

**Key Extraction Examples:**
```python
risk_level = response['risk_tolerance']  # "conservative"|"moderate"|"aggressive"
knowledge = response['financial_knowledge']  # "beginner"|"intermediate"|"advanced"
goal = response['savings_goals']['primary_goal']  # "emergency_fund"|"vacation"|etc
stress = response['motivation_factors']['stress_level']  # 1-10
```

---

## 2. Plaid Agent - Spending Analysis Response

```json
{
  "user_id": "user_12345",
  "analysis_period": {
    "start_date": "2024-05-01",
    "end_date": "2024-06-15", 
    "transaction_count": 127
  },
  "category_analysis": {
    "Food and Drink": {
      "total_amount": 642.87,
      "transaction_count": 23,
      "average_transaction": 27.95,
      "percentage_of_spending": 35.2,
      "trend": "increasing"
    },
    "Transportation": {
      "total_amount": 234.56,
      "transaction_count": 8,
      "average_transaction": 29.32,
      "percentage_of_spending": 12.8,
      "trend": "stable"
    }
  },
  "monthly_analysis": {
    "average_monthly_spending": 1825.43,
    "spending_variance": 245.67,
    "highest_month": "2024-05",
    "lowest_month": "2024-03"
  },
  "merchant_analysis": {
    "top_merchants": [
      {
        "merchant_name": "Whole Foods Market",
        "total_spent": 345.67,
        "visit_frequency": 8,
        "category": "Food and Drink"
      }
    ],
    "merchant_loyalty_score": 72
  },
  "analysis_timestamp": "2024-06-16T00:12:34.567Z"
}
```

**Key Extraction Examples:**
```python
monthly_spending = response['monthly_analysis']['average_monthly_spending']
food_spending = response['category_analysis']['Food and Drink']['total_amount']
top_merchant = response['merchant_analysis']['top_merchants'][0]['merchant_name']
```

---

## 3. Chain of Guidance Planner Response (PRIMARY ML TARGET)

```json
{
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
    },
    "Entertainment": {
      "daily_limit": 8.00,
      "weekly_limit": 56.00
    },
    "Transportation": {
      "daily_limit": 12.00,
      "weekly_limit": 84.00
    }
  },
  "daily_recommendations": [
    {
      "day": "Monday",
      "actions": ["Check account balance", "Set weekly goals"],
      "focus_area": "Goal Setting",
      "motivation": "Start your week strong!"
    }
  ],
  "tracking_metrics": [
    {
      "metric_name": "Weekly Savings",
      "target_value": 125.50,
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
```

**Key ML Feature Extraction:**
```python
# PRIMARY ML FEATURES
suggested_savings = response['ml_features']['suggested_savings_amount']  # USD amount
efficiency_score = response['ml_features']['spending_efficiency_score']  # 0-100

# Additional useful fields
savings_target = response['savings_target']['amount']
food_limit = response['spending_limits']['Food and Drink']['weekly_limit']
total_budget = sum(cat['weekly_limit'] for cat in response['spending_limits'].values())
```

---

## 4. Recap Agent Response (PERFORMANCE ML TARGET)

```json
{
  "recap_metadata": {
    "week_period": "2024-06-17 to 2024-06-23",
    "analysis_timestamp": "2024-06-24T00:12:34.567Z",
    "transaction_count": 23
  },
  "spending_performance": {
    "total_planned_spending": 420.00,
    "total_actual_spending": 387.45,
    "planned_savings_target": 125.50,
    "spending_vs_plan": -32.55,
    "spending_adherence_rate": 0.925,
    "over_budget": false,
    "budget_variance_percentage": -7.75
  },
  "category_performance": {
    "Food and Drink": {
      "planned_limit": 175.00,
      "actual_spent": 168.23,
      "variance": -6.77,
      "adherence_rate": 0.961,
      "status": "under_budget",
      "variance_percentage": -3.87
    },
    "Entertainment": {
      "planned_limit": 56.00,
      "actual_spent": 72.50,
      "variance": 16.50,
      "adherence_rate": 0.771,
      "status": "over_budget",
      "variance_percentage": 29.46
    }
  },
  "performance_scores": {
    "overall_performance_score": 87.3,
    "spending_adherence_score": 92.5,
    "category_discipline_score": 83.2,
    "goal_achievement_score": 89.1,
    "performance_grade": "B+"
  },
  "ai_insights": {
    "key_insights": [
      {
        "insight_type": "success",
        "title": "Excellent Grocery Budget Management",
        "description": "You stayed under your food budget",
        "impact_level": "high"
      }
    ],
    "success_highlights": [
      "Stayed under grocery budget for entire week"
    ],
    "improvement_areas": [
      {
        "area": "Entertainment spending control",
        "current_impact": "Exceeded budget by $16.50",
        "suggested_action": "Plan entertainment activities in advance"
      }
    ]
  },
  "recommendations": [
    {
      "type": "category_focus",
      "priority": "medium", 
      "title": "Optimize Entertainment Spending",
      "description": "You overspent in Entertainment by $16.50",
      "specific_action": "Create a weekend entertainment budget"
    }
  ]
}
```

**Key Performance ML Feature Extraction:**
```python
# PRIMARY PERFORMANCE ML FEATURES
overall_score = response['performance_scores']['overall_performance_score']  # 0-100
adherence_rate = response['spending_performance']['spending_adherence_rate']  # 0-1
variance_pct = response['spending_performance']['budget_variance_percentage']  # +/- %
performance_grade = response['performance_scores']['performance_grade']  # A,B,C,D,F

# Category performance
categories_over = sum(1 for cat in response['category_performance'].values() 
                     if cat['status'] == 'over_budget')
food_status = response['category_performance']['Food and Drink']['status']
```

---

## 5. ML Performance Features Response

**From `recap_agent.get_ml_performance_features()`:**
```json
{
  "features_available": true,
  "overall_performance_score": 87.3,
  "spending_adherence_rate": 0.925,
  "budget_variance_percentage": -7.75,
  "categories_over_budget": 1,
  "average_category_adherence": 0.918,
  "extraction_timestamp": "2024-06-24T00:12:34.567Z"
}
```

**Direct ML Feature Extraction:**
```python
# Use this for ML pipeline
ml_features = recap_agent.get_ml_performance_features()
if ml_features['features_available']:
    performance_score = ml_features['overall_performance_score']
    adherence_rate = ml_features['spending_adherence_rate'] 
    variance = ml_features['budget_variance_percentage']
    over_budget_count = ml_features['categories_over_budget']
```

---

## 6. Complete ML Pipeline Example

```python
def extract_ml_pipeline_features(quiz_resp, plaid_resp, planning_resp, recap_resp):
    """Extract all ML features for your pipeline."""
    
    # User profile features
    user_features = {
        'risk_tolerance': quiz_resp['risk_tolerance'],
        'financial_knowledge': quiz_resp['financial_knowledge'],
        'stress_level': quiz_resp['motivation_factors']['stress_level'],
        'profile_completeness': quiz_resp['profile_completeness']
    }
    
    # Spending pattern features  
    spending_features = {
        'monthly_spending': plaid_resp['monthly_analysis']['average_monthly_spending'],
        'spending_variance': plaid_resp['monthly_analysis']['spending_variance'],
        'top_category_amount': max(
            cat['total_amount'] for cat in plaid_resp['category_analysis'].values()
        ),
        'category_count': len(plaid_resp['category_analysis'])
    }
    
    # Planning features (PRIMARY ML TARGETS)
    planning_features = {
        'suggested_savings_amount': planning_resp['ml_features']['suggested_savings_amount'],
        'spending_efficiency_score': planning_resp['ml_features']['spending_efficiency_score'],
        'total_weekly_budget': sum(
            cat['weekly_limit'] for cat in planning_resp['spending_limits'].values()
        )
    }
    
    # Performance features (PRIMARY ML TARGETS)
    performance_features = {
        'overall_performance_score': recap_resp['performance_scores']['overall_performance_score'],
        'spending_adherence_rate': recap_resp['spending_performance']['spending_adherence_rate'],
        'budget_variance_percentage': recap_resp['spending_performance']['budget_variance_percentage'],
        'categories_over_budget': sum(
            1 for cat in recap_resp['category_performance'].values()
            if cat['status'] == 'over_budget'
        ),
        'performance_grade': recap_resp['performance_scores']['performance_grade']
    }
    
    return {
        'user_features': user_features,
        'spending_features': spending_features, 
        'planning_features': planning_features,
        'performance_features': performance_features,
        'extraction_timestamp': datetime.now().isoformat()
    }
```

---

## Field Value Specifications

| Field | Type | Values | Range |
|-------|------|--------|-------|
| `risk_tolerance` | string | "conservative", "moderate", "aggressive" | - |
| `financial_knowledge` | string | "beginner", "intermediate", "advanced" | - |
| `stress_level` | number | Integer | 1-10 |
| `suggested_savings_amount` | number | Float USD | 0+ |
| `spending_efficiency_score` | number | Integer | 0-100 |
| `overall_performance_score` | number | Float | 0-100 |
| `spending_adherence_rate` | number | Float | 0-1 |
| `budget_variance_percentage` | number | Float | Any (+over, -under) |
| `performance_grade` | string | "A", "B", "C", "D", "F" | - |
| `status` | string | "under_budget", "over_budget" | - |

This reference provides the exact JSON structures and extraction patterns for integrating Noumi AI agents into your ML pipeline. 