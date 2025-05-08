
from google.adk.agents import Agent

from agents.model import create_reasoning_model

from tools.tools_impl import get_flight_tools_async
from configs import get_logger
logger = get_logger(__name__)

async def get_flight_agent_async():
    tools, exit_stack = await get_flight_tools_async()
    flight_agent = Agent(
        name="flight_agent",
        model=create_reasoning_model(),
        description="Suggests reasonable flight suggestion for the user from source location to destination.",
        instruction=(
            "Given reasonable flight suggestions for the user from source location to destination."
            "Provide the flight name, departure and arrival time, price estimate, and duration in hours. "
            "The number of flights should not be too many. 3 - 5 flights will be enough."
            "Respond in plain English. Keep it concise and well-formatted."
        ),
        output_key="flight_output",
        tools=tools
    )

    return flight_agent, exit_stack
