"""
Base Trend Analysis Agent

Defines the interface and common functionality for all trend analysis agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
from datetime import datetime


class BaseTrendAgent(ABC):
    """
    Abstract base class for trend analysis agents.
    
    Provides common interface for analyzing user spending patterns
    and generating personalized trend insights.
    """

    def __init__(self, user_preferences: Dict[str, Any], 
                 spending_data: Dict[str, Any],
                 transaction_history: List[Dict[str, Any]]):
        """
        Initialize the trend analysis agent.
        
        Args:
            user_preferences: User profile and preferences
            spending_data: Current spending analysis results
            transaction_history: Historical transaction data
        """
        self.user_preferences = user_preferences
        self.spending_data = spending_data
        self.transaction_history = transaction_history
        self.analysis_timestamp = datetime.now().isoformat()
        
    @abstractmethod
    def analyze_spending_trends(self) -> List[Dict[str, str]]:
        """
        Analyze spending trends and generate insights.
        
        Returns:
            List of trend insights with icons and descriptions
            Format: [{"icon": "📊", "trend": "description"}, ...]
        """
        pass
    
    def get_analysis_metadata(self) -> Dict[str, Any]:
        """Get metadata about the analysis."""
        return {
            "timestamp": self.analysis_timestamp,
            "user_data_points": len(self.transaction_history),
            "spending_categories": len(
                self.spending_data.get("category_analysis", {})
            ),
            "analysis_period": self._get_analysis_period()
        }
    
    def _get_analysis_period(self) -> Dict[str, str]:
        """Calculate the analysis period from transaction history."""
        if not self.transaction_history:
            return {"start": "N/A", "end": "N/A"}
            
        dates = [t.get("date") for t in self.transaction_history 
                 if t.get("date")]
        if not dates:
            return {"start": "N/A", "end": "N/A"}
            
        return {
            "start": min(dates),
            "end": max(dates)
        }
    
    def _categorize_spending_level(self, amount: float, 
                                   category_avg: float) -> str:
        """Categorize spending level relative to average."""
        if amount > category_avg * 1.5:
            return "high"
        elif amount < category_avg * 0.5:
            return "low"
        else:
            return "normal"
    
    def _get_top_categories(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top spending categories."""
        category_analysis = self.spending_data.get("category_analysis", {})
        if not category_analysis:
            return []
            
        categories = [
            {
                "name": cat_name,
                "amount": cat_data.get("total_amount", 0),
                "percentage": cat_data.get("percentage", 0)
            }
            for cat_name, cat_data in category_analysis.items()
        ]
        
        return sorted(categories, 
                      key=lambda x: x["amount"], reverse=True)[:limit] 