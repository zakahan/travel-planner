import json
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from ..model import create_reasoning_model
from .prompt import booking_manager_ms, pre_req_ms, booking_ms, prepare_req_prompt
from tools.tools_impl.booking_tools import booking_attraction,booking_flight,booking_hotel
from .prompt import prepare_req_prompt
from configs import get_logger
logger = get_logger(__name__)

prepare_req_agent = LlmAgent(
    name='prepare_req_agent',
    model=create_reasoning_model(),
    description=pre_req_ms['des'],
    instruction=pre_req_ms['ins'],
    output_key="order_message"
)

booking_agent = LlmAgent(
    name='booking_agent',
    model=create_reasoning_model(),
    description=booking_ms['des'],
    instruction=booking_ms['ins'],
    tools=[booking_hotel, booking_attraction, booking_flight],
    
)


booking_manager_agent = SequentialAgent(
    name='booking_manager_agent',
    # model=create_reasoning_model(),
    description=booking_manager_ms['des'],
    # instruction=booking_manager_ms['ins'],
    sub_agents=[prepare_req_agent, booking_agent]
)

USER_ID = "user_booking"
SESSION_ID = "session_booking"
APP_NAME = "booking_manager_app"

session_service = InMemorySessionService()
runner = Runner(agent=booking_manager_agent, 
                app_name=APP_NAME,
                session_service=session_service)


async def execute(request):
    count = 0
    session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    prompt = prepare_req_prompt(request['plan'], request['message'])
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=message
    ):
        if event.is_final_response():
            print( {"summary": event.content.parts[0].text})
            if count == 1:
                return {"summary": event.content.parts[0].text}
            count += 1
    pass
