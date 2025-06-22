"""
Plaid Transaction Agent for Noumi
Concrete implementation of transaction analysis using Plaid data.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import statistics
from collections import defaultdict

from .base_transaction_agent import BaseTransactionAgent
from ..utils.llm_client import NoumiLLMClient


class PlaidTransactionAgent(BaseTransactionAgent):
    """
    Concrete implementation for analyzing Plaid transaction data.
    """

    def __init__(self, user_id: str, transactions_data: List[Dict],
                 llm_client: Optional[NoumiLLMClient] = None):
        super().__init__(user_id, transactions_data)
        self.llm_client = llm_client or NoumiLLMClient(provider="google")
        self.processed_data = None

    def analyze_spending_patterns(self) -> Dict[str, Any]:
        """
        Analyze user spending patterns from Plaid transaction data.
        """
        if not self.processed_data:
            self.processed_data = self.preprocess_transactions()

        patterns = {
            'monthly_analysis': self._analyze_monthly_patterns(),
            'category_analysis': self._analyze_category_patterns(),
            'merchant_analysis': self._analyze_merchant_patterns(),
            'timing_analysis': self._analyze_timing_patterns(),
            'frequency_analysis': self._analyze_frequency_patterns()
        }

        # Use LLM for advanced pattern recognition
        llm_analysis = self.llm_client.analyze_transactions_with_llm(
            self.transactions_data,
            {'user_id': self.user_id}
        )

        patterns['ai_insights'] = llm_analysis
        self.spending_patterns = patterns
        return patterns

    def identify_saving_opportunities(self) -> Dict[str, Any]:
        """
        Identify potential areas for cost savings.
        """
        if not self.spending_patterns:
            self.analyze_spending_patterns()

        opportunities = {
            'subscription_optimization': self._find_subscription_opportunities(),
            'category_optimization': self._find_category_opportunities(),
            'merchant_optimization': self._find_merchant_opportunities(),
            'timing_optimization': self._find_timing_opportunities(),
            'frequency_optimization': self._find_frequency_opportunities()
        }

        # Calculate potential savings amounts
        total_potential_savings = sum(
            opp.get('potential_monthly_savings', 0)
            for opp_category in opportunities.values()
            for opp in (opp_category if isinstance(opp_category, list)
                       else [opp_category])
        )

        opportunities['total_potential_monthly_savings'] = \
            total_potential_savings
        return opportunities

    def _analyze_monthly_patterns(self) -> Dict[str, Any]:
        """Analyze monthly spending patterns."""
        monthly_data = defaultdict(lambda: {'total': 0, 'count': 0})

        for transaction in self.transactions_data:
            date_str = transaction.get('date', '')
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                amount = abs(transaction.get('amount', 0))
                monthly_data[month_key]['total'] += amount
                monthly_data[month_key]['count'] += 1
            except ValueError:
                continue

        # Calculate averages and trends
        monthly_totals = [data['total'] for data in monthly_data.values()]
        avg_monthly_spending = statistics.mean(monthly_totals) if \
            monthly_totals else 0

        return {
            'monthly_breakdown': dict(monthly_data),
            'average_monthly_spending': avg_monthly_spending,
            'spending_trend': self._calculate_trend(monthly_totals)
        }

    def _analyze_category_patterns(self) -> Dict[str, Any]:
        """Analyze spending by category."""
        category_data = self.processed_data.get('categories', {})

        # Calculate percentages
        total_spending = sum(
            cat_data['total_amount'] for cat_data in category_data.values()
        )

        category_analysis = {}
        for category, data in category_data.items():
            percentage = (data['total_amount'] / total_spending * 100) if \
                total_spending > 0 else 0
            avg_transaction = data['total_amount'] / data['count'] if \
                data['count'] > 0 else 0

            category_analysis[category] = {
                'total_amount': data['total_amount'],
                'transaction_count': data['count'],
                'percentage_of_total': percentage,
                'average_transaction_amount': avg_transaction
            }

        return category_analysis

    def _analyze_merchant_patterns(self) -> Dict[str, Any]:
        """Analyze spending by merchant."""
        merchant_data = defaultdict(lambda: {'total': 0, 'count': 0})

        for transaction in self.transactions_data:
            merchant = transaction.get('merchant_name') or \
                transaction.get('name', 'Unknown')
            amount = abs(transaction.get('amount', 0))
            merchant_data[merchant]['total'] += amount
            merchant_data[merchant]['count'] += 1

        # Sort by total spending
        sorted_merchants = sorted(
            merchant_data.items(),
            key=lambda x: x[1]['total'],
            reverse=True
        )

        return {
            'top_merchants': sorted_merchants[:10],
            'total_merchants': len(merchant_data)
        }

    def _analyze_timing_patterns(self) -> Dict[str, Any]:
        """Analyze spending timing patterns."""
        weekday_spending = defaultdict(lambda: {'total': 0, 'count': 0})
        hour_spending = defaultdict(lambda: {'total': 0, 'count': 0})

        for transaction in self.transactions_data:
            date_str = transaction.get('date', '')
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                weekday = date_obj.strftime('%A')
                amount = abs(transaction.get('amount', 0))

                weekday_spending[weekday]['total'] += amount
                weekday_spending[weekday]['count'] += 1

                # If authorized_datetime is available
                auth_datetime = transaction.get('authorized_datetime')
                if auth_datetime:
                    try:
                        auth_obj = datetime.fromisoformat(
                            auth_datetime.replace('Z', '+00:00')
                        )
                        hour = auth_obj.hour
                        hour_spending[hour]['total'] += amount
                        hour_spending[hour]['count'] += 1
                    except ValueError:
                        pass

            except ValueError:
                continue

        return {
            'weekday_patterns': dict(weekday_spending),
            'hourly_patterns': dict(hour_spending)
        }

    def _analyze_frequency_patterns(self) -> Dict[str, Any]:
        """Analyze transaction frequency patterns."""
        # Group by merchant and category to find recurring transactions
        recurring_transactions = defaultdict(list)

        for transaction in self.transactions_data:
            merchant = transaction.get('merchant_name') or \
                transaction.get('name', 'Unknown')
            amount = abs(transaction.get('amount', 0))
            category = transaction.get('category', ['Other'])[0] if \
                isinstance(transaction.get('category'), list) else 'Other'

            key = f"{merchant}_{category}_{amount}"
            recurring_transactions[key].append(transaction)

        # Identify potentially recurring transactions (3+ occurrences)
        recurring = {
            key: transactions for key, transactions in
            recurring_transactions.items()
            if len(transactions) >= 3
        }

        return {
            'recurring_transactions': len(recurring),
            'recurring_details': {
                key: {
                    'count': len(transactions),
                    'total_amount': sum(abs(t.get('amount', 0))
                                       for t in transactions),
                    'frequency_days': self._calculate_frequency(transactions)
                }
                for key, transactions in recurring.items()
            }
        }

    def _find_subscription_opportunities(self) -> List[Dict[str, Any]]:
        """Find subscription optimization opportunities."""
        opportunities = []

        # Look for recurring transactions that might be subscriptions
        if self.spending_patterns and \
                'frequency_analysis' in self.spending_patterns:
            recurring = self.spending_patterns['frequency_analysis'].get(
                'recurring_details', {}
            )

            for key, details in recurring.items():
                # Subscriptions typically have regular frequency
                freq_days = details.get('frequency_days', 0)
                if 25 <= freq_days <= 35:  # Monthly subscriptions
                    merchant_info = key.split('_')
                    opportunities.append({
                        'type': 'subscription',
                        'merchant': merchant_info[0],
                        'monthly_cost': details['total_amount'] /
                        details['count'] if details['count'] > 0 else 0,
                        'opportunity': 'Review subscription necessity',
                        'potential_monthly_savings': details['total_amount'] /
                        details['count'] * 0.3 if details['count'] > 0 else 0
                    })

        return opportunities

    def _find_category_opportunities(self) -> List[Dict[str, Any]]:
        """Find category-based saving opportunities."""
        opportunities = []

        if self.spending_patterns and \
                'category_analysis' in self.spending_patterns:
            categories = self.spending_patterns['category_analysis']

            # Target high-percentage categories for optimization
            for category, data in categories.items():
                if data['percentage_of_total'] > 15:  # High spending category
                    opportunities.append({
                        'type': 'category_optimization',
                        'category': category,
                        'current_monthly_spending': data['total_amount'],
                        'opportunity': f'Reduce {category} spending by 10-20%',
                        'potential_monthly_savings': data['total_amount'] * 0.15
                    })

        return opportunities

    def _find_merchant_opportunities(self) -> List[Dict[str, Any]]:
        """Find merchant-based saving opportunities."""
        opportunities = []

        if self.spending_patterns and \
                'merchant_analysis' in self.spending_patterns:
            top_merchants = self.spending_patterns['merchant_analysis'].get(
                'top_merchants', []
            )

            # Focus on top spending merchants
            for merchant, data in top_merchants[:5]:
                opportunities.append({
                    'type': 'merchant_optimization',
                    'merchant': merchant,
                    'total_spending': data['total'],
                    'transaction_count': data['count'],
                    'opportunity': 'Find alternatives or negotiate better rates',
                    'potential_monthly_savings': data['total'] * 0.1
                })

        return opportunities

    def _find_timing_opportunities(self) -> List[Dict[str, Any]]:
        """Find timing-based saving opportunities."""
        opportunities = []

        if self.spending_patterns and \
                'timing_analysis' in self.spending_patterns:
            weekday_patterns = self.spending_patterns['timing_analysis'].get(
                'weekday_patterns', {}
            )

            # Find high-spending days
            max_spending_day = max(
                weekday_patterns.items(),
                key=lambda x: x[1]['total'],
                default=('Unknown', {'total': 0})
            )

            if max_spending_day[1]['total'] > 0:
                opportunities.append({
                    'type': 'timing_optimization',
                    'high_spending_day': max_spending_day[0],
                    'amount': max_spending_day[1]['total'],
                    'opportunity': 'Be more mindful of spending on this day',
                    'potential_monthly_savings': max_spending_day[1]['total'] *
                    0.2
                })

        return opportunities

    def _find_frequency_opportunities(self) -> List[Dict[str, Any]]:
        """Find frequency-based saving opportunities."""
        opportunities = []

        if self.spending_patterns and \
                'frequency_analysis' in self.spending_patterns:
            recurring_count = self.spending_patterns['frequency_analysis'].get(
                'recurring_transactions', 0
            )

            if recurring_count > 5:
                opportunities.append({
                    'type': 'frequency_optimization',
                    'recurring_count': recurring_count,
                    'opportunity': 'Review and consolidate recurring payments',
                    'potential_monthly_savings': recurring_count * 5  # Estimate
                })

        return opportunities

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate spending trend from values."""
        if len(values) < 2:
            return 'insufficient_data'

        recent_avg = statistics.mean(values[-3:]) if len(values) >= 3 \
            else values[-1]
        older_avg = statistics.mean(values[:-3]) if len(values) >= 3 \
            else values[0]

        if recent_avg > older_avg * 1.1:
            return 'increasing'
        elif recent_avg < older_avg * 0.9:
            return 'decreasing'
        else:
            return 'stable'

    def _calculate_frequency(self, transactions: List[Dict]) -> float:
        """Calculate average frequency in days between transactions."""
        if len(transactions) < 2:
            return 0

        dates = []
        for transaction in transactions:
            date_str = transaction.get('date', '')
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                dates.append(date_obj)
            except ValueError:
                continue

        if len(dates) < 2:
            return 0

        dates.sort()
        intervals = [
            (dates[i + 1] - dates[i]).days
            for i in range(len(dates) - 1)
        ]

        return statistics.mean(intervals) if intervals else 0 