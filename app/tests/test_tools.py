"""
Test suite for FAdvisor tools
"""
import pytest
from unittest.mock import Mock, patch
import pandas as pd
from app.tools.financial_tools import StockDataFetcher, PortfolioAnalyzer
from app.tools.agent_tools import (
    get_stock_info_tool,
    analyze_technical_tool,
    analyze_portfolio_tool,
    calculate_portfolio_allocation
)


class TestStockDataFetcher:
    """Test stock data fetching functionality"""
    
    @patch('yfinance.Ticker')
    def test_get_ticker_info(self, mock_ticker):
        """Test getting ticker information"""
        # Mock yfinance response
        mock_ticker.return_value.info = {
            "longName": "Apple Inc.",
            "sector": "Technology",
            "currentPrice": 150.0,
            "marketCap": 2500000000000,
            "trailingPE": 25.0
        }
        
        result = StockDataFetcher.get_ticker_info("AAPL")
        
        assert result["symbol"] == "AAPL"
        assert result["name"] == "Apple Inc."
        assert result["sector"] == "Technology"
        assert result["current_price"] == 150.0
    
    @patch('yfinance.Ticker')
    def test_get_price_history(self, mock_ticker):
        """Test getting price history"""
        # Create mock DataFrame
        mock_df = pd.DataFrame({
            'Open': [100, 101, 102],
            'High': [101, 102, 103],
            'Low': [99, 100, 101],
            'Close': [100.5, 101.5, 102.5],
            'Volume': [1000000, 1100000, 1200000]
        })
        mock_ticker.return_value.history.return_value = mock_df
        
        result = StockDataFetcher.get_price_history("AAPL", "1mo")
        
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert len(result) == 3


class TestPortfolioAnalyzer:
    """Test portfolio analysis functionality"""
    
    @patch('app.tools.financial_tools.StockDataFetcher.get_ticker_info')
    @patch('app.tools.financial_tools.StockDataFetcher.get_technical_indicators')
    def test_analyze_portfolio(self, mock_technical, mock_info):
        """Test portfolio analysis"""
        # Mock responses
        mock_info.return_value = {
            "current_price": 150.0,
            "name": "Apple Inc.",
            "sector": "Technology"
        }
        mock_technical.return_value = {
            "trend": "uptrend",
            "momentum": "bullish"
        }
        
        holdings = [
            {"symbol": "AAPL", "quantity": 10, "purchase_price": 140.0}
        ]
        
        result = PortfolioAnalyzer.analyze_portfolio(holdings)
        
        assert "total_value" in result
        assert "total_cost" in result
        assert "total_return" in result
        assert "holdings" in result
        assert len(result["holdings"]) == 1


class TestAgentTools:
    """Test agent tool wrappers"""
    
    @patch('app.tools.financial_tools.StockDataFetcher.get_ticker_info')
    def test_get_stock_info_tool(self, mock_get_info):
        """Test stock info tool"""
        mock_get_info.return_value = {"symbol": "AAPL", "price": 150.0}
        
        result = get_stock_info_tool("AAPL")
        
        assert result["symbol"] == "AAPL"
        assert "price" in result
        mock_get_info.assert_called_once_with("AAPL")
    
    @patch('app.tools.financial_tools.StockDataFetcher.get_technical_indicators')
    def test_analyze_technical_tool(self, mock_technical):
        """Test technical analysis tool"""
        mock_technical.return_value = {
            "symbol": "AAPL",
            "rsi": 65.0,
            "trend": "uptrend"
        }
        
        result = analyze_technical_tool("AAPL", "3mo")
        
        assert result["symbol"] == "AAPL"
        assert "rsi" in result
        assert result["trend"] == "uptrend"
    
    def test_calculate_portfolio_allocation(self):
        """Test portfolio allocation calculation"""
        result = calculate_portfolio_allocation(
            total_investment=10000,
            risk_tolerance="moderate",
            investment_goals=["growth"]
        )
        
        assert result["risk_profile"] == "moderate"
        assert "stocks" in result["allocation_percentages"]
        assert "bonds" in result["allocation_percentages"]
        assert sum(result["allocation_percentages"].values()) == 100