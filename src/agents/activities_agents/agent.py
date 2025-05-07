
from google.adk.agents import LlmAgent

from agents.model import create_reasoning_model

from tools.tools_impl import get_attraction_tools_async
from configs import get_logger
logger = get_logger(__name__)

async def get_activities_agent_async():
    tools,exist_stack = await get_attraction_tools_async()
    activities_agent = LlmAgent(
        name="activities_agent",
        model=create_reasoning_model(),
        description="Suggests interesting activities for the user at a destination.",
        instruction=(
            "Given a destination, dates, and budget, suggest 2-3 engaging tourist or cultural activities. "
            "For each activity, provide a name, a short description, price estimate, and duration in hours. "
            "Respond in plain English. Keep it concise and well-formatted."
        ),
        output_key="activities_output",
        tools=tools
    )
        
    return activities_agent, exist_stack 
