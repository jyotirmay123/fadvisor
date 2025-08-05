# FAdvisor - AI Financial Advisor using Google Agent Development Kit

FAdvisor is an AI-powered financial advisory system built using Google's Agent Development Kit (ADK)
with LiteLLM and OpenRouter integration. It provides comprehensive investment analysis, portfolio
management, and market insights.

## Features

- **Stock Analysis**: Detailed analysis of individual stocks with technical indicators and
  fundamental metrics
- **Portfolio Management**: Portfolio analysis, optimization recommendations, and risk assessment
- **Market Overview**: Real-time market conditions, indices tracking, and sentiment analysis
- **News Analysis**: Company-specific news with sentiment analysis
- **Multi-Agent Architecture**: Specialized agents for different financial tasks
- **Background Monitoring**: Continuous monitoring of selected stocks with alerts

## Architecture

FAdvisor uses Google ADK's multi-agent system with three specialized agents:

1. **Financial Advisor Agent**: Analyzes individual stocks and provides investment recommendations
2. **Market Analyst Agent**: Monitors market trends and economic conditions
3. **Portfolio Manager Agent**: Analyzes portfolios and suggests optimization strategies

## Requirements

- Python 3.10+
- OpenRouter API key (for LLM access)
- Optional: Financial data API keys (Alpha Vantage, Finnhub, NewsAPI)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/app.git
cd fadvisor
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
cp .env.example .env
# Edit .env and add your OpenRouter API key
```

## Configuration

Required environment variables:

- `OPENROUTER_API_KEY`: Your OpenRouter API key (required)

Optional API keys for enhanced features:

- `ALPHA_VANTAGE_API_KEY`: For additional stock data
- `FINNHUB_API_KEY`: For real-time market data
- `NEWS_API_KEY`: For comprehensive news coverage

## Usage

### Command Line Interface

Run the interactive CLI:

```bash
python -m app.main
```

Example queries:

- "Analyze AAPL stock"
- "What's the current market sentiment?"
- "Analyze my portfolio: 10 AAPL at $150, 20 GOOGL at $140"
- "Should I invest in technology stocks right now?"

### API Server

Start the FastAPI server:

```bash
python -m app.api_server
```

The API will be available at `http://localhost:8000`

API Endpoints:

- `POST /api/query`: Submit any financial query
- `POST /api/analyze-portfolio`: Analyze a portfolio
- `GET /api/market-overview`: Get market overview
- `POST /api/monitor/start`: Start monitoring stocks
- `DELETE /api/monitor/{task_id}`: Stop monitoring

Example API request:

```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Analyze AAPL stock"}'
```

### Using ADK Web Interface

You can also run FAdvisor using ADK's built-in web interface:

1. Set up the agent configuration:

```bash
mkdir -p fadvisor_adk
cd fadvisor_adk
```

2. Create `agent.py`:

```python
from app.agents import create_fadvisor_agent
root_agent = create_fadvisor_agent()
```

3. Create `__init__.py`:

```python
from . import agent
```

4. Run ADK web:

```bash
adk web
```

## Available Models

FAdvisor supports various free models through OpenRouter:

- DeepSeek Chat (default)
- Mistral 7B Instruct
- Llama 3.2 1B Instruct
- Google Gemma 2 9B
- Microsoft Phi 3 Mini

## Example Outputs

### Stock Analysis

```
Query: Analyze AAPL stock

FAdvisor: Based on my analysis of Apple Inc. (AAPL):

Current Price: $189.50
Market Cap: $2.95T
P/E Ratio: 31.2

Technical Analysis:
- Trend: Uptrend
- RSI: 58 (Neutral)
- MACD: Bullish crossover
- Support: $185, Resistance: $195

Recent News Sentiment: Positive
- Strong iPhone 15 sales
- Services revenue growth

Recommendation: BUY/HOLD
Apple shows strong fundamentals with reasonable valuation...
```

### Portfolio Analysis

```
Query: Analyze my portfolio: 10 AAPL at $150, 20 MSFT at $300

FAdvisor: Portfolio Analysis:

Total Value: $8,895
Total Cost: $7,500
Total Return: +18.6%

Sector Allocation:
- Technology: 100%

Recommendations:
1. High concentration in tech sector - consider diversification
2. Both holdings showing strong performance
3. Consider taking partial profits on MSFT (up 25%)
```

