"""
Trend Analysis Agent Module

This module contains AI agents for analyzing user spending trends
and generating personalized insights using Chain of Thoughts methodology.
"""

from .base_trend_agent import BaseTrendAgent
from .chain_of_thoughts_trend_agent import ChainOfThoughtsTrendAgent

__all__ = [
    'BaseTrendAgent',
    'ChainOfThoughtsTrendAgent'
] 