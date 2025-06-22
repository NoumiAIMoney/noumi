"""
Noumi FastAPI Backend - Main Application
Personalized weekly planning app with LLM and ML integration
Built according to OpenAPI specification
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
import random
import sys
import os

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Noumi API",
    description="Personalized weekly planning app with LLM and ML integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Mock token for testing - in production, use proper JWT validation
MOCK_TOKEN = "mock_jwt_token"

# Import LLM agents
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'noumi'))

try:
    from noumi_agents.planning_agent.chain_of_guidance_planner import (
        ChainOfGuidancePlanningAgent
    )
    from noumi_agents.planning_agent.recap_agent import RecapAgent
    from noumi_agents.utils.llm_client import NoumiLLMClient
    LLM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: LLM agents not available: {e}")
    LLM_AVAILABLE = False

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate token and return current user - mock implementation for testing"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # For testing purposes, accept the mock token
    if credentials.credentials != MOCK_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Return mock user data
    return {
        "id": "user_123",
        "email": "user@example.com",
        "name": "Mock User"
    }


# Pydantic Models for OpenAPI Specification


class QuizSubmission(BaseModel):
    goal_name: str
    goal_description: str
    goal_amount: float
    target_date: date
    net_monthly_income: float


class PlaidConnection(BaseModel):
    public_token: str


class User(BaseModel):
    id: Optional[str] = None
    email: str
    name: str
    created_at: Optional[datetime] = None
    preferences: Optional[Dict[str, Any]] = None


class UserCreate(BaseModel):
    email: str
    password: str
    name: str


class UserLogin(BaseModel):
    email: str
    password: str


class SpendingCategory(BaseModel):
    category_name: str
    amount: float


class SpendingTrend(BaseModel):
    icon: str
    trend: str


class ComputedGoal(BaseModel):
    goal_name: str
    target_date: date
    goal_amount: float
    amount_saved: float


class UserHabit(BaseModel):
    habit_description: str
    occurrences: int


class SpendingStatus(BaseModel):
    income: float
    expenses: float
    amount_safe_to_spend: float


class WeeklySavings(BaseModel):
    actual_savings: float
    suggested_savings_amount_weekly: float


class LongestStreak(BaseModel):
    longest_streak: int


class TotalSpent(BaseModel):
    spent_so_far: float


class AnomalyData(BaseModel):
    anomalies: List[int]


# Weekly Plan and Recap Models


class DailyRecommendation(BaseModel):
    day: str
    actions: List[str]
    focus_area: str
    motivation: str


class WeeklyPlan(BaseModel):
    week_start_date: str
    savings_target: Dict[str, Any]
    spending_limits: Dict[str, Dict[str, float]]
    daily_recommendations: List[DailyRecommendation]
    tracking_metrics: List[Dict[str, Any]]
    weekly_challenges: List[str]
    success_tips: List[str]
    ml_features: Optional[Dict[str, Any]] = None


class WeeklyPlanRequest(BaseModel):
    user_preferences: Optional[Dict[str, Any]] = None
    spending_analysis: Optional[Dict[str, Any]] = None
    force_regenerate: Optional[bool] = False


class PerformanceScore(BaseModel):
    overall_performance_score: float
    spending_adherence_score: float
    category_discipline_score: float
    goal_achievement_score: float
    performance_grade: str


class WeeklyRecap(BaseModel):
    recap_metadata: Dict[str, Any]
    spending_performance: Dict[str, Any]
    category_performance: Dict[str, Any]
    goal_achievement: Dict[str, Any]
    ai_insights: Dict[str, Any]
    performance_scores: PerformanceScore
    recommendations: List[Dict[str, Any]]
    # Enhanced fields
    detailed_category_analysis: Optional[Dict[str, Any]] = None
    streak_analysis: Optional[Dict[str, Any]] = None
    next_week_recommendations: Optional[List[str]] = None


class WeeklyRecapRequest(BaseModel):
    weekly_plan: WeeklyPlan
    actual_transactions: List[Dict[str, Any]]


# Root endpoint


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Welcome to Noumi API",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


# Health check


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "noumi-api"
    }


# Authentication endpoints


@app.post("/auth/register", response_model=Dict[str, Any])
async def register_user(user_data: UserCreate):
    """Register a new user"""
    # TODO: Implement actual user registration logic
    # For now, return a mock response
    return {
        "message": "User registered successfully",
        "user": {
            "id": "user_123",
            "email": user_data.email,
            "name": user_data.name
        },
        "token": MOCK_TOKEN
    }


@app.post("/auth/login", response_model=Dict[str, Any])
async def login_user(login_data: UserLogin):
    """Login user"""
    # TODO: Implement actual authentication logic
    # For now, return a mock response
    return {
        "message": "Login successful",
        "user": {
            "id": "user_123",
            "email": login_data.email,
            "name": "Mock User"
        },
        "token": MOCK_TOKEN
    }


@app.get("/auth/me", response_model=User)
async def get_current_user_info(current_user=Depends(get_current_user)):
    """Get current user information"""
    return User(
        id=current_user["id"],
        email=current_user["email"],
        name=current_user["name"],
        created_at=datetime.now(),
        preferences={"theme": "light", "currency": "USD"}
    )


# OpenAPI Specification Endpoints


@app.post("/quiz")
async def submit_quiz_data(
    quiz_data: QuizSubmission,
    current_user=Depends(get_current_user)
):
    """Submit quiz data - stores user's financial goals and income information"""
    # TODO: Save to database
    # For now, simulate successful storage
    
    # Validate data
    if quiz_data.goal_amount <= 0:
        raise HTTPException(status_code=400, detail="Goal amount must be positive")
    
    if quiz_data.net_monthly_income <= 0:
        raise HTTPException(status_code=400, detail="Monthly income must be positive")
    
    # Simulate saving to database
    stored_data = {
        "user_id": current_user["id"],
        "goal_name": quiz_data.goal_name,
        "goal_description": quiz_data.goal_description,
        "goal_amount": quiz_data.goal_amount,
        "target_date": quiz_data.target_date.isoformat(),
        "net_monthly_income": quiz_data.net_monthly_income,
        "created_at": datetime.now().isoformat()
    }
    
    return {"message": "Quiz data accepted", "data": stored_data}


