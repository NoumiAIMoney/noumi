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
import uuid
import sys
import os

# Load environment variables
load_dotenv()

# Import database and analytics
from database import db, User as DbUser, UserGoal, Transaction, PlaidConnection
from analytics import TransactionAnalyzer

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


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
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


class PlaidConnectionRequest(BaseModel):
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
    month: Optional[str] = None


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
    try:
        user_id = str(uuid.uuid4())
        
        # Create user in database
        db_user = DbUser(
            id=user_id,
            email=user_data.email,
            name=user_data.name,
            created_at=datetime.now().isoformat(),
            preferences={"theme": "light", "currency": "USD"}
        )
        
        success = db.create_user(db_user)
        if not success:
            raise HTTPException(status_code=400, detail="User already exists")
        
        return {
            "message": "User registered successfully",
            "user": {
                "id": user_id,
                "email": user_data.email,
                "name": user_data.name
            },
            "token": MOCK_TOKEN
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
    # Try to get user from database
    db_user = db.get_user(current_user["id"])
    if db_user:
        return User(
            id=db_user.id,
            email=db_user.email,
            name=db_user.name,
            created_at=datetime.fromisoformat(db_user.created_at),
            preferences=db_user.preferences
        )
    
    # Fallback to mock data
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
    try:
        # Validate data
        if quiz_data.goal_amount <= 0:
            raise HTTPException(
                status_code=400, detail="Goal amount must be positive"
            )
        
        if quiz_data.net_monthly_income <= 0:
            raise HTTPException(
                status_code=400, detail="Monthly income must be positive"
            )
        
        # Save to database
        goal = UserGoal(
            user_id=current_user["id"],
            goal_name=quiz_data.goal_name,
            goal_description=quiz_data.goal_description,
            goal_amount=quiz_data.goal_amount,
            target_date=quiz_data.target_date.isoformat(),
            net_monthly_income=quiz_data.net_monthly_income,
            created_at=datetime.now().isoformat()
        )
        
        success = db.save_user_goal(goal)
        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to save quiz data"
            )
        
        return {"success": True}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/plaid/connect")
