# Detailed JSON Return Formats - Noumi AI Agents

## Overview

This document provides the **exact** JSON structures returned by each Noumi AI agent, with specific field names, data types, and realistic example values.

## 1. Quiz Agent - `analyze_quiz_responses()` Return Format

### Exact JSON Structure with Example Values

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

### Field Specifications

| Field | Type | Possible Values | Description |
|-------|------|-----------------|-------------|
| `user_id` | `string` | Any user identifier | Unique user identifier |
| `risk_tolerance` | `string` | `"conservative"`, `"moderate"`, `"aggressive"` | Investment risk appetite |
| `financial_knowledge` | `string` | `"beginner"`, `"intermediate"`, `"advanced"` | User's financial sophistication |
| `savings_goals.primary_goal` | `string` | `"emergency_fund"`, `"vacation"`, `"house_down_payment"`, `"retirement"`, `"debt_payoff"` | Main financial goal |
| `savings_goals.target_amount` | `number` | 1000-100000+ | Target amount in USD |
| `savings_goals.timeline` | `string` | `"1-3 months"`, `"6-12 months"`, `"1-2 years"`, etc. | Time to achieve goal |
| `spending_patterns.problem_categories` | `array[string]` | Category names | Categories where user struggles |
| `spending_patterns.strong_categories` | `array[string]` | Category names | Categories user manages well |
| `spending_patterns.spending_personality` | `string` | `"planner"`, `"impulse"`, `"balanced"` | Spending behavior type |
| `motivation_factors.primary_motivation` | `string` | `"milestones"`, `"social"`, `"gamification"`, `"education"` | What motivates the user |
| `motivation_factors.stress_level` | `number` | 1-10 | Financial stress level (10 = highest) |
| `motivation_factors.confidence_level` | `number` | 1-10 | Confidence in financial decisions |
| `preferences.tracking_method` | `string` | Free text | How user prefers to track expenses |
| `preferences.notification_frequency` | `string` | `"daily"`, `"weekly"`, `"monthly"` | Preferred notification cadence |
| `preferences.savings_frequency` | `string` | `"weekly"`, `"biweekly"`, `"monthly"` | Preferred savings frequency |
| `profile_completeness` | `number` | 0-100 | Percentage of profile completed |
| `analysis_timestamp` | `string` | ISO 8601 timestamp | When analysis was performed |

---

## 2. Plaid Transaction Agent Return Formats

