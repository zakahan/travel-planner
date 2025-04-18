import json

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from ..model import create_reasoning_model

activities_agent = Agent(
    name="stay_agent",
    model=create_reasoning_model(),
    description="Finds hotels within budget at a destination.",
    instruction=("Given a destination, Finds hotels within budget."),
)
session_service = InMemorySessionService()
runner = Runner(
    agent=activities_agent, app_name="stay_app", session_service=session_service
)
USER_ID = "user_stay"
SESSION_ID = "session_stay"


async def execute(request):
    session_service.create_session(
        app_name="stay_app", user_id=USER_ID, session_id=SESSION_ID
    )
    prompt = f"User is flying to {request['destination']}, and the budget is {request['budget']}."
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=message
    ):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            return response_text
