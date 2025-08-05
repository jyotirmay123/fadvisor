"""
Financial analysis tools for the FAdvisor agent
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import ta  # Technical analysis library
import yfinance as yf

logger = logging.getLogger(__name__)


class StockDataFetcher:
    """Fetch and analyze stock data"""

    @staticmethod
    def get_ticker_info(symbol: str) -> dict[str, Any]:
        """Get basic information about a stock"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                "symbol": symbol,
                "name": info.get("longName", "Unknown"),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "market_cap": info.get("marketCap", 0),
                "currency": info.get("currency", "USD"),
                "exchange": info.get("exchange", "Unknown"),
                "current_price": info.get(
                    "currentPrice", info.get("regularMarketPrice", 0)
                ),
                "previous_close": info.get("previousClose", 0),
                "volume": info.get("volume", 0),
                "average_volume": info.get("averageVolume", 0),
                "52_week_high": info.get("fiftyTwoWeekHigh", 0),
                "52_week_low": info.get("fiftyTwoWeekLow", 0),
                "pe_ratio": info.get("trailingPE", 0),
                "forward_pe": info.get("forwardPE", 0),
                "dividend_yield": info.get("dividendYield", 0),
                "beta": info.get("beta", 0),
                "eps": info.get("trailingEps", 0),
                "revenue": info.get("totalRevenue", 0),
                "profit_margin": info.get("profitMargins", 0),
                "operating_margin": info.get("operatingMargins", 0),
                "roe": info.get("returnOnEquity", 0),
                "debt_to_equity": info.get("debtToEquity", 0),
                "free_cashflow": info.get("freeCashflow", 0),
                "recommendation": info.get("recommendationKey", "none"),
            }
        except Exception as e:
            logger.error(f"Error fetching ticker info for {symbol}: {e}")
            return {"symbol": symbol, "error": str(e)}

    @staticmethod
    def get_price_history(
        symbol: str, period: str = "1y", interval: str = "1d"
    ) -> pd.DataFrame:
        """Get historical price data"""
        try:
            ticker = yf.Ticker(symbol)
            history = ticker.history(period=period, interval=interval)
            return history
        except Exception as e:
            logger.error(f"Error fetching price history for {symbol}: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_technical_indicators(symbol: str, period: str = "3mo") -> dict[str, Any]:
        """Calculate technical indicators"""
        try:
            history = StockDataFetcher.get_price_history(symbol, period)
            if history.empty:
                return {"error": "No data available"}

            close = history["Close"]
            high = history["High"]
            low = history["Low"]
            volume = history["Volume"]

            indicators = {
                "symbol": symbol,
                "current_price": close.iloc[-1],
                "price_change_pct": ((close.iloc[-1] - close.iloc[0]) / close.iloc[0])
                * 100,
                # Moving averages
                "sma_20": ta.trend.sma_indicator(close, window=20).iloc[-1],
                "sma_50": ta.trend.sma_indicator(close, window=50).iloc[-1]
                if len(close) >= 50
                else None,
                "ema_20": ta.trend.ema_indicator(close, window=20).iloc[-1],
                # RSI
                "rsi": ta.momentum.rsi(close, window=14).iloc[-1],
                # MACD
                "macd": ta.trend.macd_diff(close).iloc[-1],
                "macd_signal": ta.trend.macd_signal(close).iloc[-1],
                # Bollinger Bands
                "bb_high": ta.volatility.bollinger_hband(close).iloc[-1],
                "bb_low": ta.volatility.bollinger_lband(close).iloc[-1],
                "bb_mid": ta.volatility.bollinger_mavg(close).iloc[-1],
                # Volume indicators
                "volume_sma": ta.volume.volume_weighted_average_price(
                    high, low, close, volume
                ).iloc[-1],
                "volume_trend": "increasing"
                if volume.iloc[-5:].mean() > volume.iloc[-20:-5].mean()
                else "decreasing",
                # Volatility
                "atr": ta.volatility.average_true_range(high, low, close).iloc[-1],
                "volatility": close.pct_change().std()
                * np.sqrt(252)
                * 100,  # Annualized volatility
                # Support and Resistance
                "support": low.iloc[-20:].min(),
                "resistance": high.iloc[-20:].max(),
            }

            # Add trend analysis
            indicators["trend"] = StockDataFetcher._analyze_trend(close)
            indicators["momentum"] = StockDataFetcher._analyze_momentum(indicators)

            return indicators

        except Exception as e:
            logger.error(f"Error calculating technical indicators for {symbol}: {e}")
            return {"symbol": symbol, "error": str(e)}

    @staticmethod
    def _analyze_trend(prices: pd.Series) -> str:
        """Analyze price trend"""
        sma_short = ta.trend.sma_indicator(prices, window=10).iloc[-1]
        sma_long = ta.trend.sma_indicator(prices, window=30).iloc[-1]

        if sma_short > sma_long * 1.02:
            return "strong_uptrend"
        elif sma_short > sma_long:
            return "uptrend"
        elif sma_short < sma_long * 0.98:
            return "strong_downtrend"
        elif sma_short < sma_long:
            return "downtrend"
        else:
            return "sideways"

    @staticmethod
    def _analyze_momentum(indicators: dict[str, Any]) -> str:
        """Analyze momentum indicators"""
        rsi = indicators.get("rsi", 50)
        macd = indicators.get("macd", 0)

        if rsi > 70 and macd > 0:
            return "overbought"
        elif rsi < 30 and macd < 0:
            return "oversold"
        elif rsi > 60 and macd > 0:
            return "bullish"
        elif rsi < 40 and macd < 0:
            return "bearish"
        else:
            return "neutral"


class PortfolioAnalyzer:
    """Analyze portfolio performance and provide recommendations"""

    @staticmethod
    def analyze_portfolio(holdings: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Analyze a portfolio of holdings
        holdings: List of dicts with keys: symbol, quantity, purchase_price
        """
        portfolio_data = []
        total_value = 0
        total_cost = 0

        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_holding = {
                executor.submit(PortfolioAnalyzer._analyze_holding, holding): holding
                for holding in holdings
            }

            for future in as_completed(future_to_holding):
                result = future.result()
                if result:
                    portfolio_data.append(result)
                    total_value += result["current_value"]
                    total_cost += result["cost_basis"]

        # Calculate portfolio metrics
        portfolio_return = (
            ((total_value - total_cost) / total_cost) * 100 if total_cost > 0 else 0
        )

        # Sector allocation
        sector_allocation = {}
        for holding in portfolio_data:
            sector = holding.get("sector", "Unknown")
            if sector not in sector_allocation:
                sector_allocation[sector] = 0
            sector_allocation[sector] += holding["current_value"]

        # Convert to percentages
        for sector in sector_allocation:
            sector_allocation[sector] = (sector_allocation[sector] / total_value) * 100

        return {
            "total_value": total_value,
            "total_cost": total_cost,
            "total_return": portfolio_return,
            "holdings": portfolio_data,
            "sector_allocation": sector_allocation,
            "recommendations": PortfolioAnalyzer._generate_recommendations(
                portfolio_data, sector_allocation
            ),
        }

    @staticmethod
    def _analyze_holding(holding: dict[str, Any]) -> dict[str, Any] | None:
        """Analyze individual holding"""
        try:
            symbol = holding["symbol"]
            quantity = holding["quantity"]
            purchase_price = holding["purchase_price"]

            # Get current data
            info = StockDataFetcher.get_ticker_info(symbol)
            technical = StockDataFetcher.get_technical_indicators(symbol)

            current_price = info.get("current_price", 0)
            current_value = current_price * quantity
            cost_basis = purchase_price * quantity

            return {
                "symbol": symbol,
                "name": info.get("name", symbol),
                "sector": info.get("sector", "Unknown"),
                "quantity": quantity,
                "purchase_price": purchase_price,
                "current_price": current_price,
                "cost_basis": cost_basis,
                "current_value": current_value,
                "gain_loss": current_value - cost_basis,
                "gain_loss_pct": ((current_value - cost_basis) / cost_basis) * 100
                if cost_basis > 0
                else 0,
                "portfolio_weight": 0,  # Will be calculated later
                "technical_indicators": technical,
                "recommendation": info.get("recommendation", "none"),
                "trend": technical.get("trend", "unknown"),
                "momentum": technical.get("momentum", "neutral"),
            }
        except Exception as e:
            logger.error(f"Error analyzing holding {holding}: {e}")
            return None

    @staticmethod
    def _generate_recommendations(
        holdings: list[dict[str, Any]], sector_allocation: dict[str, float]
    ) -> list[str]:
        """Generate portfolio recommendations"""
        recommendations = []

        # Check sector concentration
        for sector, allocation in sector_allocation.items():
            if allocation > 30:
                recommendations.append(
                    f"High concentration in {sector} sector ({allocation:.1f}%). Consider diversification."
                )

        # Check individual holdings
        for holding in holdings:
            symbol = holding["symbol"]
            gain_loss_pct = holding["gain_loss_pct"]
            momentum = holding.get("technical_indicators", {}).get(
                "momentum", "neutral"
            )
            trend = holding.get("technical_indicators", {}).get("trend", "unknown")

            # Profit taking recommendations
            if gain_loss_pct > 50 and momentum == "overbought":
                recommendations.append(
                    f"{symbol}: Consider taking partial profits (up {gain_loss_pct:.1f}%, overbought)"
                )

            # Stop loss recommendations
            elif gain_loss_pct < -20 and trend in ["downtrend", "strong_downtrend"]:
                recommendations.append(
                    f"{symbol}: Consider stop loss (down {abs(gain_loss_pct):.1f}%, downtrend)"
                )

            # Buy more recommendations
            elif momentum == "oversold" and trend == "uptrend":
                recommendations.append(
                    f"{symbol}: Potential buying opportunity (oversold in uptrend)"
                )

        return recommendations


class MarketAnalyzer:
    """Analyze market conditions and trends"""

    @staticmethod
    def get_market_overview() -> dict[str, Any]:
        """Get overview of major market indices"""
        indices = {
            "^GSPC": "S&P 500",
            "^DJI": "Dow Jones",
            "^IXIC": "NASDAQ",
            "^VIX": "VIX (Volatility)",
            "^TNX": "10-Year Treasury Yield",
        }

        market_data = {}
        for symbol, name in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                history = ticker.history(period="1d")

                if not history.empty:
                    market_data[name] = {
                        "symbol": symbol,
                        "current": history["Close"].iloc[-1],
                        "change": history["Close"].iloc[-1] - history["Open"].iloc[0],
                        "change_pct": (
                            (history["Close"].iloc[-1] - history["Open"].iloc[0])
                            / history["Open"].iloc[0]
                        )
                        * 100,
                    }
            except Exception as e:
                logger.error(f"Error fetching market data for {symbol}: {e}")

        # Add market sentiment
        vix = market_data.get("VIX (Volatility)", {}).get("current", 20)
        if vix < 15:
            sentiment = "Low volatility - Bullish"
        elif vix < 25:
            sentiment = "Normal volatility - Neutral"
        else:
            sentiment = "High volatility - Bearish"

        return {
            "indices": market_data,
            "market_sentiment": sentiment,
            "timestamp": datetime.now().isoformat(),
        }