@app.post("/plaid/connect")
async def initiate_plaid_connection(
    plaid_data: PlaidConnection,
    current_user=Depends(get_current_user)
):
    """Initiate Plaid connection and fetch account/transaction data"""
    # TODO: Implement actual Plaid integration
    # This would typically:
    # 1. Exchange public_token for access_token
    # 2. Fetch accounts data
    # 3. Fetch transactions data
    # 4. Store in database
    
    # Simulate Plaid connection and data fetching
    mock_accounts = [
        {
            "account_id": "acc_1",
            "name": "Checking Account",
            "type": "depository",
            "subtype": "checking",
            "balance": 2500.75
        },
        {
            "account_id": "acc_2", 
            "name": "Savings Account",
            "type": "depository",
            "subtype": "savings",
            "balance": 15000.00
        }
    ]
    
    mock_transactions = [
        {
            "transaction_id": "txn_1",
            "account_id": "acc_1",
            "amount": 12.50,
            "date": "2024-01-15",
            "name": "Starbucks Coffee",
            "category": ["Food and Drink", "Coffee Shops"],
            "merchant_name": "Starbucks"
        },
        {
            "transaction_id": "txn_2",
            "account_id": "acc_1", 
            "amount": 85.00,
            "date": "2024-01-14",
            "name": "Shell Gas Station",
            "category": ["Transportation", "Gas Stations"],
            "merchant_name": "Shell"
        }
    ]
    
    return {
        "message": "Plaid connection established and data fetched",
        "accounts": mock_accounts,
        "transactions": mock_transactions
    }


@app.get("/anomalies/yearly", response_model=AnomalyData)
async def get_yearly_anomaly_counts(current_user=Depends(get_current_user)):
    """Get yearly anomaly counts - anomalies per month for current year"""
    # TODO: Implement actual LLM anomaly detection
    # For now, return mock data representing anomalies per month
    
    # Generate realistic anomaly data (0-4 anomalies per month)
    anomalies = [random.randint(0, 4) for _ in range(12)]
    
    return AnomalyData(anomalies=anomalies)