async def initiate_plaid_connection(
    plaid_data: PlaidConnectionRequest,
    current_user=Depends(get_current_user)
):
    """Initiate Plaid connection and fetch account/transaction data"""
    try:
        # TODO: Implement actual Plaid integration
        # For now, simulate with mock data and save to database
        
        # Create mock accounts and transactions
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
        
        # Save Plaid connection
        plaid_connection = PlaidConnection(
            user_id=current_user["id"],
            access_token=f"access_token_{uuid.uuid4()}",
            accounts=mock_accounts,
            connected_at=datetime.now().isoformat()
        )
        
        db.save_plaid_connection(plaid_connection)
        
        # Create sample transactions for testing
        sample_transactions = [
            Transaction(
                transaction_id=f"txn_{uuid.uuid4()}",
                user_id=current_user["id"],
                account_id="acc_1",
                amount=-12.50,
                date=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                description="Starbucks Coffee",
                category="Food & Dining",
                merchant_name="Starbucks",
                created_at=datetime.now().isoformat()
            ),
            Transaction(
                transaction_id=f"txn_{uuid.uuid4()}",
                user_id=current_user["id"],
                account_id="acc_1",
                amount=-85.00,
                date=(datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                description="Shell Gas Station",
                category="Transportation",
                merchant_name="Shell",
                created_at=datetime.now().isoformat()
            ),
            Transaction(
                transaction_id=f"txn_{uuid.uuid4()}",
                user_id=current_user["id"],
                account_id="acc_1",
                amount=-67.43,
                date=(datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
                description="Safeway Grocery Store",
                category="Food & Dining",
                merchant_name="Safeway",
                created_at=datetime.now().isoformat()
            ),
            Transaction(
                transaction_id=f"txn_{uuid.uuid4()}",
                user_id=current_user["id"],
                account_id="acc_1",
                amount=-15.99,
                date=(datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"),
                description="Netflix Subscription",
                category="Entertainment",
                merchant_name="Netflix",
                created_at=datetime.now().isoformat()
            ),
            Transaction(
                transaction_id=f"txn_{uuid.uuid4()}",
                user_id=current_user["id"],
                account_id="acc_1",
                amount=-89.99,
                date=(datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
                description="Amazon Purchase",
                category="Shopping",
                merchant_name="Amazon",
                created_at=datetime.now().isoformat()
            )
        ]
        
        db.save_transactions(sample_transactions)
        
        return {
            "status": "connected",
            "message": "Plaid connection established and data fetched"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/anomalies/yearly", response_model=AnomalyData)
async def get_yearly_anomaly_counts(current_user=Depends(get_current_user)):
    """Get yearly anomaly counts for the current user"""
    try:
        analyzer = TransactionAnalyzer(current_user["id"])
        anomalies = analyzer.detect_spending_anomalies()
        return AnomalyData(anomalies=anomalies)
    except Exception as e:
        print(f"Error getting anomalies: {e}")
        # COMMENTED OUT - NO MORE MOCK DATA FALLBACK
        # Return mock data if analytics fails
        # return AnomalyData(anomalies=[0,0,0,0,0,0,0,0,0,0,0,0])
        raise HTTPException(status_code=500, detail="Failed to get anomaly data")


@app.get("/trends", response_model=List[SpendingTrend])
async def get_spending_trends(current_user=Depends(get_current_user)):
    """Get spending trends and insights for the current user"""
    try:
        analyzer = TransactionAnalyzer(current_user["id"])
        trends = analyzer.analyze_spending_trends()
        
        return [SpendingTrend(icon=trend["icon"], trend=trend["trend"]) 
                for trend in trends]
    except Exception as e:
        print(f"Error getting trends: {e}")
        # COMMENTED OUT - NO MORE MOCK DATA FALLBACK
        # Return mock trends if analytics fails
        # return [SpendingTrend(icon="📊", trend="Unable to analyze trends")]
        raise HTTPException(status_code=500, detail="Failed to get spending trends")


@app.get("/spending/categories", response_model=List[SpendingCategory])
async def get_spending_categories(current_user=Depends(get_current_user)):
    """Get spending breakdown by categories for the current user"""
    try:
        analyzer = TransactionAnalyzer(current_user["id"])
        categories = analyzer.get_spending_categories_with_history()
        
        return [SpendingCategory(
            category_name=cat["category_name"],
            amount=cat["amount"],
            month=cat["month"]
        ) for cat in categories]
    except Exception as e:
        print(f"Error getting spending categories: {e}")
        # COMMENTED OUT - NO MORE MOCK DATA FALLBACK
        # Return mock data if database query fails
        # return [SpendingCategory(category_name="Food", amount=0, month="2025-06")]
        raise HTTPException(status_code=500, detail="Failed to get spending categories")


@app.get("/goal/computed", response_model=ComputedGoal)
async def get_computed_goal_data(current_user=Depends(get_current_user)):
    """Get computed goal data with progress calculations"""
    try:
        # Get goal from database
        goal = db.get_user_goal(current_user["id"])
        if not goal:
            raise HTTPException(status_code=404, detail="No goal found")
        
        # Calculate amount saved (simplified calculation)
        analyzer = TransactionAnalyzer(current_user["id"])
        total_spent = analyzer.calculate_total_spent_ytd()
        
        # Use goal's net monthly income for calculation
        months_elapsed = 6  # Approximate months since start of year
        total_income = goal.net_monthly_income * months_elapsed
        amount_saved = max(0, total_income - total_spent)
        
        return ComputedGoal(
            goal_name=goal.goal_name,
            target_date=datetime.strptime(goal.target_date, "%Y-%m-%d").date(),
            goal_amount=goal.goal_amount,
            amount_saved=amount_saved
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting computed goal: {e}")
        # COMMENTED OUT - NO MORE MOCK DATA FALLBACK
        # Return mock data if database query fails
        # return ComputedGoal(
        #     goal_name="Savings Goal",
        #     target_date=date(2025, 12, 31),
        #     goal_amount=5000.0,
        #     amount_saved=1250.0
        # )
        raise HTTPException(status_code=500, detail="Failed to get goal data")


@app.get("/habits", response_model=List[UserHabit])
async def get_user_habits(current_user=Depends(get_current_user)):
    """Get user habits based on spending patterns"""
    try:
        # Analyze spending patterns to suggest habits
        analyzer = TransactionAnalyzer(current_user["id"])
        trends = analyzer.analyze_spending_trends()
        
        habits = []
        
        # Generate habit suggestions based on real data
        if len(trends) > 0:
            habits.append(UserHabit(
                habit_description="Log in to Noumi daily",
                occurrences=7
            ))
            habits.append(UserHabit(
                habit_description="Set weekly spending limits",
                occurrences=1
            ))
        
        return habits
        
    except Exception as e:
        print(f"Error analyzing habits: {e}")
        # COMMENTED OUT - NO MORE MOCK DATA FALLBACK
        # Return mock habits if analysis fails
        # return [
        #     UserHabit(habit_description="Log in to Noumi daily", occurrences=7),
        #     UserHabit(habit_description="Set weekly spending limits", occurrences=1)
        # ]
        raise HTTPException(status_code=500, detail="Failed to analyze habits")


@app.get("/streak/weekly", response_model=List[int])
async def get_weekly_streak(current_user=Depends(get_current_user)):
    """Get weekly streak data for the current user"""
    try:
        analyzer = TransactionAnalyzer(current_user["id"])
        streak = analyzer.calculate_weekly_streak()
        return streak
    except Exception as e:
        print(f"Error getting weekly streak: {e}")
        # COMMENTED OUT - NO MORE MOCK DATA FALLBACK
        # Return mock streak if calculation fails
        # return [1, 1, 1, 1, 1, 1, 1]
        raise HTTPException(status_code=500, detail="Failed to get weekly streak")


@app.get("/spending/status", response_model=SpendingStatus)
async def get_spending_status(current_user=Depends(get_current_user)):
    """Get spending status - income vs expenses with safe spending amount"""
    try:
        analyzer = TransactionAnalyzer(current_user["id"])
        status = analyzer.calculate_spending_status()
        return SpendingStatus(**status)
    except Exception as e:
        print(f"Error getting spending status: {e}")
        # COMMENTED OUT - NO MORE MOCK DATA FALLBACK
        # Return mock status if calculation fails
        # return SpendingStatus(income=5000, expenses=3500, amount_safe_to_spend=1500)
        raise HTTPException(status_code=500, detail="Failed to get spending status")


@app.get("/savings/weekly", response_model=WeeklySavings)
async def get_weekly_savings_data(current_user=Depends(get_current_user)):
    """Get weekly savings data with actual vs suggested amounts"""
    try:
        analyzer = TransactionAnalyzer(current_user["id"])
        savings = analyzer.calculate_weekly_savings()
        return WeeklySavings(**savings)
    except Exception as e:
        print(f"Error getting weekly savings: {e}")
        # COMMENTED OUT - NO MORE MOCK DATA FALLBACK
        # Return mock savings if calculation fails
        # return WeeklySavings(actual_savings=200.0, suggested_savings_amount_weekly=250.0)
        raise HTTPException(status_code=500, detail="Failed to get weekly savings")


@app.get("/streak/longest", response_model=LongestStreak)
async def get_longest_no_anomaly_streak(
    current_user=Depends(get_current_user)
):
    """Get longest streak without spending anomalies"""
    try:
        analyzer = TransactionAnalyzer(current_user["id"])
        longest = analyzer.calculate_longest_streak()
        return LongestStreak(longest_streak=longest)
    except Exception as e:
        print(f"Error getting longest streak: {e}")
        # COMMENTED OUT - NO MORE MOCK DATA FALLBACK
        # Return mock longest streak if calculation fails
        # return LongestStreak(longest_streak=42)
        raise HTTPException(status_code=500, detail="Failed to get longest streak")


@app.get("/spending/total", response_model=TotalSpent)
async def get_total_amount_spent(current_user=Depends(get_current_user)):
    """Get total amount spent year-to-date"""
    try:
        analyzer = TransactionAnalyzer(current_user["id"])
        total = analyzer.calculate_total_spent_ytd()
        return TotalSpent(spent_so_far=total)
    except Exception as e:
        print(f"Error getting total spent: {e}")
        # COMMENTED OUT - NO MORE MOCK DATA FALLBACK
        # Return mock total if calculation fails
        # return TotalSpent(spent_so_far=2500.00)
        raise HTTPException(status_code=500, detail="Failed to get total spending")


# Weekly Plan and Recap Endpoints


# COMMENTED OUT - NO MORE MOCK DATA - USING REAL DATABASE ONLY
# def _generate_mock_weekly_plan() -> Dict[str, Any]:
#     """Generate mock weekly plan for testing purposes."""
#     return {
#         "week_start_date": datetime.now().strftime("%Y-%m-%d"),
#         "savings_target": {
#             "amount": 200.00,
#             "currency": "USD"
#         },
#         "spending_limits": {
#             "Food & Dining": {"daily_limit": 15.0, "weekly_limit": 105.0},
#             "Transportation": {"daily_limit": 8.0, "weekly_limit": 56.0},
#             "Entertainment": {"daily_limit": 10.0, "weekly_limit": 70.0},
#             "Shopping": {"daily_limit": 12.0, "weekly_limit": 84.0}
#         },
#         "daily_recommendations": [
#             {
#                 "day": "Monday",
#                 "actions": ["Check account balance", "Set weekly goals"],
#                 "focus_area": "Goal Setting",
#                 "motivation": "Start your week strong!"
#             },
#             {
#                 "day": "Tuesday", 
#                 "actions": ["Track expenses", "Review spending limits"],
#                 "focus_area": "Expense Tracking",
#                 "motivation": "Stay on track!"
#             },
#             {
#                 "day": "Wednesday",
#                 "actions": ["Mid-week check-in", "Adjust if needed"],
#                 "focus_area": "Progress Review", 
#                 "motivation": "You're halfway there!"
#             },
#             {
#                 "day": "Thursday",
#                 "actions": ["Evaluate spending", "Plan weekend budget"],
#                 "focus_area": "Weekend Planning",
#                 "motivation": "Prepare for success!"
#             },
#             {
#                 "day": "Friday",
#                 "actions": ["Review week's progress", "Set weekend limits"],
#                 "focus_area": "Week Review",
#                 "motivation": "Strong finish ahead!"
#             },
#             {
#                 "day": "Saturday",
#                 "actions": ["Track weekend spending", "Find free activities"],
#                 "focus_area": "Weekend Management",
#                 "motivation": "Smart weekend choices!"
#             },
#             {
#                 "day": "Sunday",
#                 "actions": ["Calculate weekly total", "Plan next week"],
#                 "focus_area": "Weekly Wrap-up",
#                 "motivation": "Prepare for another successful week!"
#             }
#         ],
#         "tracking_metrics": [
#             {
#                 "metric_name": "Weekly Savings",
#                 "target_value": 200,
#                 "current_value": 0
#             },
#             {
#                 "metric_name": "Days Under Budget",
#                 "target_value": 7,
#                 "current_value": 0
#             }
#         ],
#         "weekly_challenges": [
#             "Track every expense for 7 days",
#             "Cook at home 5 out of 7 days",
#             "Find one free entertainment activity"
#         ],
#         "success_tips": [
#             "Review progress daily",
#             "Celebrate small wins", 
#             "Stay consistent with tracking"
#         ],
#         "ml_features": {
#             "suggested_savings_amount": 200.0,
#             "spending_efficiency_score": 85.0
#         }
#     }


def _generate_llm_weekly_plan(user_prefs: Dict, spending_data: Dict) -> Dict:
    """Generate weekly plan using LLM agents."""
    if not LLM_AVAILABLE:
        # COMMENTED OUT - NO MORE MOCK DATA FALLBACK
        # return _generate_mock_weekly_plan()
        raise HTTPException(status_code=503, detail="LLM service unavailable")
    
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
        # COMMENTED OUT - NO MORE MOCK DATA FALLBACK
        # return _generate_mock_weekly_plan()
        raise HTTPException(status_code=500, detail="Failed to generate weekly plan")


@app.get("/plans/weekly", response_model=WeeklyPlan)
async def get_weekly_plan(current_user=Depends(get_current_user)):
    """Get current weekly plan for the user"""
    try:
        # Get user preferences from database
        goal = db.get_user_goal(current_user["id"])
        if not goal:
            # Use default preferences if no goal set
            user_prefs = {
                "risk_tolerance": "moderate",
                "savings_goals": {"primary_goal": "General savings"},
                "spending_priorities": ["Food & Dining", "Transportation"]
            }
        else:
            user_prefs = {
                "risk_tolerance": "moderate",
                "savings_goals": {
                    "primary_goal": goal.goal_name,
                    "target_amount": goal.goal_amount,
                    "timeframe_months": 6,
                },
                "spending_priorities": ["Food & Dining", "Transportation", 
                                      "Entertainment", "Shopping"]
            }
        
        # Get spending analysis from database
        analyzer = TransactionAnalyzer(current_user["id"])
        categories = analyzer.get_spending_categories_with_history()
        
        spending_data = {
            "monthly_analysis": {"average_monthly_spending": 2500.0},
            "category_analysis": {}
        }
        
        # Convert categories to analysis format
        for cat in categories:
            if cat["month"] == datetime.now().strftime("%Y-%m"):
                spending_data["category_analysis"][cat["category_name"]] = {
                    "total_amount": cat["amount"],
                    "percentage": (cat["amount"] / 2500.0) * 100
                }
        
        plan_data = _generate_llm_weekly_plan(user_prefs, spending_data)
        return WeeklyPlan(**plan_data)
        
    except Exception as e:
        print(f"Error getting weekly plan: {e}")
        # Return mock plan if LLM or database fails
        # plan_data = _generate_mock_weekly_plan()
        # return WeeklyPlan(**plan_data)
        raise HTTPException(status_code=500, detail="Failed to generate weekly plan")


@app.post("/plans/weekly", response_model=WeeklyPlan)
async def create_weekly_plan(
    request: WeeklyPlanRequest,
    current_user=Depends(get_current_user)
):
    """Generate a new weekly plan based on user preferences and spending"""
    try:
        # Use provided data or fetch from database
        if request.user_preferences:
            user_prefs = request.user_preferences
        else:
            goal = db.get_user_goal(current_user["id"])
            user_prefs = {
                "risk_tolerance": "moderate",
                "savings_goals": {"primary_goal": goal.goal_name if goal else "General savings"}
            }
        
        if request.spending_analysis:
            spending_data = request.spending_analysis
        else:
            analyzer = TransactionAnalyzer(current_user["id"])
            categories = analyzer.get_spending_categories_with_history()
            spending_data = {
                "monthly_analysis": {"average_monthly_spending": 2500.0},
                "category_analysis": {
                    cat["category_name"]: {"total_amount": cat["amount"]}
                    for cat in categories
                    if cat["month"] == datetime.now().strftime("%Y-%m")
                }
            }
        
        # Generate new plan using LLM
        plan_data = _generate_llm_weekly_plan(user_prefs, spending_data)
        
        # TODO: Save to database
        return WeeklyPlan(**plan_data)
        
    except Exception as e:
        print(f"Error creating weekly plan: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate weekly plan")


def _get_user_spending_data(user_id: str) -> Dict[str, Any]:
    """Get user's spending data from database/storage"""
    try:
        analyzer = TransactionAnalyzer(user_id)
        categories = analyzer.get_spending_categories_with_history()
        
        # Get recent transactions for detailed analysis
        recent_transactions = db.get_user_transactions(
            user_id, 
            (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        )
        
        return {
            "monthly_analysis": {"average_monthly_spending": 2500.0},
            "category_analysis": {
                cat["category_name"]: {
                    "total_amount": cat["amount"], 
                    "percentage": (cat["amount"] / 2500.0) * 100
                }
                for cat in categories
                if cat["month"] == datetime.now().strftime("%Y-%m")
            },
            "recent_transactions": [
                {
                    "transaction_id": txn.transaction_id,
                    "amount": txn.amount,
                    "description": txn.description,
                    "category": txn.category,
                    "date": txn.date,
                    "merchant_name": txn.merchant_name
                }
                for txn in recent_transactions[:10]  # Latest 10 transactions
            ]
        }
    except Exception as e:
        print(f"Error getting spending data: {e}")
        return {
            "monthly_analysis": {"average_monthly_spending": 2500.0},
            "category_analysis": {},
            "recent_transactions": []
        }


def _get_user_preferences(user_id: str) -> Dict[str, Any]:
    """Get user preferences from database/storage"""
    try:
        goal = db.get_user_goal(user_id)
        if goal:
            return {
                "risk_tolerance": "moderate",
                "savings_goals": {
                    "primary_goal": goal.goal_name,
                    "timeframe_months": 6,
                    "target_amount": goal.goal_amount
                },
                "spending_priorities": ["Food & Dining", "Transportation", 
                                      "Entertainment", "Shopping"],
                "financial_knowledge": "intermediate",
                "motivation_style": "milestone_focused"
            }
        else:
            return {
                "risk_tolerance": "moderate",
                "savings_goals": {"primary_goal": "General savings"},
                "spending_priorities": ["Food & Dining"],
                "financial_knowledge": "beginner"
            }
    except Exception as e:
        print(f"Error getting user preferences: {e}")
        return {
            "risk_tolerance": "moderate",
            "savings_goals": {"primary_goal": "General savings"},
            "spending_priorities": ["Food & Dining"],
            "financial_knowledge": "beginner"
        }


def _get_current_weekly_plan(user_id: str) -> Dict[str, Any]:
    """Get user's current weekly plan from database/storage"""
    try:
        user_prefs = _get_user_preferences(user_id)
        spending_data = _get_user_spending_data(user_id)
        
        return _generate_llm_weekly_plan(user_prefs, spending_data)
    except Exception as e:
        print(f"Error getting weekly plan: {e}")
        # Return mock plan if database fails
        # return _generate_mock_weekly_plan()
        raise HTTPException(status_code=500, detail="Failed to generate weekly plan")


def _get_week_transactions(user_id: str, week_start: str = None) -> List[Dict]:
    """Get user's transactions for a specific week"""
    try:
        if week_start is None:
            # Get current week transactions
            today = datetime.now()
            days_since_monday = today.weekday()
            monday = today - timedelta(days=days_since_monday)
            week_start = monday.strftime("%Y-%m-%d")
        
        # Get week end date
        week_end = (datetime.strptime(week_start, "%Y-%m-%d") + timedelta(days=7)).strftime("%Y-%m-%d")
        
        # Fetch transactions from database
        transactions = db.get_user_transactions(user_id, week_start, week_end)
        
        return [
            {
                "transaction_id": txn.transaction_id,
                "amount": txn.amount,
                "description": txn.description,
                "category": txn.category,
                "date": txn.date,
                "merchant_name": txn.merchant_name,
                "account_id": txn.account_id
            }
            for txn in transactions
        ]
    except Exception as e:
        print(f"Error getting week transactions: {e}")
        # Return mock transactions if database fails
        return [
            {
                "transaction_id": "fallback_txn_1",
                "amount": -45.50,
                "description": "Grocery Store",
                "category": "Food & Dining",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "merchant_name": "Safeway",
                "account_id": "acc_1"
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
        # mock_plan = _generate_mock_weekly_plan()
        # mock_transactions = [
        #     {
        #         "transaction_id": "fallback_txn_1",
        #         "amount": -45.50,
        #         "description": "Grocery Store",
        #         "category": "Food & Dining",
        #         "date": datetime.now().strftime("%Y-%m-%d")
        #     }
        # ]
        # recap_data = _generate_llm_weekly_recap(mock_plan, mock_transactions)
        raise HTTPException(status_code=500, detail="Failed to generate weekly recap")


def _enhance_recap_with_metrics(
    recap_data: Dict, 
    plan: Dict, 
    transactions: List
) -> Dict:
    """Enhance the LLM-generated recap with additional computed metrics"""
    try:
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
    except Exception as e:
        print(f"Error enhancing recap: {e}")
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
        # save_weekly_recap_to_db(current_user["id"], recap_data)
        
        return WeeklyRecap(**recap_data)
        
    except Exception as e:
        print(f"Error creating weekly recap: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate weekly recap")


# COMMENTED OUT - NO MORE MOCK DATA - USING REAL DATABASE ONLY
# def _generate_mock_weekly_recap(plan: Dict, transactions: List) -> Dict:
#     """Generate mock weekly recap for testing purposes."""
#     return {
#         "recap_metadata": {
#             "week_period": f"{datetime.now().strftime('%Y-%m-%d')} to "
#                           f"{(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}",
#             "analysis_timestamp": datetime.now().isoformat(),
#             "transaction_count": len(transactions)
#         },
#         "spending_performance": {
#             "total_planned_spending": 315.0,
#             "total_actual_spending": 287.50,
#             "planned_savings_target": 200.0,
#             "spending_vs_plan": -27.50,
#             "spending_adherence_rate": 0.91,
#             "over_budget": False,
#             "budget_variance_percentage": -8.73
#         },
#         "category_performance": {
#             "Food & Dining": {
#                 "planned_limit": 105.0,
#                 "actual_spent": 98.50,
#                 "variance": -6.50,
#                 "adherence_rate": 0.94,
#                 "status": "under_budget",
#                 "variance_percentage": -6.19
#             }
#         },
#         "goal_achievement": {
#             "metric_achievements": [
#                 {
#                     "metric_name": "Weekly Savings",
#                     "target_value": 200,
#                     "estimated_achievement_rate": 0.85,
#                     "status": "on_track"
#                 }
#             ],
#             "overall_goal_success_rate": 0.85
#         },
#         "ai_insights": {
#             "key_insights": [
#                 {
#                     "insight_type": "success",
#                     "title": "Great Budget Adherence",
#                     "description": "You stayed under budget this week!",
#                     "impact_level": "high"
#                 }
#             ],
#             "success_highlights": [
#                 "Stayed under budget in Food & Dining category"
#             ],
#             "improvement_areas": []
#         },
#         "performance_scores": {
#             "overall_performance_score": 85.0,
#             "spending_adherence_score": 91.0,
#             "category_discipline_score": 88.0,
#             "goal_achievement_score": 85.0,
#             "performance_grade": "B+"
#         },
#         "recommendations": [
#             {
#                 "type": "encouragement",
#                 "priority": "low",
#                 "title": "Keep Up the Good Work",
#                 "description": "You're doing great with budget adherence!",
#                 "specific_action": "Continue current spending patterns"
#             }
#         ]
#     }


def _generate_llm_weekly_recap(plan: Dict, transactions: List) -> Dict:
    """Generate weekly recap using LLM agents."""
    if not LLM_AVAILABLE:
        # COMMENTED OUT - NO MORE MOCK DATA FALLBACK
        # return _generate_mock_weekly_recap(plan, transactions)
        raise HTTPException(status_code=503, detail="LLM service unavailable")
    
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
        # COMMENTED OUT - NO MORE MOCK DATA FALLBACK
        # return _generate_mock_weekly_recap(plan, transactions)
        raise HTTPException(status_code=500, detail="Failed to generate weekly recap")


# Sample data insertion endpoint for testing
@app.post("/admin/insert-sample-data")
async def insert_sample_data(current_user=Depends(get_current_user)):
    """Insert sample data for testing purposes"""
    try:
        user_id = current_user["id"]
        
        # Insert sample goal if not exists
        existing_goal = db.get_user_goal(user_id)
        if not existing_goal:
            sample_goal = UserGoal(
                user_id=user_id,
                goal_name="Trip to Mexico",
                goal_description="Vacation fund for Mexico trip",
                goal_amount=1200.0,
                target_date="2025-09-30",
                net_monthly_income=6000.0,
                created_at=datetime.now().isoformat()
            )
            db.save_user_goal(sample_goal)
        
        # Insert sample transactions for better testing
        sample_transactions = []
        for i in range(30):  # 30 days of transactions
            date_offset = datetime.now() - timedelta(days=i)
            
            # Add 1-3 transactions per day
            for j in range(1, 4):
                categories = ["Food & Dining", "Transportation", "Entertainment", "Shopping"]
                merchants = {
                    "Food & Dining": ["Starbucks", "McDonald's", "Subway", "Chipotle"],
                    "Transportation": ["Shell", "Chevron", "Uber", "Metro"],
                    "Entertainment": ["Netflix", "Spotify", "AMC Theaters"],
                    "Shopping": ["Amazon", "Target", "Walmart", "Best Buy"]
                }
                
                category = categories[j % len(categories)]
                merchant = merchants[category][j % len(merchants[category])]
                amount = -round(5 + (i + j) * 2.5, 2)  # Vary amounts
                
                sample_transactions.append(Transaction(
                    transaction_id=f"sample_{user_id}_{i}_{j}",
                    user_id=user_id,
                    account_id="acc_sample",
                    amount=amount,
                    date=date_offset.strftime("%Y-%m-%d"),
                    description=f"{merchant} Purchase",
                    category=category,
                    merchant_name=merchant,
                    created_at=datetime.now().isoformat()
                ))
        
        db.save_transactions(sample_transactions)
        
        return {
            "message": "Sample data inserted successfully",
            "transactions_added": len(sample_transactions),
            "goal_created": existing_goal is None
        }
        
    except Exception as e:
        print(f"Error inserting sample data: {e}")
        raise HTTPException(status_code=500, detail="Failed to insert sample data")


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