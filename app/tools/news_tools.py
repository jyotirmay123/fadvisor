"""
News and sentiment analysis tools for FAdvisor
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp

from app.config import config

logger = logging.getLogger(__name__)


class NewsAnalyzer:
    """Analyze news and sentiment for stocks and markets"""

    def __init__(self):
        self.finnhub_key = config.FINNHUB_API_KEY
        self.news_api_key = config.NEWS_API_KEY

    async def get_company_news(
        self, symbol: str, days: int = 7
    ) -> list[dict[str, Any]]:
        """Get recent news for a specific company"""
        news_items = []

        # Try multiple sources
        if self.finnhub_key:
            finnhub_news = await self._get_finnhub_news(symbol, days)
            news_items.extend(finnhub_news)

        # Fallback to Yahoo Finance news (free)
        yahoo_news = await self._get_yahoo_news(symbol)
        news_items.extend(yahoo_news)

        # Sort by date and remove duplicates
        news_items = self._deduplicate_news(news_items)
        news_items.sort(key=lambda x: x.get("datetime", datetime.now()), reverse=True)

        return news_items[:10]  # Return top 10 most recent

    async def _get_finnhub_news(self, symbol: str, days: int) -> list[dict[str, Any]]:
        """Get news from Finnhub API"""
        if not self.finnhub_key:
            return []

        try:
            from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            to_date = datetime.now().strftime("%Y-%m-%d")

            url = f"https://finnhub.io/api/v1/company-news"
            params = {
                "symbol": symbol,
                "from": from_date,
                "to": to_date,
                "token": self.finnhub_key,
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [
                            {
                                "title": item.get("headline", ""),
                                "summary": item.get("summary", ""),
                                "url": item.get("url", ""),
                                "source": item.get("source", ""),
                                "datetime": datetime.fromtimestamp(
                                    item.get("datetime", 0)
                                ),
                                "sentiment": self._analyze_basic_sentiment(
                                    item.get("headline", "")
                                    + " "
                                    + item.get("summary", "")
                                ),
                            }
                            for item in data
                        ]
        except Exception as e:
            logger.error(f"Error fetching Finnhub news: {e}")

        return []

    async def _get_yahoo_news(self, symbol: str) -> list[dict[str, Any]]:
        """Get news from Yahoo Finance (using yfinance)"""
        try:
            import yfinance as yf

            ticker = yf.Ticker(symbol)
            news = ticker.news

            return [
                {
                    "title": item.get("title", ""),
                    "summary": item.get("summary", item.get("title", "")),
                    "url": item.get("link", ""),
                    "source": item.get("publisher", "Yahoo Finance"),
                    "datetime": datetime.fromtimestamp(
                        item.get("providerPublishTime", 0)
                    ),
                    "sentiment": self._analyze_basic_sentiment(
                        item.get("title", "")
                        + " "
                        + item.get("summary", item.get("title", ""))
                    ),
                }
                for item in news[:10]
            ]
        except Exception as e:
            logger.error(f"Error fetching Yahoo news: {e}")
            return []

    def _analyze_basic_sentiment(self, text: str) -> dict[str, Any]:
        """Basic sentiment analysis using keyword matching"""
        text_lower = text.lower()

        # Positive keywords
        positive_keywords = [
            "surge",
            "rally",
            "gain",
            "profit",
            "revenue",
            "beat",
            "upgrade",
            "positive",
            "growth",
            "expand",
            "increase",
            "breakthrough",
            "success",
            "outperform",
            "bullish",
            "optimistic",
            "strong",
            "record",
        ]

        # Negative keywords
        negative_keywords = [
            "loss",
            "decline",
            "fall",
            "drop",
            "miss",
            "downgrade",
            "negative",
            "concern",
            "risk",
            "weak",
            "bearish",
            "pessimistic",
            "warning",
            "lawsuit",
            "investigation",
            "recall",
            "bankruptcy",
            "layoff",
        ]

        positive_count = sum(1 for word in positive_keywords if word in text_lower)
        negative_count = sum(1 for word in negative_keywords if word in text_lower)

        # Calculate sentiment score
        total_keywords = positive_count + negative_count
        if total_keywords == 0:
            sentiment = "neutral"
            score = 0
        else:
            score = (positive_count - negative_count) / total_keywords
            if score > 0.3:
                sentiment = "positive"
            elif score < -0.3:
                sentiment = "negative"
            else:
                sentiment = "neutral"

        return {
            "sentiment": sentiment,
            "score": score,
            "positive_keywords": positive_count,
            "negative_keywords": negative_count,
        }

    def _deduplicate_news(
        self, news_items: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Remove duplicate news items based on title similarity"""
        unique_news = []
        seen_titles = set()

        for item in news_items:
            title = item.get("title", "").lower()
            # Simple deduplication by checking if first 50 chars are the same
            title_key = title[:50] if len(title) > 50 else title

            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_news.append(item)

        return unique_news

    async def get_market_news(self, category: str = "general") -> list[dict[str, Any]]:
        """Get general market news"""
        news_items = []

        # Categories mapping
        categories = {
            "general": ["business", "finance", "economy"],
            "crypto": ["cryptocurrency", "bitcoin", "blockchain"],
            "forex": ["forex", "currency", "dollar"],
            "commodities": ["commodities", "gold", "oil"],
        }

        search_terms = categories.get(category, ["business"])

        # Use NewsAPI if available
        if self.news_api_key:
            for term in search_terms:
                news = await self._get_newsapi_headlines(term)
                news_items.extend(news)

        # Sort by date
        news_items.sort(key=lambda x: x.get("datetime", datetime.now()), reverse=True)

        return news_items[:15]

    async def _get_newsapi_headlines(self, query: str) -> list[dict[str, Any]]:
        """Get headlines from NewsAPI"""
        if not self.news_api_key:
            return []

        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "apiKey": self.news_api_key,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 10,
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [
                            {
                                "title": article.get("title", ""),
                                "summary": article.get("description", ""),
                                "url": article.get("url", ""),
                                "source": article.get("source", {}).get("name", ""),
                                "datetime": datetime.fromisoformat(
                                    article.get("publishedAt", "").replace(
                                        "Z", "+00:00"
                                    )
                                ),
                                "sentiment": self._analyze_basic_sentiment(
                                    article.get("title", "")
                                    + " "
                                    + article.get("description", "")
                                ),
                            }
                            for article in data.get("articles", [])
                        ]
        except Exception as e:
            logger.error(f"Error fetching NewsAPI headlines: {e}")

        return []

    def summarize_news_sentiment(
        self, news_items: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Summarize overall sentiment from news items"""
        if not news_items:
            return {
                "overall_sentiment": "neutral",
                "sentiment_score": 0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
                "key_topics": [],
            }

        sentiments = {"positive": 0, "negative": 0, "neutral": 0}
        total_score = 0

        for item in news_items:
            sentiment_data = item.get("sentiment", {})
            sentiment = sentiment_data.get("sentiment", "neutral")
            sentiments[sentiment] += 1
            total_score += sentiment_data.get("score", 0)

        avg_score = total_score / len(news_items)

        # Determine overall sentiment
        if avg_score > 0.2:
            overall = "positive"
        elif avg_score < -0.2:
            overall = "negative"
        else:
            overall = "neutral"

        # Extract key topics (simple word frequency)
        all_text = " ".join([item.get("title", "") for item in news_items])
        key_topics = self._extract_key_topics(all_text)

        return {
            "overall_sentiment": overall,
            "sentiment_score": avg_score,
            "positive_count": sentiments["positive"],
            "negative_count": sentiments["negative"],
            "neutral_count": sentiments["neutral"],
            "total_articles": len(news_items),
            "key_topics": key_topics,
        }

    def _extract_key_topics(self, text: str) -> list[str]:
        """Extract key topics from text (simple implementation)"""
        # Common words to exclude
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "as",
            "is",
            "was",
            "are",
            "were",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "can",
            "stock",
            "stocks",
            "market",
        }

        # Split and count words
        words = text.lower().split()
        word_count = {}

        for word in words:
            # Clean word
            word = word.strip(".,!?;:\"'")
            if len(word) > 3 and word not in stop_words:
                word_count[word] = word_count.get(word, 0) + 1

        # Get top 5 words
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_words[:5]]