@app.get("/trends", response_model=List[SpendingTrend])
async def get_spending_trends(current_user=Depends(get_current_user)):
    """Get spending trends from prompt engineering/LLM analysis"""
    # TODO: Implement actual LLM trend analysis
    # For now, return mock trends with icons
    
    mock_trends = [
        SpendingTrend(
            icon="📈",
            trend="Your coffee spending increased by 25% this month"
        ),
        SpendingTrend(
            icon="🍕",
            trend="You're spending 40% more on food delivery than average"
        ),
        SpendingTrend(
            icon="⛽",
            trend="Gas expenses are 15% lower due to remote work"
        ),
        SpendingTrend(
            icon="🛒",
            trend="Grocery shopping shows consistent weekly patterns"
        ),
        SpendingTrend(
            icon="💳",
            trend="Credit card usage decreased by 30% this quarter"
        )
    ]
    
    return mock_trends


@app.get("/spending/categories", response_model=List[SpendingCategory])
async def get_spending_categories(current_user=Depends(get_current_user)):
    """Get spending categories - breakdown by category with amounts"""
    # TODO: Implement actual transaction categorization from database
    # This should group transactions by MCC codes or categories
    
    mock_categories = [
        SpendingCategory(category_name="Food & Dining", amount=450.25),
        SpendingCategory(category_name="Transportation", amount=200.00),
        SpendingCategory(category_name="Entertainment", amount=150.50),
        SpendingCategory(category_name="Utilities", amount=300.00),
        SpendingCategory(category_name="Shopping", amount=275.75),
        SpendingCategory(category_name="Healthcare", amount=125.00),
        SpendingCategory(category_name="Education", amount=89.99)
    ]
    
    return mock_categories


@app.get("/goal/computed", response_model=ComputedGoal)
async def get_computed_goal_data(current_user=Depends(get_current_user)):
    """Get computed goal data from quiz responses stored in database"""
    # TODO: Fetch actual data from database
    # This should retrieve the quiz data and compute amount_saved
    # amount_saved = net_monthly_income - amount_spent_so_far
    
    # Mock computation based on stored quiz data
    mock_monthly_income = 5000.00
    mock_spent_this_month = 1850.50
    amount_saved = mock_monthly_income - mock_spent_this_month
    
    return ComputedGoal(
        goal_name="Emergency Fund",
        target_date=date(2024, 12, 31),
        goal_amount=10000.00,
        amount_saved=amount_saved
    )


@app.get("/habits", response_model=List[UserHabit])
async def get_user_habits(current_user=Depends(get_current_user)):
    """Get user habits from prompt engineering/LLM suggestions"""
    # TODO: Implement actual LLM habit suggestions
    # For now, return mock habit suggestions with occurrences
    
    mock_habits = [
        UserHabit(
            habit_description="Reduce eating out to save money",
            occurrences=2  # twice a week
        ),
        UserHabit(
            habit_description="Set up automatic savings transfer",
            occurrences=1  # once a month
        ),
        UserHabit(
            habit_description="Review and cancel unused subscriptions",
            occurrences=1  # once a month
        ),
        UserHabit(
            habit_description="Use grocery list to avoid impulse purchases",
            occurrences=4  # every grocery trip
        ),
        UserHabit(
            habit_description="Check account balances weekly",
            occurrences=1  # once a week
        )
    ]
    
    return mock_habits


@app.get("/streak/weekly", response_model=List[int])
async def get_weekly_streak(current_user=Depends(get_current_user)):
    """Get weekly streak of no anomalies (current week)"""
    # TODO: Implement actual anomaly detection for current week
    # Array represents each day: [Mon, Tue, Wed, Thu, Fri, Sat, Sun]
    # 1 = no anomalies, 0 = anomalies detected
    
    # Mock weekly streak data
    weekly_streak = [1, 1, 0, 1, 1, 1, 0]  # 5 out of 7 days with no anomalies
    
    return weekly_streak


