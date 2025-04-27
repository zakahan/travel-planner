import json

from contextlib import AsyncExitStack
from google.adk.agents import Agent, LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from ..model import create_reasoning_model

from tools.tools_impl import get_attraction_tools_async
from configs import get_logger
logger = get_logger(__name__)

async def get_activities_agent_async():
    tools,exist_stack = await get_attraction_tools_async()
    activities_agent = Agent(
    name="activities_agent",
    model=create_reasoning_model(),
    description="Suggests interesting activities for the user at a destination.",
    instruction=(
        "Given a destination, dates, and budget, suggest 2-3 engaging tourist or cultural activities. "
        "For each activity, provide a name, a short description, price estimate, and duration in hours. "
        "Respond in plain English. Keep it concise and well-formatted."
    ),
    tools = tools
    )
        
    return activities_agent, exist_stack 

USER_ID = "user_activities"
SESSION_ID = "session_activities"


async def execute(request):
    activities_agent, exist_stack = await get_activities_agent_async()
    session_service = InMemorySessionService()
    runner = Runner(
        agent=activities_agent, app_name="activities_app", session_service=session_service
    )
    session_service.create_session(
        app_name="activities_app", user_id=USER_ID, session_id=SESSION_ID
    )
    prompt = (
        f"User is flying to {request['destination']} from {request['start_date']} to {request['end_date']}, "
        f"with a budget of {request['budget']}. Suggest 2-3 activities, each with name, description, price estimate, and duration. "
    )
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=message
    ):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            logger.debug(f"Activaties Agent:\n{response_text}")
            await exist_stack.aclose()
            return response_text
