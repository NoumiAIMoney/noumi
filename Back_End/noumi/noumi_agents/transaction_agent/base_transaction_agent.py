from abc import ABC, abstractmethod
from typing import Dict, List, Any


class BaseTransactionAgent(ABC):
    """
    Base class for transaction analysis agents.
    Analyzes Plaid transaction data to understand spending patterns.
    """

    def __init__(self, user_id: str, transactions_data: List[Dict]):
        self.user_id = user_id
        self.transactions_data = transactions_data
        self.spending_patterns = None
        self.category_analysis = None
        self.monthly_trends = None
        self.insights = None

    def preprocess_transactions(self) -> Dict[str, Any]:
        """
        Preprocess transaction data for analysis.
        Standardize formats, categorize, and clean data.
        """
        processed_data = {
            'total_transactions': len(self.transactions_data),
            'categories': {},
            'monthly_spending': {},
            'merchant_analysis': {}
        }

        for transaction in self.transactions_data:
            # Extract category information
            category = transaction.get('category', ['Other'])[0] if \
                isinstance(transaction.get('category'), list) else 'Other'
            amount = abs(transaction.get('amount', 0))

            if category not in processed_data['categories']:
                processed_data['categories'][category] = {
                    'total_amount': 0,
                    'count': 0,
                    'transactions': []
                }

            processed_data['categories'][category]['total_amount'] += amount
            processed_data['categories'][category]['count'] += 1
            processed_data['categories'][category]['transactions'].append(
                transaction
            )

        return processed_data

    @abstractmethod
    def analyze_spending_patterns(self) -> Dict[str, Any]:
        """
        Analyze user spending patterns from transaction data.
        Must be implemented by concrete classes.
        """
        pass

    @abstractmethod
    def identify_saving_opportunities(self) -> Dict[str, Any]:
        """
        Identify potential areas for cost savings.
        Must be implemented by concrete classes.
        """
        pass

    def get_spending_patterns(self) -> Dict[str, Any]:
        """Return analyzed spending patterns."""
        return self.spending_patterns

    def get_insights(self) -> Dict[str, Any]:
        """Return transaction insights."""
        return self.insights 