@app.get("/spending/status", response_model=SpendingStatus)
async def get_spending_status(current_user=Depends(get_current_user)):
    """Get current financial status for home screen"""
    # TODO: Implement actual calculation from quiz data and transactions
    # income comes from quiz (monthly), expenses from transactions
    
    # Mock financial status calculation
    monthly_income = 5000.00
    monthly_expenses = 1850.50
    safe_to_spend = monthly_income - monthly_expenses - 500.00  # buffer
    
    return SpendingStatus(
        income=monthly_income,
        expenses=monthly_expenses,
        amount_safe_to_spend=max(0, safe_to_spend)
    )


@app.get("/savings/weekly", response_model=WeeklySavings)
async def get_weekly_savings_data(current_user=Depends(get_current_user)):
    """Get weekly savings data - compares current vs previous week"""
    # TODO: Implement actual calculation from transaction data
    # actual_savings = previous_week_expenses - current_week_expenses
    
    # Calculate actual savings based on transaction data
    previous_week_expenses = 425.75
    current_week_expenses = 380.50
    actual_savings = previous_week_expenses - current_week_expenses
    
    # Get suggested savings from LLM-generated weekly plan
    try:
        # Use same logic as get_weekly_plan to get LLM suggestions
        user_prefs = {
            "risk_tolerance": "moderate",
            "savings_goals": {
                "primary_goal": "Emergency fund",
                "timeframe_months": 6,
                "current_savings_level": "$5,000 - $15,000"
            },
            "spending_priorities": ["Food & Dining", "Transportation", 
                                  "Entertainment", "Shopping"]
        }
        
        spending_data = {
            "monthly_analysis": {"average_monthly_spending": 2500.0},
            "category_analysis": {
                "Food & Dining": {"total_amount": 400.0, "percentage": 25.0},
                "Transportation": {"total_amount": 200.0, "percentage": 12.5},
                "Entertainment": {"total_amount": 300.0, "percentage": 18.75}
            }
        }
        
        # Generate weekly plan to get ML features
        plan_data = _generate_llm_weekly_plan(user_prefs, spending_data)
        
        # Extract suggested savings from ML features
        ml_features = plan_data.get("ml_features", {})
        suggested_weekly_savings = ml_features.get("suggested_savings_amount", 125.00)
        
    except Exception as e:
        print(f"Error getting LLM savings suggestion: {e}")
        suggested_weekly_savings = 125.00  # Fallback
    
    return WeeklySavings(
        actual_savings=actual_savings,
        suggested_savings_amount_weekly=suggested_weekly_savings
    )


@app.get("/streak/longest", response_model=LongestStreak)
async def get_longest_no_anomaly_streak(current_user=Depends(get_current_user)):
    """Get longest consecutive days with no anomalies for current year"""
    # TODO: Implement actual calculation from anomaly detection data
    # This should analyze all days in the current year and find the longest
    # consecutive period without anomalies
    
    # Mock calculation - simulate finding longest streak
    longest_streak = 23  # 23 consecutive days without anomalies
    
    return LongestStreak(longest_streak=longest_streak)


@app.get("/spending/total", response_model=TotalSpent)
async def get_total_amount_spent(current_user=Depends(get_current_user)):
    """Get total amount spent so far this year"""
    # TODO: Implement actual calculation from transaction data
    # Sum all expenses from January 1st to current date
    
    # Mock calculation for year-to-date spending
    ytd_spending = 15750.25  # Total spent from Jan 1 to current date
    
    return TotalSpent(spent_so_far=ytd_spending)


# Weekly Plan and Recap Endpoints


