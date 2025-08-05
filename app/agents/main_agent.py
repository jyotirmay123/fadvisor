"""
Main FAdvisor Agent - Orchestrates all financial advisory capabilities
"""

import logging
from typing import Dict, List, Optional

from google.adk.agents import Agent, SequentialAgent

from app.agents.financial_advisor import FinancialAdvisorAgent
from app.agents.market_analyst import MarketAnalystAgent
from app.agents.portfolio_manager import PortfolioManagerAgent
from app.config import config
from app.tools import analyze_technical_tool, get_company_news_tool, get_stock_info_tool
from app.utils import OpenRouterLLM

logger = logging.getLogger(__name__)


def create_fadvisor_agent(model: str = None) -> Agent:
    """
    Create the main FAdvisor agent with all sub-agents

    Args:
        model: Optional model name to use (defaults to config.DEFAULT_MODEL)

    Returns:
        Configured Agent instance
    """
    # Validate configuration
    config.validate()

    # Create LLM wrapper
    llm_wrapper = OpenRouterLLM(model=model)

    # Create sub-agents
    financial_advisor = FinancialAdvisorAgent(model=model).get_agent()
    market_analyst = MarketAnalystAgent(model=model).get_agent()
    portfolio_manager = PortfolioManagerAgent(model=model).get_agent()

    # Create main orchestrator agent
    root_agent = Agent(
        name="fadvisor_root",
        model=llm_wrapper.get_adk_model(),
        description="AI-powered financial advisor that provides comprehensive investment analysis and recommendations",
        instruction="""You are FAdvisor, an AI-powered financial advisory system that helps users make
        informed investment decisions.

        You coordinate three specialized agents:
        1. Financial Advisor: For individual stock analysis and investment recommendations
        2. Market Analyst: For market trends and economic conditions
        3. Portfolio Manager: For portfolio analysis and optimization

        Your approach:
        - When users ask about specific stocks or companies, use the Financial Advisor
        - When users ask about market conditions or trends, use the Market Analyst
        - When users provide their portfolio for analysis, use the Portfolio Manager
        - For complex questions, you may need to consult multiple agents

        Key principles:
        - Always provide balanced, objective analysis
        - Mention both opportunities and risks
        - Use data and metrics to support recommendations
        - Explain financial concepts clearly
        - Remind users this is not personalized financial advice

        Response format:
        - Start with a brief summary of the user's question
        - Provide comprehensive analysis using appropriate agents
        - End with clear, actionable recommendations
        - Include relevant disclaimers about investment risks

        Remember: Your goal is to educate and inform, helping users make better investment decisions
        based on data-driven analysis.
        """,
        sub_agents=[financial_advisor, market_analyst, portfolio_manager],
    )

    return root_agent


def create_background_monitoring_agent(
    symbols: list[str], thresholds: dict[str, float] = None
) -> Agent:
    """
    Create a background monitoring agent for continuous market monitoring

    Args:
        symbols: List of stock symbols to monitor
        thresholds: Price/indicator thresholds for alerts

    Returns:
        Configured monitoring agent
    """
    llm_wrapper = OpenRouterLLM()

    monitoring_agent = Agent(
        name="market_monitor",
        model=llm_wrapper.get_adk_model(),
        description="Background agent that monitors markets for significant changes",
        instruction=f"""You are a market monitoring agent that tracks these symbols: {', '.join(symbols)}.

        Your role is to:
        1. Monitor price movements and volume changes
        2. Track technical indicator changes (RSI, MACD, etc.)
        3. Monitor news sentiment shifts
        4. Alert on threshold breaches: {thresholds or 'Use default 5% price change'}

        Alert conditions:
        - Price change > 5% in a day
        - Volume spike > 200% of average
        - RSI enters oversold (<30) or overbought (>70)
        - Major news events affecting the stock
        - Sentiment shift from positive to negative or vice versa

        When generating alerts:
        - Clearly state what triggered the alert
        - Provide current metrics
        - Suggest potential actions
        - Include relevant context
        """,
        tools=[get_stock_info_tool, analyze_technical_tool, get_company_news_tool],
    )

    return monitoring_agent
