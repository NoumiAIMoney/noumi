from abc import ABC, abstractmethod
from typing import Dict, Any


class BasePlanningAgent(ABC):
    """
    Base class for financial planning agents.
    Generates personalized savings plans based on spending analysis.
    """

    def __init__(self, user_preferences: Dict[str, Any],
                 spending_analysis: Dict[str, Any]):
        self.user_preferences = user_preferences
        self.spending_analysis = spending_analysis
        self.savings_plan = None

    @abstractmethod
    def generate_weekly_plan(self) -> Dict[str, Any]:
        """
        Generate a weekly savings plan based on analysis and preferences.
        Must be implemented by concrete classes.
        """
        pass

    def get_savings_plan(self) -> Dict[str, Any]:
        """Return the generated savings plan."""
        return self.savings_plan 