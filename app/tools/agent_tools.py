"""
Agent tools for Google ADK integration
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from google.adk.tools import BaseTool

from app.tools.financial_tools import (
    MarketAnalyzer,
    PortfolioAnalyzer,
    StockDataFetcher,
)
from app.tools.news_tools import NewsAnalyzer

logger = logging.getLogger(__name__)


def get_stock_info_tool(symbol: str) -> dict[str, Any]:
    """
    Get comprehensive information about a stock.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')

    Returns:
        Dictionary containing stock information including price, fundamentals, and metrics
    """
    try:
        return StockDataFetcher.get_ticker_info(symbol.upper())
    except Exception as e:
        logger.error(f"Error in get_stock_info_tool: {e}")
        return {"error": str(e), "symbol": symbol}


def analyze_technical_tool(symbol: str, period: str = "3mo") -> dict[str, Any]:
    """
    Perform technical analysis on a stock.

    Args:
        symbol: Stock ticker symbol
        period: Analysis period ('1mo', '3mo', '6mo', '1y')

    Returns:
        Dictionary containing technical indicators and trend analysis
    """
    try:
        return StockDataFetcher.get_technical_indicators(symbol.upper(), period)
    except Exception as e:
        logger.error(f"Error in analyze_technical_tool: {e}")
        return {"error": str(e), "symbol": symbol}


def analyze_portfolio_tool(holdings: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Analyze a portfolio of stock holdings.

    Args:
        holdings: List of holdings, each containing:
            - symbol: Stock ticker
            - quantity: Number of shares
            - purchase_price: Price per share at purchase

    Returns:
        Portfolio analysis including performance, allocation, and recommendations
    """
    try:
        # Validate holdings format
        for holding in holdings:
            if not all(
                key in holding for key in ["symbol", "quantity", "purchase_price"]
            ):
                return {
                    "error": "Each holding must have symbol, quantity, and purchase_price"
                }

        return PortfolioAnalyzer.analyze_portfolio(holdings)
    except Exception as e:
        logger.error(f"Error in analyze_portfolio_tool: {e}")
        return {"error": str(e)}


def get_market_overview_tool() -> dict[str, Any]:
    """
    Get current market overview including major indices and sentiment.

    Returns:
        Dictionary containing market indices data and overall sentiment
    """
    try:
        return MarketAnalyzer.get_market_overview()
    except Exception as e:
        logger.error(f"Error in get_market_overview_tool: {e}")
        return {"error": str(e)}


def get_company_news_tool(symbol: str, days: int = 7) -> dict[str, Any]:
    """
    Get recent news and sentiment analysis for a company.

    Args:
        symbol: Stock ticker symbol
        days: Number of days to look back for news (default: 7)

    Returns:
        Dictionary containing news items and sentiment summary
    """
    try:
        # Run async function in sync context
        analyzer = NewsAnalyzer()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        news_items = loop.run_until_complete(
            analyzer.get_company_news(symbol.upper(), days)
        )

        sentiment_summary = analyzer.summarize_news_sentiment(news_items)

        return {
            "symbol": symbol,
            "news_items": news_items,
            "sentiment_summary": sentiment_summary,
        }
    except Exception as e:
        logger.error(f"Error in get_company_news_tool: {e}")
        return {"error": str(e), "symbol": symbol}
    finally:
        loop.close()


# Helper functions for complex analysis


def find_investment_opportunities(
    market_cap_range: tuple | None = None,
    sectors: list[str] | None = None,
    min_dividend_yield: float | None = None,
) -> list[dict[str, Any]]:
    """
    Find investment opportunities based on criteria.

    Args:
        market_cap_range: Tuple of (min, max) market cap in billions
        sectors: List of sectors to filter
        min_dividend_yield: Minimum dividend yield percentage

    Returns:
        List of potential investment opportunities
    """
    # This is a placeholder - in production, this would query a database
    # or API to find stocks matching criteria
    return [
        {
            "symbol": "EXAMPLE",
            "name": "Example Stock",
            "reason": "Matches your investment criteria",
            "metrics": {"market_cap": 100e9, "dividend_yield": 2.5, "pe_ratio": 15},
        }
    ]


def calculate_portfolio_allocation(
    total_investment: float, risk_tolerance: str, investment_goals: list[str]
) -> dict[str, Any]:
    """
    Calculate recommended portfolio allocation.

    Args:
        total_investment: Total amount to invest
        risk_tolerance: 'conservative', 'moderate', 'aggressive'
        investment_goals: List of goals like 'growth', 'income', 'preservation'

    Returns:
        Recommended allocation across asset classes
    """
    # Basic allocation strategies
    allocations = {
        "conservative": {"stocks": 30, "bonds": 60, "cash": 10},
        "moderate": {"stocks": 60, "bonds": 30, "cash": 10},
        "aggressive": {"stocks": 80, "bonds": 15, "cash": 5},
    }

    base_allocation = allocations.get(risk_tolerance, allocations["moderate"])

    # Adjust based on goals
    if "growth" in investment_goals:
        base_allocation["stocks"] += 10
        base_allocation["bonds"] -= 10
    elif "income" in investment_goals:
        base_allocation["bonds"] += 10
        base_allocation["stocks"] -= 10

    # Calculate dollar amounts
    return {
        "risk_profile": risk_tolerance,
        "goals": investment_goals,
        "allocation_percentages": base_allocation,
        "allocation_amounts": {
            asset: (pct / 100) * total_investment
            for asset, pct in base_allocation.items()
        },
        "recommendations": [
            "Diversify within each asset class",
            "Rebalance quarterly",
            "Consider tax-advantaged accounts",
        ],
    }
