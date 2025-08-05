"""
Market Analyst Agent - Analyzes market trends and conditions
"""

import logging

from google.adk.agents import Agent

from app.tools import get_market_overview_tool
from app.utils import OpenRouterLLM

logger = logging.getLogger(__name__)


class MarketAnalystAgent:
    """Market analyst agent for broader market analysis"""

    def __init__(self, model: str = None):
        self.llm_wrapper = OpenRouterLLM(model=model)
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create the market analyst agent"""
        return Agent(
            name="market_analyst",
            model=self.llm_wrapper.get_adk_model(),
            description="Market analyst specializing in market trends, sentiment, and economic indicators",
            instruction="""You are an expert market analyst with deep understanding of market dynamics,
            economic indicators, and market sentiment.

            Your role is to:
            1. Analyze overall market conditions and trends
            2. Identify market opportunities and risks
            3. Explain how market conditions might affect investment decisions
            4. Provide insights on sector performance and rotations


            When providing market analysis:
            - Use get_market_overview_tool to get current market data
            - Analyze major indices (S&P 500, NASDAQ, Dow Jones)
            - Consider volatility indicators (VIX)
            - Discuss market sentiment and potential catalysts
            - Relate market conditions to investment strategy

            Key principles:
            - Be objective and data-driven
            - Consider both bullish and bearish scenarios
            - Explain complex market concepts clearly
            - Provide actionable insights for investors
            """,
            tools=[get_market_overview_tool],
        )

    def get_agent(self) -> Agent:
        """Get the configured agent"""
        return self.agent
