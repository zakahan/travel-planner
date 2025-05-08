
from google.adk.agents import LlmAgent

from agents.model import create_reasoning_model

from tools.tools_impl import get_hotel_tools_async
from configs import get_logger
logger = get_logger(__name__)

async def get_stay_agent_async():
    tools, exit_stack = await get_hotel_tools_async()
    stay_agent = LlmAgent(
        name="stay_agent",
        model=create_reasoning_model(),
        description="Finds hotels within budget at a destination.",
        instruction=("Given a destination, Finds hotels within budget."
                     "Respond in plain English. Keep it concise and well-formatted."),
        output_key="stay_output",
        tools=tools
    )
   
    return stay_agent, exit_stack
