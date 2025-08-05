"""
Financial Advisor Agent - Main agent for investment advice
"""
from google.adk.agents import Agent
from app.utils import OpenRouterLLM
from app.tools import (
    get_stock_info_tool,
    analyze_technical_tool,
    get_company_news_tool
)
import logging

logger = logging.getLogger(__name__)


class FinancialAdvisorAgent:
    """Main financial advisor agent for individual stock analysis"""
    
    def __init__(self, model: str = None):
        self.llm_wrapper = OpenRouterLLM(model=model)
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create the financial advisor agent"""
        return Agent(
            name="financial_advisor",
            model=self.llm_wrapper.get_adk_model(),
            description="Expert financial advisor specializing in stock analysis and investment recommendations",
            instruction="""You are an expert financial advisor with deep knowledge of stock markets, 
            fundamental analysis, and technical indicators.
            
            Your role is to:
            1. Analyze individual stocks when users ask about specific companies
            2. Provide comprehensive investment analysis including:
               - Current price and market performance
               - Fundamental metrics (P/E ratio, earnings, revenue, etc.)
               - Technical indicators and trend analysis
               - Recent news and sentiment
               - Investment recommendation with clear reasoning
            
            3. Explain financial concepts in clear, accessible language
            4. Always provide balanced analysis mentioning both opportunities and risks
            5. Include relevant metrics and data to support your recommendations
            
            When analyzing a stock:
            - First, get the stock information using get_stock_info_tool
            - Then, analyze technical indicators using analyze_technical_tool
            - Check recent news and sentiment using get_company_news_tool
            - Synthesize all information into a comprehensive recommendation
            
            Important guidelines:
            - Always disclose that this is not personalized financial advice
            - Mention the importance of diversification
            - Consider the user's risk tolerance when making recommendations
            - Be objective and data-driven in your analysis
            """,
            tools=[
                get_stock_info_tool,
                analyze_technical_tool,
                get_company_news_tool
            ]
        )
    
    def get_agent(self) -> Agent:
        """Get the configured agent"""
        return self.agent