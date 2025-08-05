"""
Main entry point for FAdvisor - AI Financial Advisor
"""

import asyncio
import logging
import os
import sys
from typing import Optional

from dotenv import load_dotenv

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agents import create_fadvisor_agent
from app.config import config
from app.utils import FREE_MODELS, OpenRouterLLM

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class FAdvisorCLI:
    """Command-line interface for FAdvisor"""

    def __init__(self):
        self.agent = None
        self.runner = None
        self.session_service = None
        self.session_id = "fadvisor_session"
        self.user_id = "user"

    def setup(self, model: str | None = None):
        """Set up the agent and runner"""
        try:
            # Test LLM connection first
            llm = OpenRouterLLM(model=model)
            logger.info("Testing LLM connection...")

            if not llm.test_connection():
                logger.error(
                    "Failed to connect to OpenRouter. Please check your API key."
                )
                return False

            logger.info("LLM connection successful!")

            # Create the main agent
            logger.info("Creating FAdvisor agent...")
            self.agent = create_fadvisor_agent(model=model)

            # Set up session service and runner
            self.session_service = InMemorySessionService()
            self.runner = Runner(
                agent=self.agent,
                app_name=config.APP_NAME,
                session_service=self.session_service,
            )

            logger.info("FAdvisor is ready!")
            return True

        except Exception as e:
            logger.error(f"Setup failed: {e}")
            return False

    async def process_query(self, query: str) -> str:
        """Process a user query and return the response"""
        try:
            # Create session if it doesn't exist
            session = await self.session_service.get_session(
                app_name=config.APP_NAME,
                user_id=self.user_id,
                session_id=self.session_id,
            )

            if not session:
                session = await self.session_service.create_session(
                    app_name=config.APP_NAME,
                    user_id=self.user_id,
                    session_id=self.session_id,
                )

            # Create message content
            content = types.Content(role="user", parts=[types.Part(text=query)])

            # Run the agent
            response_text = ""
            events = self.runner.run_async(
                user_id=self.user_id, session_id=self.session_id, new_message=content
            )

            async for event in events:
                if event.is_final_response() and event.content and event.content.parts:
                    response_text = event.content.parts[0].text

            return response_text

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"Error: {str(e)}"

    def print_welcome(self):
        """Print welcome message"""
        print("\n" + "=" * 60)
        print("Welcome to FAdvisor - Your AI Financial Assistant")
        print("=" * 60)
        print("\nI can help you with:")
        print("- Stock analysis and recommendations")
        print("- Market trends and conditions")
        print("- Portfolio analysis and optimization")
        print("- Investment strategies and education")
        print("\nType 'help' for commands or 'quit' to exit")
        print("=" * 60 + "\n")

    def print_help(self):
        """Print help message"""
        print("\nAvailable commands:")
        print("- Ask any investment question")
        print("- 'analyze SYMBOL' - Analyze a specific stock")
        print("- 'portfolio' - Get help with portfolio analysis")
        print("- 'market' - Get market overview")
        print("- 'help' - Show this help message")
        print("- 'quit' or 'exit' - Exit the application\n")

    async def run_interactive(self):
        """Run interactive CLI mode"""
        self.print_welcome()

        while True:
            try:
                # Get user input
                query = input("\nYou: ").strip()

                # Handle special commands
                if query.lower() in ["quit", "exit"]:
                    print("\nThank you for using app. Goodbye!")
                    break
                elif query.lower() == "help":
                    self.print_help()
                    continue
                elif not query:
                    continue

                # Process the query
                print("\nFAdvisor: Analyzing...\n")
                response = await self.process_query(query)
                print(response)

            except KeyboardInterrupt:
                print("\n\nInterrupted. Type 'quit' to exit.")
            except Exception as e:
                print(f"\nError: {e}")


async def main():
    """Main entry point"""
    # Load environment variables
    load_dotenv()

    # Create CLI instance
    cli = FAdvisorCLI()

    # Allow model selection
    print("\nAvailable models:")
    for i, (name, model) in enumerate(FREE_MODELS.items(), 1):
        print(f"{i}. {name}: {model}")

    model_choice = input("\nSelect model (1-5) or press Enter for default: ").strip()

    selected_model = None
    if model_choice.isdigit() and 1 <= int(model_choice) <= len(FREE_MODELS):
        selected_model = list(FREE_MODELS.values())[int(model_choice) - 1]
        print(f"Using model: {selected_model}")
    else:
        print(f"Using default model: {config.DEFAULT_MODEL}")

    # Set up the agent
    if not cli.setup(model=selected_model):
        print("Failed to initialize app. Please check your configuration.")
        return

    # Run interactive mode
    await cli.run_interactive()


if __name__ == "__main__":
    asyncio.run(main())
