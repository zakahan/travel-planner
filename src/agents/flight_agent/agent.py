import json

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from ..model import create_reasoning_model

activities_agent = Agent(
    name="flight_agent",
    model=create_reasoning_model(),
    description="Suggests reasonable flight suggestion for the user from source location to destination.",
    instruction=(
        "Given reasonable flight suggestions for the user from source location to destination."
        "Provide the flight name, departure and arrival time, price estimate, and duration in hours. "
        "Respond in plain English. Keep it concise and well-formatted."
    ),
)
session_service = InMemorySessionService()
runner = Runner(
    agent=activities_agent, app_name="flight_app", session_service=session_service
)
USER_ID = "user_flight"
SESSION_ID = "session_flight"


async def execute(request):
    session_service.create_session(
        app_name="flight_app", user_id=USER_ID, session_id=SESSION_ID
    )
    prompt = "Provide some possible flights for the user from source location to destination. The source location is {src} and the destination is {dest}.".format(
        src=request["origin"], dest=request["destination"]
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
            print(response_text)
            return response_text
