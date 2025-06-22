from abc import ABC, abstractmethod
from typing import Dict, List, Any


class BaseQuizAgent(ABC):
    """
    Base class for quiz generation agents.
    Creates personalized quizzes to understand user preferences and goals.
    """

    def __init__(self, user_profile: Dict[str, Any] = None):
        self.user_profile = user_profile or {}
        self.quiz_questions = None
        self.quiz_results = None
        self.user_preferences = None

    @abstractmethod
    def generate_personalized_quiz(self) -> List[Dict[str, Any]]:
        """
        Generate personalized quiz questions based on user profile.
        Must be implemented by concrete classes.
        """
        pass

    @abstractmethod
    def analyze_quiz_responses(self, responses: Dict[str, Any]) -> \
            Dict[str, Any]:
        """
        Analyze quiz responses to extract user preferences and goals.
        Must be implemented by concrete classes.
        """
        pass

    def get_quiz_questions(self) -> List[Dict[str, Any]]:
        """Return generated quiz questions."""
        return self.quiz_questions

    def get_user_preferences(self) -> Dict[str, Any]:
        """Return analyzed user preferences from quiz."""
        return self.user_preferences 