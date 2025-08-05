"""
ADK Web interface agent configuration for FAdvisor
This file enables running the full FAdvisor agent with 'adk web'
"""

import os
import sys

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add fadvisor to Python path if needed
if "fadvisor" not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main FAdvisor agent
from app.agents import create_fadvisor_agent

# Create the root agent that ADK will use
# This will use all the sub-agents and tools from the main implementation
root_agent = create_fadvisor_agent()

# The agent is now available for ADK web interface
# Run 'adk web' from this directory to start the web interface