### A. `analyze_spending_patterns()` Return Format

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
    },
    "Entertainment": {
      "total_amount": 156.78,
      "transaction_count": 12,
      "average_transaction": 13.07,
      "percentage_of_spending": 8.6,
      "trend": "decreasing"
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
      },
      {
        "merchant_name": "Shell",
        "total_spent": 234.56,
        "visit_frequency": 6,
        "category": "Transportation"
      }
    ],
    "merchant_loyalty_score": 72
  },
  "spending_timing": {
    "peak_spending_days": ["Friday", "Saturday"],
    "peak_spending_hours": ["12-14", "18-20"],
    "weekend_vs_weekday_ratio": 1.35
  },
  "analysis_timestamp": "2024-06-16T00:12:34.567Z"
}
```

### B. `identify_saving_opportunities()` Return Format

```json
{
  "total_potential_monthly_savings": 347.82,
  "opportunities": [
    {
      "category": "Food and Drink",
      "opportunity_type": "reduce_frequency",
      "current_monthly_spending": 642.87,
      "potential_savings": 128.57,
      "confidence_score": 85,
      "specific_recommendations": [
        "Cook at home 2 more days per week",
        "Limit coffee shop visits to 3 per week"
      ],
      "difficulty_level": "medium"
    },
    {
      "category": "Entertainment",
      "opportunity_type": "substitute",
      "current_monthly_spending": 156.78,
      "potential_savings": 62.71,
      "confidence_score": 92,
      "specific_recommendations": [
        "Use free streaming trials instead of movie tickets",
        "Find free local events"
      ],
      "difficulty_level": "easy"
    }
  ],
  "quick_wins": [
    {
      "recommendation": "Cancel unused subscription services",
      "estimated_monthly_savings": 47.98,
      "implementation_effort": "low"
    },
    {
      "recommendation": "Switch to generic brands for groceries",
      "estimated_monthly_savings": 89.45,
      "implementation_effort": "low"
    }
  ],
  "behavioral_insights": {
    "spending_triggers": ["Friday evenings", "Stressful workdays"],
    "successful_patterns": ["Meal planning on Sundays", "Using shopping lists"],
    "areas_for_improvement": ["Impulse purchases", "Weekend overspending"]
  },
  "analysis_timestamp": "2024-06-16T00:12:34.567Z"
}
```

---

## 3. Chain of Guidance Planner Return Format

### `generate_weekly_plan()` Exact JSON Structure

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
    },
    "Shopping": {
      "daily_limit": 15.00,
      "weekly_limit": 105.00
    }
  },
  "daily_recommendations": [
    {
      "day": "Monday",
      "actions": [
        "Check account balance",
        "Set weekly spending goals"
      ],
      "focus_area": "Goal Setting",
      "motivation": "Start your week strong!"
    },
    {
      "day": "Tuesday",
      "actions": [
        "Track all expenses",
        "Review yesterday's spending"
      ],
      "focus_area": "Expense Tracking",
      "motivation": "Stay on track!"
    },
    {
      "day": "Wednesday",
      "actions": [
        "Mid-week check-in",
        "Adjust spending if needed"
      ],
      "focus_area": "Progress Review",
      "motivation": "You're halfway there!"
    },
    {
      "day": "Thursday",
      "actions": [
        "Evaluate weekly progress",
        "Plan weekend budget"
      ],
      "focus_area": "Weekend Planning",
      "motivation": "Prepare for success!"
    },
    {
      "day": "Friday",
      "actions": [
        "Review week's progress",
        "Set weekend spending limits"
      ],
      "focus_area": "Week Review",
      "motivation": "Strong finish ahead!"
    },
    {
      "day": "Saturday",
      "actions": [
        "Track weekend spending",
        "Find free activities"
      ],
      "focus_area": "Weekend Management",
      "motivation": "Smart weekend choices!"
    },
    {
      "day": "Sunday",
      "actions": [
        "Calculate weekly total",
        "Plan next week"
      ],
      "focus_area": "Weekly Wrap-up",
      "motivation": "Prepare for another successful week!"
    }
  ],
  "tracking_metrics": [
    {
      "metric_name": "Weekly Savings",
      "target_value": 125.50,
      "current_value": 0
    },
    {
      "metric_name": "Days Under Budget",
      "target_value": 7,
      "current_value": 0
    }
  ],
  "weekly_challenges": [
    "Track every expense for 7 days",
    "Cook at home 5 out of 7 days",
    "Find one free entertainment activity"
  ],
  "success_tips": [
    "Review progress daily",
    "Celebrate small wins",
    "Stay consistent with tracking"
  ]
}
```

### `extract_ml_features()` Return Format

```json
{
  "suggested_savings_amount": 125.50,
  "spending_efficiency_score": 78,
  "extraction_successful": true,
  "extraction_timestamp": "2024-06-16T00:12:34.567Z"
}
```

**OR** (if extraction fails):

```json
{
  "suggested_savings_amount": null,
  "spending_efficiency_score": null,
  "extraction_successful": false,
  "extraction_timestamp": "2024-06-16T00:12:34.567Z",
  "error": "Missing ml_features in plan data"
}
```

---

## 4. Recap Agent Return Formats

