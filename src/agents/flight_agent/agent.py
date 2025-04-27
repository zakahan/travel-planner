import json

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from ..model import create_reasoning_model
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
            "Respond in plain English. Keep it concise and well-formatted."
        ),
        tools=tools
    )

    return flight_agent, exit_stack

USER_ID = "user_flight"
SESSION_ID = "session_flight"


async def execute(request):
    flight_agent, exit_stack = await get_flight_agent_async()
    session_service = InMemorySessionService()
    session_service.create_session(
        app_name="flight_app", user_id=USER_ID, session_id=SESSION_ID
    )
    runner = Runner(
        agent=flight_agent, app_name="flight_app", session_service=session_service
    )
    prompt = "Please use the tool to help the user search for the most suitable flights and provide suggestions. " \
    "The user's departure location is {src}, the destination is {dest}, and the departure date is {start_date}.".format(
        src=request["origin"], dest=request["destination"], start_date=request["start_date"]
    )
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=message
    ):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            # try:
            #     parsed = json.loads(response_text)
            #     if "activities" in parsed and isinstance(parsed["activities"], list):
            #         return {"activities": parsed["activities"]}
            #     else:
            #         print("'activities' key missing or not a list in response JSON")
            #         return {"activities": response_text}  # fallback to raw text
            # except json.JSONDecodeError as e:
            #     print("JSON parsing failed:", e)
            #     print("Response content:", response_text)
            #     return {"activities": response_text}  # fallback to raw text
            logger.debug(f"Flight Agent:\n{response_text}")
            await exit_stack.aclose()
            return response_text