def _generate_mock_weekly_plan() -> Dict[str, Any]:
    """Generate mock weekly plan for testing purposes."""
    return {
        "week_start_date": datetime.now().strftime("%Y-%m-%d"),
        "savings_target": {
            "amount": 200.00,
            "currency": "USD"
        },
        "spending_limits": {
            "Food & Dining": {"daily_limit": 15.0, "weekly_limit": 105.0},
            "Transportation": {"daily_limit": 8.0, "weekly_limit": 56.0},
            "Entertainment": {"daily_limit": 10.0, "weekly_limit": 70.0},
            "Shopping": {"daily_limit": 12.0, "weekly_limit": 84.0}
        },
        "daily_recommendations": [
            {
                "day": "Monday",
                "actions": ["Check account balance", "Set weekly goals"],
                "focus_area": "Goal Setting",
                "motivation": "Start your week strong!"
            },
            {
                "day": "Tuesday", 
                "actions": ["Track expenses", "Review spending limits"],
                "focus_area": "Expense Tracking",
                "motivation": "Stay on track!"
            },
            {
                "day": "Wednesday",
                "actions": ["Mid-week check-in", "Adjust if needed"],
                "focus_area": "Progress Review", 
                "motivation": "You're halfway there!"
            },
            {
                "day": "Thursday",
                "actions": ["Evaluate spending", "Plan weekend budget"],
                "focus_area": "Weekend Planning",
                "motivation": "Prepare for success!"
            },
            {
                "day": "Friday",
                "actions": ["Review week's progress", "Set weekend limits"],
                "focus_area": "Week Review",
                "motivation": "Strong finish ahead!"
            },
            {
                "day": "Saturday",
                "actions": ["Track weekend spending", "Find free activities"],
                "focus_area": "Weekend Management",
                "motivation": "Smart weekend choices!"
            },
            {
                "day": "Sunday",
                "actions": ["Calculate weekly total", "Plan next week"],
                "focus_area": "Weekly Wrap-up",
                "motivation": "Prepare for another successful week!"
            }
        ],
        "tracking_metrics": [
            {
                "metric_name": "Weekly Savings",
                "target_value": 200,
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
        ],
        "ml_features": {
            "suggested_savings_amount": 200.0,
            "spending_efficiency_score": 85.0
        }
    }


def _generate_llm_weekly_plan(user_prefs: Dict, spending_data: Dict) -> Dict:
    """Generate weekly plan using LLM agents."""
    if not LLM_AVAILABLE:
        return _generate_mock_weekly_plan()
    
    try:
        # Initialize the Chain of Guidance planner
        planner = ChainOfGuidancePlanningAgent(
            user_preferences=user_prefs,
            spending_analysis=spending_data,
            llm_client=NoumiLLMClient(provider="google")
        )
        
        # Generate the plan
        weekly_plan = planner.generate_weekly_plan()
        return weekly_plan
        
    except Exception as e:
        print(f"Error generating LLM plan: {e}")
        return _generate_mock_weekly_plan()


@app.get("/plans/weekly", response_model=WeeklyPlan)
async def get_weekly_plan(current_user=Depends(get_current_user)):
    """Get current weekly plan for the user"""
    # TODO: Fetch from database if exists
    # For now, generate using LLM or return mock data
    
    # Mock user preferences and spending data
    user_prefs = {
        "risk_tolerance": "moderate",
        "savings_goals": {
            "primary_goal": "Emergency fund",
            "timeframe_months": 6,
            "current_savings_level": "$5,000 - $15,000"
        },
        "spending_priorities": ["Food & Dining", "Transportation", 
                              "Entertainment", "Shopping"]
    }
    
    spending_data = {
        "monthly_analysis": {"average_monthly_spending": 2500.0},
        "category_analysis": {
            "Food & Dining": {"total_amount": 400.0, "percentage": 25.0},
            "Transportation": {"total_amount": 200.0, "percentage": 12.5},
            "Entertainment": {"total_amount": 300.0, "percentage": 18.75}
        }
    }
    
    plan_data = _generate_llm_weekly_plan(user_prefs, spending_data)
    return WeeklyPlan(**plan_data)


@app.post("/plans/weekly", response_model=WeeklyPlan)
async def create_weekly_plan(
    request: WeeklyPlanRequest,
    current_user=Depends(get_current_user)
):
    """Generate a new weekly plan based on user preferences and spending"""
    
    # Use provided data or defaults
    user_prefs = request.user_preferences or {
        "risk_tolerance": "moderate",
        "savings_goals": {"primary_goal": "Emergency fund"}
    }
    
    spending_data = request.spending_analysis or {
        "monthly_analysis": {"average_monthly_spending": 2500.0}
    }
    
    # Generate new plan using LLM
    plan_data = _generate_llm_weekly_plan(user_prefs, spending_data)
    
    # TODO: Save to database
    return WeeklyPlan(**plan_data)


def _get_user_spending_data(user_id: str) -> Dict[str, Any]:
    """Get user's spending data from database/storage"""
    # TODO: Replace with actual database query
    # This would fetch spending analysis from stored Plaid data
    return {
        "monthly_analysis": {"average_monthly_spending": 2500.0},
        "category_analysis": {
            "Food & Dining": {"total_amount": 400.0, "percentage": 25.0},
            "Transportation": {"total_amount": 200.0, "percentage": 12.5},
            "Entertainment": {"total_amount": 300.0, "percentage": 18.75},
            "Shopping": {"total_amount": 275.0, "percentage": 16.25}
        },
        "recent_transactions": [
            {
                "transaction_id": "txn_real_1",
                "amount": -89.50,
                "description": "Whole Foods Market",
                "category": "Food & Dining",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "merchant_name": "Whole Foods"
            },
            {
                "transaction_id": "txn_real_2",
                "amount": -45.00,
                "description": "Shell Gas Station",
                "category": "Transportation",
                "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "merchant_name": "Shell"
            },
            {
                "transaction_id": "txn_real_3",
                "amount": -25.00,
                "description": "Netflix Subscription",
                "category": "Entertainment",
                "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                "merchant_name": "Netflix"
            }
        ]
    }


def _get_user_preferences(user_id: str) -> Dict[str, Any]:
    """Get user preferences from database/storage"""
    # TODO: Replace with actual database query
    # This would fetch user preferences from quiz data
    return {
        "risk_tolerance": "moderate",
        "savings_goals": {
            "primary_goal": "Emergency fund",
            "timeframe_months": 6,
            "current_savings_level": "$5,000 - $15,000",
            "target_amount": 10000.0
        },
        "spending_priorities": ["Food & Dining", "Transportation", 
                              "Entertainment", "Shopping"],
        "financial_knowledge": "intermediate",
        "motivation_style": "milestone_focused"
    }


def _get_current_weekly_plan(user_id: str) -> Dict[str, Any]:
    """Get user's current weekly plan from database/storage"""
    # TODO: Replace with actual database query
    # For now, generate a plan based on user data
    user_prefs = _get_user_preferences(user_id)
    spending_data = _get_user_spending_data(user_id)
    
    return _generate_llm_weekly_plan(user_prefs, spending_data)


def _get_week_transactions(user_id: str, week_start: str = None) -> List[Dict]:
    """Get user's transactions for a specific week"""
    # TODO: Replace with actual database query
    # This would fetch transactions from Plaid data for the specific week
    
    if week_start is None:
        # Get current week transactions
        week_start = datetime.now().strftime("%Y-%m-%d")
    
    # Mock realistic transaction data for the week
    return [
        {
            "transaction_id": "week_txn_1",
            "amount": -67.43,
            "description": "Safeway Grocery Store",
            "category": "Food & Dining",
            "date": week_start,
            "merchant_name": "Safeway",
            "account_id": "acc_checking_001"
        },
        {
            "transaction_id": "week_txn_2",
            "amount": -58.42,
            "description": "Shell Gas Station",
            "category": "Transportation", 
            "date": (datetime.strptime(week_start, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d"),
            "merchant_name": "Shell",
            "account_id": "acc_checking_001"
        },
        {
            "transaction_id": "week_txn_3",
            "amount": -32.75,
            "description": "Starbucks Coffee",
            "category": "Food & Dining",
            "date": (datetime.strptime(week_start, "%Y-%m-%d") + timedelta(days=2)).strftime("%Y-%m-%d"),
            "merchant_name": "Starbucks",
            "account_id": "acc_checking_001"
        },
        {
            "transaction_id": "week_txn_4",
            "amount": -15.99,
            "description": "Netflix Subscription",
            "category": "Entertainment",
            "date": (datetime.strptime(week_start, "%Y-%m-%d") + timedelta(days=3)).strftime("%Y-%m-%d"),
            "merchant_name": "Netflix",
            "account_id": "acc_checking_001"
        },
        {
            "transaction_id": "week_txn_5",
            "amount": -89.99,
            "description": "Amazon Purchase",
            "category": "Shopping",
            "date": (datetime.strptime(week_start, "%Y-%m-%d") + timedelta(days=4)).strftime("%Y-%m-%d"),
            "merchant_name": "Amazon",
            "account_id": "acc_checking_001"
        }
    ]


@app.get("/recaps/weekly", response_model=WeeklyRecap)
async def get_weekly_recap(
    week_start: Optional[str] = None,
    current_user=Depends(get_current_user)
):
    """Get the most recent weekly recap for the user"""
    user_id = current_user["id"]
    
    try:
        # Get the user's current weekly plan (or from specified week)
        current_plan = _get_current_weekly_plan(user_id)
        
        # Get actual transactions for the week
        week_transactions = _get_week_transactions(user_id, week_start)
        
        # Generate comprehensive recap using LLM
        recap_data = _generate_llm_weekly_recap(current_plan, week_transactions)
        
        # Enhance with additional computed metrics
        recap_data = _enhance_recap_with_metrics(recap_data, current_plan, week_transactions)
        
        return WeeklyRecap(**recap_data)
        
    except Exception as e:
        print(f"Error generating weekly recap: {e}")
        # Fallback to mock data
        mock_plan = _generate_mock_weekly_plan()
        mock_transactions = [
            {
                "transaction_id": "fallback_txn_1",
                "amount": -45.50,
                "description": "Grocery Store",
                "category": "Food & Dining",
                "date": datetime.now().strftime("%Y-%m-%d")
            }
        ]
        recap_data = _generate_llm_weekly_recap(mock_plan, mock_transactions)
        return WeeklyRecap(**recap_data)


def _enhance_recap_with_metrics(
    recap_data: Dict, 
    plan: Dict, 
    transactions: List
) -> Dict:
    """Enhance the LLM-generated recap with additional computed metrics"""
    
    # Calculate additional performance metrics
    total_spent = sum(abs(t.get("amount", 0)) for t in transactions if t.get("amount", 0) < 0)
    planned_total = sum(
        limit.get("weekly_limit", 0) 
        for limit in plan.get("spending_limits", {}).values()
    )
    
    # Add enhanced metadata
    recap_data["recap_metadata"]["total_transactions"] = len(transactions)
    recap_data["recap_metadata"]["total_spent"] = total_spent
    recap_data["recap_metadata"]["planned_budget"] = planned_total
    recap_data["recap_metadata"]["savings_achieved"] = max(0, planned_total - total_spent)
    
    # Add category breakdown with merchant details
    category_details = {}
    for transaction in transactions:
        if transaction.get("amount", 0) < 0:  # Only spending transactions
            category = transaction.get("category", "Other")
            amount = abs(transaction.get("amount", 0))
            merchant = transaction.get("merchant_name", "Unknown")
            
            if category not in category_details:
                category_details[category] = {
                    "total_spent": 0,
                    "transaction_count": 0,
                    "merchants": {}
                }
            
            category_details[category]["total_spent"] += amount
            category_details[category]["transaction_count"] += 1
            
            if merchant not in category_details[category]["merchants"]:
                category_details[category]["merchants"][merchant] = 0
            category_details[category]["merchants"][merchant] += amount
    
    recap_data["detailed_category_analysis"] = category_details
    
    # Add streak calculation (mock for now)
    recap_data["streak_analysis"] = {
        "current_no_overspend_streak": 5,
        "longest_streak_this_month": 12,
        "streak_broken_categories": []
    }
    
    # Add next week recommendations based on performance
    if recap_data.get("performance_scores", {}).get("overall_performance_score", 0) >= 80:
        next_week_recommendations = [
            "Continue current spending patterns - you're doing great!",
            "Consider increasing savings target by 10%",
            "Look for opportunities to optimize high-performing categories"
        ]
    else:
        next_week_recommendations = [
            "Focus on the categories where you overspent",
            "Set daily spending reminders",
            "Review and adjust weekly limits"
        ]
    
    recap_data["next_week_recommendations"] = next_week_recommendations
    
    return recap_data


@app.post("/recaps/weekly", response_model=WeeklyRecap)
async def create_weekly_recap(
    request: WeeklyRecapRequest,
    current_user=Depends(get_current_user)
):
    """Generate a weekly recap based on plan and actual transactions"""
    
    try:
        plan_dict = request.weekly_plan.dict()
        transactions = request.actual_transactions
        
        # Generate recap using LLM
        recap_data = _generate_llm_weekly_recap(plan_dict, transactions)
        
        # Enhance with additional metrics
        recap_data = _enhance_recap_with_metrics(recap_data, plan_dict, transactions)
        
        # TODO: Save to database with user_id and timestamp
        user_id = current_user["id"]
        # save_weekly_recap_to_db(user_id, recap_data)
        
        return WeeklyRecap(**recap_data)
        
    except Exception as e:
        print(f"Error creating weekly recap: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate weekly recap")


def _generate_mock_weekly_recap(plan: Dict, transactions: List) -> Dict:
    """Generate mock weekly recap for testing purposes."""
    return {
        "recap_metadata": {
            "week_period": f"{datetime.now().strftime('%Y-%m-%d')} to "
                          f"{(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}",
            "analysis_timestamp": datetime.now().isoformat(),
            "transaction_count": len(transactions)
        },
        "spending_performance": {
            "total_planned_spending": 315.0,
            "total_actual_spending": 287.50,
            "planned_savings_target": 200.0,
            "spending_vs_plan": -27.50,
            "spending_adherence_rate": 0.91,
            "over_budget": False,
            "budget_variance_percentage": -8.73
        },
        "category_performance": {
            "Food & Dining": {
                "planned_limit": 105.0,
                "actual_spent": 98.50,
                "variance": -6.50,
                "adherence_rate": 0.94,
                "status": "under_budget",
                "variance_percentage": -6.19
            }
        },
        "goal_achievement": {
            "metric_achievements": [
                {
                    "metric_name": "Weekly Savings",
                    "target_value": 200,
                    "estimated_achievement_rate": 0.85,
                    "status": "on_track"
                }
            ],
            "overall_goal_success_rate": 0.85
        },
        "ai_insights": {
            "key_insights": [
                {
                    "insight_type": "success",
                    "title": "Great Budget Adherence",
                    "description": "You stayed under budget this week!",
                    "impact_level": "high"
                }
            ],
            "success_highlights": [
                "Stayed under budget in Food & Dining category"
            ],
            "improvement_areas": []
        },
        "performance_scores": {
            "overall_performance_score": 85.0,
            "spending_adherence_score": 91.0,
            "category_discipline_score": 88.0,
            "goal_achievement_score": 85.0,
            "performance_grade": "B+"
        },
        "recommendations": [
            {
                "type": "encouragement",
                "priority": "low",
                "title": "Keep Up the Good Work",
                "description": "You're doing great with budget adherence!",
                "specific_action": "Continue current spending patterns"
            }
        ]
    }


def _generate_llm_weekly_recap(plan: Dict, transactions: List) -> Dict:
    """Generate weekly recap using LLM agents."""
    if not LLM_AVAILABLE:
        return _generate_mock_weekly_recap(plan, transactions)
    
    try:
        # Initialize the Recap agent
        recap_agent = RecapAgent(
            weekly_plan=plan,
            actual_transactions=transactions,
            llm_client=NoumiLLMClient(provider="google")
        )
        
        # Generate the recap
        weekly_recap = recap_agent.generate_weekly_recap()
        return weekly_recap
        
    except Exception as e:
        print(f"Error generating LLM recap: {e}")
        return _generate_mock_weekly_recap(plan, transactions)


if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 