### A. `generate_weekly_recap()` Exact JSON Structure

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
    },
    "Transportation": {
      "planned_limit": 84.00,
      "actual_spent": 78.90,
      "variance": -5.10,
      "adherence_rate": 0.939,
      "status": "under_budget",
      "variance_percentage": -6.07
    },
    "Shopping": {
      "planned_limit": 105.00,
      "actual_spent": 67.82,
      "variance": -37.18,
      "adherence_rate": 1.0,
      "status": "under_budget",
      "variance_percentage": -35.41
    }
  },
  "goal_achievement": {
    "metric_achievements": [
      {
        "metric_name": "Weekly Savings",
        "target_value": 125.50,
        "estimated_achievement_rate": 0.925,
        "status": "achieved"
      },
      {
        "metric_name": "Days Under Budget",
        "target_value": 7,
        "estimated_achievement_rate": 0.857,
        "status": "partial"
      }
    ],
    "challenge_count": 3,
    "overall_goal_success_rate": 0.891
  },
  "ai_insights": {
    "key_insights": [
      {
        "insight_type": "success",
        "title": "Excellent Grocery Budget Management",
        "description": "You stayed under your food budget while maintaining healthy choices",
        "impact_level": "high"
      },
      {
        "insight_type": "improvement",
        "title": "Entertainment Overspend Alert",
        "description": "Entertainment spending exceeded budget by 29%, mostly on weekend activities",
        "impact_level": "medium"
      }
    ],
    "behavioral_patterns": [
      {
        "pattern_type": "spending_timing",
        "description": "Higher spending observed on Friday and Saturday evenings",
        "recommendation": "Set weekend spending alerts"
      }
    ],
    "success_highlights": [
      "Stayed under grocery budget for entire week",
      "Successfully tracked all expenses"
    ],
    "improvement_areas": [
      {
        "area": "Entertainment spending control",
        "current_impact": "Exceeded budget by $16.50",
        "suggested_action": "Plan entertainment activities in advance with set budgets"
      }
    ],
    "overall_performance_summary": "Strong week overall with good discipline in most categories. Focus on weekend entertainment planning for continued success."
  },
  "performance_scores": {
    "overall_performance_score": 87.3,
    "spending_adherence_score": 92.5,
    "category_discipline_score": 83.2,
    "goal_achievement_score": 89.1,
    "performance_grade": "B+"
  },
  "recommendations": [
    {
      "type": "category_focus",
      "priority": "medium",
      "title": "Optimize Entertainment Spending",
      "description": "You overspent in Entertainment by $16.50 this week",
      "specific_action": "Create a weekend entertainment budget and stick to it"
    },
    {
      "type": "behavioral_change",
      "priority": "low",
      "title": "Maintain Current Food Discipline",
      "description": "Excellent performance in Food and Drink category",
      "specific_action": "Continue current meal planning strategy"
    }
  ]
}
```

### B. `get_ml_performance_features()` Return Format

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

---

## 5. Data Type Specifications

### Common Data Types Used

| Type | Format | Example | Notes |
|------|--------|---------|-------|
| `string` | UTF-8 text | `"example_text"` | Always quoted |
| `number` | Float/Integer | `123.45` or `42` | No quotes, decimals allowed |
| `boolean` | Boolean | `true` or `false` | No quotes, lowercase |
| `array[string]` | Array of strings | `["item1", "item2"]` | Square brackets |
| `array[object]` | Array of objects | `[{"key": "value"}]` | Objects in array |
| `object` | JSON object | `{"key": "value"}` | Curly braces |
| `timestamp` | ISO 8601 | `"2024-06-16T00:12:34.567Z"` | Always quoted, UTC |
| `date` | YYYY-MM-DD | `"2024-06-16"` | Always quoted |
| `currency` | USD amount | `125.50` | Number, 2 decimal places |
| `percentage` | 0-100 scale | `87.3` | Number, can have decimals |
| `rate` | 0-1 scale | `0.925` | Number, 0 = 0%, 1 = 100% |

### Enum Value Specifications

#### Risk Tolerance
- `"conservative"` - Low risk, prefers stable returns
- `"moderate"` - Balanced risk/return approach  
- `"aggressive"` - High risk, seeks maximum returns

#### Financial Knowledge
- `"beginner"` - Basic understanding of personal finance
- `"intermediate"` - Good grasp of budgeting and saving
- `"advanced"` - Sophisticated financial planning knowledge

#### Performance Grades
- `"A"` - 90-100 score (Excellent)
- `"B"` - 80-89 score (Good)  
- `"C"` - 70-79 score (Average)
- `"D"` - 60-69 score (Below Average)
- `"F"` - 0-59 score (Poor)

#### Category Status
- `"under_budget"` - Spent less than planned limit
- `"over_budget"` - Exceeded planned limit

#### Achievement Status  
- `"achieved"` - 80%+ of target met
- `"partial"` - 50-79% of target met
- `"not_achieved"` - <50% of target met

This detailed specification provides the exact JSON structures you can expect from each Noumi AI agent. 