## Testing

Run the test suite:

```bash
pytest fadvisor/tests/
```

### Last Test Run

==================================================== test session starts
===================================================== platform darwin -- Python 3.11.11,
pytest-8.4.1, pluggy-1.6.0 -- /Users/administrator/Desktop/work/fadvisor/.venv/bin/python3.11
cachedir: .pytest_cache rootdir: /Users/administrator/Desktop/work/fadvisor configfile: pytest.ini
testpaths: app plugins: asyncio-1.1.0, anyio-4.10.0, cov-6.2.1 asyncio: mode=Mode.STRICT,
asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function collected 14 items

app/tests/test_agents.py::TestFinancialAdvisorAgent::test_agent_creation PASSED [ 7%]
app/tests/test_agents.py::TestFinancialAdvisorAgent::test_agent_has_tools PASSED [ 14%]
app/tests/test_agents.py::TestMarketAnalystAgent::test_agent_creation PASSED [ 21%]
app/tests/test_agents.py::TestMarketAnalystAgent::test_agent_has_tools PASSED [ 28%]
app/tests/test_agents.py::TestPortfolioManagerAgent::test_agent_creation PASSED [ 35%]
app/tests/test_agents.py::TestPortfolioManagerAgent::test_agent_has_tools PASSED [ 42%]
app/tests/test_agents.py::TestMainAgent::test_agent_creation PASSED [ 50%]
app/tests/test_agents.py::TestMainAgent::test_agent_has_subagents PASSED [ 57%]
app/tests/test_tools.py::TestStockDataFetcher::test_get_ticker_info PASSED [ 64%]
app/tests/test_tools.py::TestStockDataFetcher::test_get_price_history PASSED [ 71%]
app/tests/test_tools.py::TestPortfolioAnalyzer::test_analyze_portfolio PASSED [ 78%]
app/tests/test_tools.py::TestAgentTools::test_get_stock_info_tool PASSED [ 85%]
app/tests/test_tools.py::TestAgentTools::test_analyze_technical_tool PASSED [ 92%]
app/tests/test_tools.py::TestAgentTools::test_calculate_portfolio_allocation PASSED [100%]

======================================================= tests coverage
======================================================= ********\*\*********\_********\*\*********
coverage: platform darwin, python 3.11.11-final-0 ********\*\*********\_\_********\*\*********

## Name Stmts Miss Cover

app/**init**.py 2 0 100% app/agent.py 8 8 0% app/agents/**init**.py 5 0 100%
app/agents/financial_advisor.py 13 0 100% app/agents/main_agent.py 22 3 86%
app/agents/market_analyst.py 13 0 100% app/agents/portfolio_manager.py 13 0 100% app/api_server.py
130 130 0% app/config.py 26 3 88% app/main.py 111 111 0% app/setup.py 4 4 0% app/tests/**init**.py 0
0 100% app/tests/test_agents.py 69 0 100% app/tests/test_tools.py 56 0 100% app/tools/**init**.py 4
0 100% app/tools/agent_tools.py 59 34 42% app/tools/financial_tools.py 149 67 55%
app/tools/news_tools.py 127 108 15% app/utils/**init**.py 2 0 100% app/utils/llm_wrapper.py 28 6 79%

---

TOTAL 841 474 44% Coverage HTML written to dir htmlcov Coverage XML written to file out/coverage.xml
===================================================== 14 passed in 4.75s
=====================================================

## Development

The project structure:

```
fadvisor/
├── agents/          # ADK agent definitions
├── tools/           # Financial analysis tools
├── utils/           # LiteLLM wrapper and utilities
├── tests/           # Test suite
├── main.py          # CLI interface
├── api_server.py    # FastAPI server
└── config.py        # Configuration
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Disclaimer

FAdvisor provides AI-generated financial analysis for educational purposes only. It is not
personalized financial advice. Always consult with qualified financial advisors and do your own
research before making investment decisions.

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built with Google Agent Development Kit (ADK)
- Powered by LiteLLM and OpenRouter
- Financial data from Yahoo Finance
