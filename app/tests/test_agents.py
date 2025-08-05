"""
Test suite for FAdvisor agents
"""

import asyncio
from unittest.mock import Mock, patch

import pytest

from app.agents import create_fadvisor_agent
from app.agents.financial_advisor import FinancialAdvisorAgent
from app.agents.market_analyst import MarketAnalystAgent
from app.agents.portfolio_manager import PortfolioManagerAgent
from app.config import config


@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    with patch.object(config, "OPENROUTER_API_KEY", "test_key"):
        with patch.object(config, "validate", return_value=True):
            yield config


@pytest.fixture
def mock_llm():
    """Mock LLM for testing"""
    with patch("app.utils.llm_wrapper.OpenRouterLLM") as mock:
        instance = mock.return_value
        instance.test_connection.return_value = True
        instance.get_adk_model.return_value = Mock()
        yield instance


class TestFinancialAdvisorAgent:
    """Test financial advisor agent"""

    def test_agent_creation(self, mock_llm):
        """Test agent can be created"""
        agent = FinancialAdvisorAgent()
        assert agent is not None
        assert agent.agent is not None
        assert agent.agent.name == "financial_advisor"

    def test_agent_has_tools(self, mock_llm):
        """Test agent has required tools"""
        agent = FinancialAdvisorAgent()
        tools = agent.agent.tools
        assert len(tools) == 3
        tool_names = [tool.__name__ for tool in tools]
        assert "get_stock_info_tool" in tool_names
        assert "analyze_technical_tool" in tool_names
        assert "get_company_news_tool" in tool_names


class TestMarketAnalystAgent:
    """Test market analyst agent"""

    def test_agent_creation(self, mock_llm):
        """Test agent can be created"""
        agent = MarketAnalystAgent()
        assert agent is not None
        assert agent.agent is not None
        assert agent.agent.name == "market_analyst"

    def test_agent_has_tools(self, mock_llm):
        """Test agent has required tools"""
        agent = MarketAnalystAgent()
        tools = agent.agent.tools
        assert len(tools) == 1
        assert tools[0].__name__ == "get_market_overview_tool"


class TestPortfolioManagerAgent:
    """Test portfolio manager agent"""

    def test_agent_creation(self, mock_llm):
        """Test agent can be created"""
        agent = PortfolioManagerAgent()
        assert agent is not None
        assert agent.agent is not None
        assert agent.agent.name == "portfolio_manager"

    def test_agent_has_tools(self, mock_llm):
        """Test agent has required tools"""
        agent = PortfolioManagerAgent()
        tools = agent.agent.tools
        assert len(tools) == 1
        assert tools[0].__name__ == "analyze_portfolio_tool"


class TestMainAgent:
    """Test main orchestrator agent"""

    def test_agent_creation(self, mock_config, mock_llm):
        """Test main agent can be created"""
        agent = create_fadvisor_agent()
        assert agent is not None
        assert agent.name == "fadvisor_root"

    def test_agent_has_subagents(self, mock_config, mock_llm):
        """Test main agent has all sub-agents"""
        agent = create_fadvisor_agent()
        assert hasattr(agent, "sub_agents")
        assert len(agent.sub_agents) == 3

        sub_agent_names = [sa.name for sa in agent.sub_agents]
        assert "financial_advisor" in sub_agent_names
        assert "market_analyst" in sub_agent_names
        assert "portfolio_manager" in sub_agent_names


# Integration tests would go here, but require actual API keys
# and would be marked with @pytest.mark.integration
