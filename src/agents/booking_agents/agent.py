from google.adk.agents import LlmAgent

from agents.model import create_reasoning_model
from .prompt import booking_des, booking_ins
from tools.tools_impl.booking_tools import booking_attraction,booking_flight,booking_hotel
from configs import get_logger
logger = get_logger(__name__)



def get_booking_agent() -> LlmAgent:
    booking_agent = LlmAgent(
        name='booking_agent',
        model=create_reasoning_model(),
        description=booking_des,
        instruction=booking_ins,
        tools=[booking_hotel, booking_attraction, booking_flight],
    )
    return booking_agent

