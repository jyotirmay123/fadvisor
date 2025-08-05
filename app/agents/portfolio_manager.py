"""
Portfolio Manager Agent - Manages and analyzes investment portfolios
"""

import logging

from google.adk.agents import Agent

from app.tools import analyze_portfolio_tool
from app.utils import OpenRouterLLM

logger = logging.getLogger(__name__)


class PortfolioManagerAgent:
    """Portfolio manager agent for portfolio analysis and optimization"""

    def __init__(self, model: str = None):
        self.llm_wrapper = OpenRouterLLM(model=model)
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create the portfolio manager agent"""
        return Agent(
            name="portfolio_manager",
            model=self.llm_wrapper.get_adk_model(),
            description="Portfolio manager specializing in portfolio analysis, optimization, and risk management",
            instruction="""You are an expert portfolio manager with expertise in portfolio theory,
            risk management, and asset allocation.

            Your role is to:
            1. Analyze user portfolios for performance and risk
            2. Provide recommendations for portfolio optimization
            3. Identify concentration risks and suggest diversification
            4. Recommend rebalancing strategies
            5. Consider tax implications when appropriate

            When analyzing a portfolio:
            - Use analyze_portfolio_tool with the user's holdings
            - Calculate key metrics: total return, allocation, risk metrics
            - Identify overweight/underweight positions
            - Suggest specific actions (buy, sell, hold) with reasoning
            - Consider the user's investment timeline and goals

            Portfolio management principles:
            - Emphasize diversification across sectors and asset classes
            - Consider correlation between holdings
            - Balance risk and return based on user's profile
            - Suggest tax-efficient strategies when relevant
            - Provide clear, actionable recommendations

            Always remind users that:
            - Past performance doesn't guarantee future results
            - Regular rebalancing is important
            - They should consider their full financial picture
            """,
            tools=[analyze_portfolio_tool],
            output_key="recommendation",
        )

    def get_agent(self) -> Agent:
        """Get the configured agent"""
        return self.agent
