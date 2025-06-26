"""
Chain of Thoughts Trend Analysis Agent for Noumi

Implements comprehensive spending trend analysis using multi-step reasoning.
Based on Chain of Thoughts methodology for deep analytical reasoning.
Uses prompt engineering to ensure LLM only uses provided analyzed numbers.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from .base_trend_agent import BaseTrendAgent
from ..utils.llm_client import NoumiLLMClient


class ChainOfThoughtsTrendAgent(BaseTrendAgent):
    """
    Chain of Thoughts trend analysis agent for comprehensive spending insights.
    
    CoT Process:
    1. Data Collection & Preprocessing (gather all relevant data)
    2. Pattern Recognition & Analysis (LLM identifies spending patterns)
    3. Contextual Insight Generation (LLM generates meaningful insights)
    4. Trend Synthesis & Icon Mapping (LLM creates final trend outputs)
    
    Prompt Engineering Approach:
    - Provides only analyzed numbers to LLM
    - Instructs LLM to use ONLY provided data
    - Maintains consistency through structured prompts
    - Uses Chain of Thought reasoning for robustness
    """

    def __init__(self, user_preferences: Dict[str, Any],
                 spending_data: Dict[str, Any],
                 transaction_history: List[Dict[str, Any]],
                 llm_client: Optional[NoumiLLMClient] = None):
        super().__init__(user_preferences, spending_data, transaction_history)
        self.llm_client = llm_client or NoumiLLMClient(provider="google")
        self.cot_trace = []  # Track Chain of Thoughts steps for debugging

    def analyze_spending_trends(self) -> List[Dict[str, str]]:
        """
        Generate comprehensive spending trends using Chain of Thoughts 
        methodology with LLM-powered analysis of provided numbers.
        """
        
        print("🔄 DEBUG: Using LLM Chain of Thoughts trend analysis")
        
        # CoT Step 1: Data Collection & Preprocessing
        self._log_cot_step("Data Collection & Preprocessing")
        structured_data = self._cot_step1_collect_and_preprocess()
        
        # CoT Step 2: Pattern Recognition & Analysis (LLM)
        self._log_cot_step("LLM Pattern Recognition & Analysis")
        pattern_analysis = self._cot_step2_pattern_recognition(structured_data)
        
        # CoT Step 3: Contextual Insight Generation (LLM)
        self._log_cot_step("LLM Contextual Insight Generation")
        contextual_insights = self._cot_step3_contextual_insights(
            structured_data, pattern_analysis
        )
        
        # CoT Step 4: Trend Synthesis & Icon Mapping (LLM)
        self._log_cot_step("LLM Trend Synthesis & Icon Mapping")
        final_trends = self._cot_step4_trend_synthesis(
            structured_data, pattern_analysis, contextual_insights
        )
        
        print(f"🔄 DEBUG: Generated {len(final_trends)} LLM-powered trends")
        return final_trends

    def _cot_step1_collect_and_preprocess(self) -> Dict[str, Any]:
        """
        CoT Step 1: Collect and preprocess all relevant data.
        Focus: Data completeness, frequency patterns, anomalies
        """
        
        # Calculate spending velocity (transactions per week)
        transaction_dates = [
            t.get("date") for t in self.transaction_history if t.get("date")
        ]
        
        spending_velocity = 0
        date_range = 0
        if transaction_dates:
            date_range = (
                datetime.strptime(max(transaction_dates), "%Y-%m-%d") -
                datetime.strptime(min(transaction_dates), "%Y-%m-%d")
            ).days
            weeks = max(1, date_range / 7)
            spending_velocity = len(self.transaction_history) / weeks
        
        # Analyze day-of-week patterns
        day_patterns = {}
        weekend_spending = []
        weekday_spending = []
        evening_spending = []
        
        for txn in self.transaction_history:
            day = txn.get("day_of_week", "Unknown")
            if day not in day_patterns:
                day_patterns[day] = 0
            day_patterns[day] += 1
            
            if txn.get("is_weekend"):
                weekend_spending.append(abs(txn.get("amount", 0)))
            else:
                weekday_spending.append(abs(txn.get("amount", 0)))
                
            if txn.get("local_time_bucket") == "Evening":
                evening_spending.append(abs(txn.get("amount", 0)))
        
        # Calculate merchant frequency patterns
        merchant_frequency = {}
        for txn in self.transaction_history:
            merchant = txn.get("merchant_name", "Unknown")
            if merchant not in merchant_frequency:
                merchant_frequency[merchant] = 0
            merchant_frequency[merchant] += 1
        
        # Sort merchants by frequency
        top_merchants = sorted(
            merchant_frequency.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        # Calculate category frequency and timing
        category_timing = {}
        category_frequency = {}
        for txn in self.transaction_history:
            category = txn.get("category", "Unknown")
            day = txn.get("day_of_week", "Unknown")
            
            if category not in category_frequency:
                category_frequency[category] = 0
                category_timing[category] = {}
            
            category_frequency[category] += 1
            
            if day not in category_timing[category]:
                category_timing[category][day] = 0
            category_timing[category][day] += 1
        
        # Calculate category concentration (Gini coefficient approximation)
        category_amounts = []
        category_analysis = self.spending_data.get("category_analysis", {})
        for cat_data in category_analysis.values():
            category_amounts.append(cat_data.get("total_amount", 0))
        
        concentration_score = self._calculate_concentration(category_amounts)
        
        # Prepare analyzed numbers for LLM
        total_transactions = len(self.transaction_history)
        weekend_count = len(weekend_spending)
        weekday_count = len(weekday_spending)
        weekend_percentage = (weekend_count / total_transactions * 100) if total_transactions > 0 else 0
        weekday_percentage = (weekday_count / total_transactions * 100) if total_transactions > 0 else 0
        
        return {
            "analyzed_numbers": {
                "total_transactions": total_transactions,
                "spending_velocity_per_week": round(spending_velocity, 1),
                "weekend_transactions": weekend_count,
                "weekday_transactions": weekday_count,
                "weekend_percentage": round(weekend_percentage, 1),
                "weekday_percentage": round(weekday_percentage, 1),
                "evening_transactions": len(evening_spending),
                "evening_percentage": round((len(evening_spending) / total_transactions * 100) if total_transactions > 0 else 0, 1),
                "top_merchants": dict(top_merchants[:5]),
                "category_frequencies": category_frequency,
                "analysis_period_days": date_range,
                "category_concentration_score": round(concentration_score, 2)
            },
            "user_context": {
                "financial_goal": self.user_preferences.get("financial_goal", ""),
                "impulse_triggers": self.user_preferences.get("impulse_triggers", []),
                "budgeting_score": self.user_preferences.get("budgeting_score", 0),
                "goal_name": self.user_preferences.get("goal_name", ""),
                "goal_amount": self.user_preferences.get("goal_amount", 0),
                "net_monthly_income": self.user_preferences.get("net_monthly_income", 0)
            },
            "spending_summary": {
                "monthly_spending": self.spending_data.get("monthly_analysis", {}).get("average_monthly_spending", 0),
                "anomaly_counts": self.spending_data.get("anomaly_counts", []),
                "top_categories": self._get_top_categories(3)
            }
        }

    def _cot_step2_pattern_recognition(self, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        CoT Step 2: LLM-powered pattern recognition using only provided numbers.
        Focus: Identify spending patterns with confidence scores
        """
        
        system_role = """
        You are an expert financial data analyst specializing in spending pattern recognition.
        
        CRITICAL INSTRUCTIONS:
        1. Use ONLY the analyzed numbers provided in the data
        2. Do NOT make up or assume any additional numbers
        3. Base ALL analysis on the exact figures given
        4. Provide confidence scores (0-100) for each pattern identified
        5. Use Chain of Thought reasoning to explain your analysis step by step
        
        ANALYSIS FOCUS:
        - Day-of-week spending patterns (weekday vs weekend)
        - Merchant frequency patterns 
        - Category distribution patterns
        - Time-based spending patterns
        - Spending velocity patterns
        
        Return detailed pattern analysis with confidence scores.
        """

        content = f"""
        ANALYZED SPENDING DATA (Use ONLY these numbers):
        {structured_data['analyzed_numbers']}
        
        USER CONTEXT:
        {structured_data['user_context']}
        
        SPENDING SUMMARY:
        {structured_data['spending_summary']}
        
        Perform Chain of Thought pattern recognition analysis. Think step by step:
        
        Step 1: Analyze day-of-week patterns using the provided percentages
        Step 2: Examine merchant frequency patterns using the provided merchant data
        Step 3: Review category distribution using the provided category frequencies
        Step 4: Assess spending velocity using the provided transaction frequency
        Step 5: Identify the most significant patterns with confidence scores
        
        Return ONLY valid JSON:
        {{
            "dominant_patterns": [
                {{
                    "pattern_type": "day_of_week|merchant|category|time|velocity",
                    "description": "Clear description of the pattern",
                    "supporting_numbers": ["specific numbers from provided data"],
                    "confidence_score": number_0_to_100,
                    "significance": "high|medium|low"
                }}
            ],
            "spending_personality": {{
                "type": "weekend_spender|weekday_focused|merchant_loyal|category_diverse|high_frequency|etc",
                "characteristics": ["characteristic1", "characteristic2"],
                "confidence": number_0_to_100
            }},
            "behavioral_insights": [
                {{
                    "insight": "behavioral observation",
                    "evidence": "numbers that support this",
                    "impact": "positive|negative|neutral"
                }}
            ]
        }}
        """

        return self.llm_client.query_financial_planner(
            content, system_role, return_json=True
        )

    def _cot_step3_contextual_insights(self, structured_data: Dict[str, Any], 
                                       pattern_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        CoT Step 3: Generate contextual insights based on user context and patterns.
        Focus: Personalized insights aligned with user goals and preferences
        """
        
        system_role = """
        You are a personalized financial insights specialist who generates meaningful
        observations based on user context and spending patterns.
        
        CRITICAL INSTRUCTIONS:
        1. Use ONLY the provided analyzed numbers and pattern data
        2. Reference the user's specific financial goals and context
        3. Generate insights that are factual and evidence-based
        4. Avoid giving advice - focus on observational insights
        5. Use Chain of Thought reasoning to connect patterns to user context
        
        INSIGHT CATEGORIES:
        - Goal alignment observations
        - Spending trigger pattern observations  
        - Financial habit observations
        - Timing and frequency observations
        - Category preference observations
        """

        content = f"""
        ANALYZED DATA: {structured_data['analyzed_numbers']}
        IDENTIFIED PATTERNS: {pattern_analysis}
        USER CONTEXT: {structured_data['user_context']}
        
        Generate contextual insights using Chain of Thought reasoning:
        
        Step 1: Consider user's financial goal and current spending patterns
        Step 2: Analyze how spending patterns align with or work against their goal
        Step 3: Observe patterns related to their impulse triggers
        Step 4: Note significant timing or frequency patterns
        Step 5: Generate factual, observational insights (not advice)
        
        Return ONLY valid JSON:
        {{
            "goal_alignment_insights": [
                {{
                    "observation": "factual observation about goal progress",
                    "supporting_data": "specific numbers from analysis",
                    "trend_direction": "positive|negative|neutral"
                }}
            ],
            "behavioral_observations": [
                {{
                    "behavior": "observed spending behavior",
                    "frequency_data": "actual frequency from data",
                    "context_relevance": "how this relates to user context"
                }}
            ],
            "timing_insights": [
                {{
                    "timing_pattern": "when user tends to spend",
                    "frequency_evidence": "supporting frequency data",
                    "potential_correlation": "possible connection to triggers/habits"
                }}
            ],
            "category_preferences": [
                {{
                    "category": "spending category",
                    "usage_frequency": "actual frequency from data",
                    "percentage_of_spending": "actual percentage"
                }}
            ]
        }}
        """

        return self.llm_client.query_financial_planner(
            content, system_role, return_json=True
        )

    def _cot_step4_trend_synthesis(self, structured_data: Dict[str, Any],
                                   pattern_analysis: Dict[str, Any],
                                   contextual_insights: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        CoT Step 4: Synthesize final trends with appropriate icons.
        Focus: Factual, observational trends using only provided data
        """
        
        system_role = """
        You are a financial trend synthesis specialist who creates factual,
        observational trend statements with appropriate icons.
        
        CRITICAL REQUIREMENTS:
        1. Use ONLY the provided analyzed numbers - no additional calculations
        2. Create observational statements, not advice
        3. Each trend must be under 100 characters
        4. Include appropriate emoji icons
        5. Focus on the most significant patterns identified
        6. Maximum 5 trends total
        
        TREND FORMATS:
        - "X% of purchases were made on [day pattern]"
        - "[Merchant] appears in X of your last Y transactions"
        - "[Category] represents X% of recent transactions"
        - "Transaction frequency averaged X per week"
        - "[Time] purchases account for X% of transactions"
        
        ICON GUIDELINES:
        📊 - General statistics
        📅 - Day/time patterns  
        🛒 - Merchant/shopping
        🍽️ - Food & dining
        🚗 - Transportation
        ⏰ - Time-based patterns
        📈 - Frequency/trends
        """

        content = f"""
        ANALYZED NUMBERS: {structured_data['analyzed_numbers']}
        IDENTIFIED PATTERNS: {pattern_analysis}
        CONTEXTUAL INSIGHTS: {contextual_insights}
        
        Create final trend statements using Chain of Thought synthesis:
        
        Step 1: Identify the 5 most significant patterns from the analysis
        Step 2: Convert each pattern into a factual, observational statement
        Step 3: Use the exact numbers provided in the analyzed data
        Step 4: Select appropriate icons for each trend
        Step 5: Ensure each trend is under 100 characters and factual
        
        Focus on these data points:
        - Weekday vs weekend percentages: {structured_data['analyzed_numbers']['weekday_percentage']}% vs {structured_data['analyzed_numbers']['weekend_percentage']}%
        - Top merchants: {structured_data['analyzed_numbers']['top_merchants']}
        - Category frequencies: {structured_data['analyzed_numbers']['category_frequencies']}
        - Evening percentage: {structured_data['analyzed_numbers']['evening_percentage']}%
        - Transaction velocity: {structured_data['analyzed_numbers']['spending_velocity_per_week']} per week
        
        Return ONLY valid JSON array:
        [
            {{
                "icon": "emoji",
                "trend": "factual observational statement under 100 chars"
            }}
        ]
        """

        response = self.llm_client.query_financial_planner(
            content, system_role, return_json=True
        )
        
        # Handle different response formats
        if isinstance(response, list):
            return response[:5]  # Limit to 5 trends
        elif isinstance(response, dict) and "trends" in response:
            return response["trends"][:5]
        else:
            # Fallback to basic data-driven trends if LLM response is invalid
            return self._generate_fallback_trends(structured_data)

    def _generate_fallback_trends(self, structured_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate fallback trends if LLM fails."""
        analyzed = structured_data["analyzed_numbers"]
        trends = []
        
        # Day pattern trend
        if analyzed["weekday_percentage"] > analyzed["weekend_percentage"]:
            trends.append({
                "icon": "📊",
                "trend": f"{analyzed['weekday_percentage']:.0f}% of purchases on weekdays vs {analyzed['weekend_percentage']:.0f}% weekends."
            })
        
        # Top merchant trend
        if analyzed["top_merchants"]:
            top_merchant, count = list(analyzed["top_merchants"].items())[0]
            trends.append({
                "icon": "🛒",
                "trend": f"{top_merchant} appears in {count} of last {analyzed['total_transactions']} transactions."
            })
        
        # Category trend
        if analyzed["category_frequencies"]:
            top_cat, count = max(analyzed["category_frequencies"].items(), key=lambda x: x[1])
            pct = (count / analyzed["total_transactions"] * 100) if analyzed["total_transactions"] > 0 else 0
            trends.append({
                "icon": "📈",
                "trend": f"{top_cat} represents {pct:.0f}% of transactions ({count} of {analyzed['total_transactions']})."
            })
        
        return trends[:5]

    def _calculate_concentration(self, amounts: List[float]) -> float:
        """Calculate spending concentration using Gini coefficient approx."""
        if not amounts or len(amounts) < 2:
            return 0.0
            
        amounts = sorted([a for a in amounts if a > 0])
        n = len(amounts)
        
        if n == 0:
            return 0.0
        
        # Simplified Gini coefficient calculation
        total = sum(amounts)
        if total == 0:
            return 0.0
            
        cumulative = 0
        weighted_sum = 0
        
        for i, amount in enumerate(amounts):
            cumulative += amount
            weighted_sum += cumulative
            
        gini = (2 * weighted_sum) / (n * total) - (n + 1) / n
        return max(0.0, min(1.0, gini))

    def _log_cot_step(self, step_description: str):
        """Log Chain of Thoughts steps for transparency."""
        self.cot_trace.append({
            "timestamp": datetime.now().isoformat(),
            "step": len(self.cot_trace) + 1,
            "description": step_description
        })
        print(f"🧠 CoT Step {len(self.cot_trace)}: {step_description}")

    def get_cot_trace(self) -> List[Dict[str, Any]]:
        """Return Chain of Thoughts execution trace for debugging."""
        return self.cot_trace 