"""
FastAPI server for FAdvisor
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pydantic import BaseModel, Field

from app.agents import create_background_monitoring_agent, create_fadvisor_agent
from app.config import config
from app.utils import OpenRouterLLM

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="FAdvisor API",
    description="AI-powered financial advisor API",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for agent management
agent = None
runner = None
session_service = None
monitoring_tasks = {}


# Request/Response models
class QueryRequest(BaseModel):
    query: str = Field(..., description="User's financial query")
    session_id: str | None = Field(
        default="default", description="Session ID for conversation continuity"
    )
    user_id: str | None = Field(default="user", description="User identifier")


class PortfolioRequest(BaseModel):
    holdings: list[dict[str, Any]] = Field(
        ..., description="List of portfolio holdings"
    )
    session_id: str | None = Field(default="default")
    user_id: str | None = Field(default="user")


class MonitoringRequest(BaseModel):
    symbols: list[str] = Field(..., description="Stock symbols to monitor")
    thresholds: dict[str, float] | None = Field(
        default=None, description="Alert thresholds"
    )
    interval_minutes: int = Field(default=60, description="Check interval in minutes")


class Response(BaseModel):
    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup"""
    global agent, runner, session_service

    try:
        # Validate configuration
        config.validate()

        # Test LLM connection
        llm = OpenRouterLLM()
        if not llm.test_connection():
            logger.error("Failed to connect to OpenRouter")
            raise Exception("LLM connection failed")

        # Create agent and runner
        agent = create_fadvisor_agent()
        session_service = InMemorySessionService()
        runner = Runner(
            agent=agent, app_name=config.APP_NAME, session_service=session_service
        )

        logger.info("FAdvisor API started successfully")

    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "FAdvisor API is running",
        "version": "0.1.0",
        "endpoints": {
            "POST /api/query": "Submit a financial query",
            "POST /api/analyze-portfolio": "Analyze a portfolio",
            "GET /api/market-overview": "Get market overview",
            "POST /api/monitor/start": "Start monitoring stocks",
            "DELETE /api/monitor/{task_id}": "Stop monitoring",
        },
    }


@app.post("/api/query", response_model=Response)
async def process_query(request: QueryRequest):
    """Process a financial query"""
    try:
        # Create or get session
        session = await session_service.get_session(
            app_name=config.APP_NAME,
            user_id=request.user_id,
            session_id=request.session_id,
        )

        if not session:
            session = await session_service.create_session(
                app_name=config.APP_NAME,
                user_id=request.user_id,
                session_id=request.session_id,
            )

        # Create message content
        content = types.Content(role="user", parts=[types.Part(text=request.query)])

        # Run the agent
        response_text = ""
        events = runner.run_async(
            user_id=request.user_id, session_id=request.session_id, new_message=content
        )

        async for event in events:
            if event.is_final_response() and event.content and event.content.parts:
                response_text = event.content.parts[0].text

        return Response(
            success=True,
            data={"response": response_text, "session_id": request.session_id},
        )

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze-portfolio", response_model=Response)
async def analyze_portfolio(request: PortfolioRequest):
    """Analyze a portfolio"""
    try:
        # Format the portfolio query
        holdings_str = "\n".join(
            [
                f"- {h['symbol']}: {h['quantity']} shares at ${h['purchase_price']}"
                for h in request.holdings
            ]
        )

        query = f"Please analyze my portfolio:\n{holdings_str}"

        # Process as a regular query
        query_request = QueryRequest(
            query=query, session_id=request.session_id, user_id=request.user_id
        )

        return await process_query(query_request)

    except Exception as e:
        logger.error(f"Error analyzing portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market-overview", response_model=Response)
async def get_market_overview():
    """Get current market overview"""
    try:
        query_request = QueryRequest(
            query="Please provide a current market overview with major indices and sentiment"
        )

        return await process_query(query_request)

    except Exception as e:
        logger.error(f"Error getting market overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/monitor/start", response_model=Response)
async def start_monitoring(
    request: MonitoringRequest, background_tasks: BackgroundTasks
):
    """Start background monitoring for stocks"""
    try:
        # Create a unique task ID
        task_id = f"monitor_{datetime.now().timestamp()}"

        # Create monitoring agent
        monitor_agent = create_background_monitoring_agent(
            symbols=request.symbols, thresholds=request.thresholds
        )

        # Start background monitoring task
        async def monitor_loop():
            while task_id in monitoring_tasks:
                try:
                    # Check each symbol
                    for symbol in request.symbols:
                        query = f"Check {symbol} for any significant changes or alerts"
                        # Process through the monitoring agent
                        # (Implementation would involve running the agent and checking conditions)

                    # Wait for next interval
                    await asyncio.sleep(request.interval_minutes * 60)

                except Exception as e:
                    logger.error(f"Monitoring error: {e}")

        # Add task to background tasks
        monitoring_tasks[task_id] = True
        background_tasks.add_task(monitor_loop)

        return Response(
            success=True,
            data={
                "task_id": task_id,
                "symbols": request.symbols,
                "interval_minutes": request.interval_minutes,
            },
        )

    except Exception as e:
        logger.error(f"Error starting monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/monitor/{task_id}", response_model=Response)
async def stop_monitoring(task_id: str):
    """Stop a monitoring task"""
    try:
        if task_id in monitoring_tasks:
            del monitoring_tasks[task_id]
            return Response(
                success=True, data={"message": f"Monitoring task {task_id} stopped"}
            )
        else:
            raise HTTPException(status_code=404, detail="Task not found")

    except Exception as e:
        logger.error(f"Error stopping monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agent_ready": agent is not None,
    }


if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True if config.ENVIRONMENT == "development" else False,
    )
