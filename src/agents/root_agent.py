import os
import json
import asyncio
from contextlib import AsyncExitStack
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent
from google.adk.models.lite_llm import LiteLlm
from google.genai import types
from google.adk.tools import agent_tool
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

from typing import Any
from configs import get_logger
logger = get_logger(__name__)
from .model import create_reasoning_model
from .activities_agents import get_activities_agent_async
from .booking_agents import get_booking_agent
from .flight_agents import get_flight_agent_async
from .stay_agents import get_stay_agent_async



async def _collect_exit_stack(
        exit_stack_list: list[AsyncExitStack]
)-> AsyncExitStack:
    """
    collection exit stack by all tools.
    refer to https://github.com/wadave/vertex_ai_mcp_samples/blob/main/adk-web-mcp-sse/adk_multiagent_mcp_app/agent.py
    """
    # create the master exit_stack
    collection_exit_stack = AsyncExitStack()
    for exit_stack in exit_stack_list:
        if exit_stack:
            await collection_exit_stack.enter_async_context(exit_stack)
            pass
        pass
    return collection_exit_stack



root_description = "You are an expert in travel planning, and you will have multiple tools at your disposal for formulating procedures or booking travel itineraries.  "

root_instruction = """You will receive requests that can be roughly divided into three categories: plan generation, plan regeneration, and booking.
Firstly, you need to make a judgment on which category the current user request belongs to. Then, you need to consider the Agent tools that need to be called for each type of request, make a selection, and execute it.
Plan Generation: You need to call activities_agent, flight_agent, and stay_agent to generate a plan.
Plan Regeneration: You need to judge which one or more of activities_agent, flight_agent, and stay_agent need to be called according to the user's opinion to regenerate the plan.
Booking: You need to call booking_agent for booking according to the user's suggestions.
Requirement:
Each time the final result is returned as text, it should be in JSON format, and the key is the name of the Agent used.
For example, if flight_agent and stay_agent are called in this call and the information related to these two parts is involved, the return value is
```json
{
    "flight_agent": "some text",
    "stay_agent": "some text"
}
"""


async def create_agent() -> tuple[SequentialAgent, AsyncExitStack]:
    """get all async tools from mcp server."""
    booking_agent = get_booking_agent()
    act_agent, sub_stack_1 = await get_activities_agent_async()
    flight_agent, sub_stack_2 = await get_flight_agent_async()
    stay_agent, sub_stack_3 = await get_stay_agent_async()
    exit_list = [sub_stack_1,sub_stack_2,sub_stack_3]
    exit_stack = await _collect_exit_stack(exit_list)

    tools = [
        agent_tool.AgentTool(act_agent), 
        agent_tool.AgentTool(flight_agent),
        agent_tool.AgentTool(stay_agent),
        agent_tool.AgentTool(booking_agent)
    ]

    # root
    root_agent = LlmAgent(
        model=create_reasoning_model(),
        name='root_agent',
        description=root_description,
        instruction=root_instruction,
        # sub_agents=[planning_agent, booking_manager_agent]
        # sub_agents=[act_agent, flight_agent, stay_agent, booking_agent]
        tools=tools
    )
    return root_agent, exit_stack


async def execute(prompt:str) -> list[str]:
    user_id = "user_01"
    session_id = "session_01"
    app_name = "travel_planner_app"
    session_service = InMemorySessionService()
    session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
    root_agent, exit_stack = await create_agent()

    runner = Runner(
        agent=root_agent,
        app_name=app_name,
        session_service=session_service,
    )
   
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    response_list = []
    try:
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=message,
        ):
            
            if event.is_final_response() and event.author == "root_agent":
                logger.debug(f"author event done: {event.author}")
                # res =  {"text": event.content.parts[0].text, "author": event.author}
                res = event.content.parts[0].text
                response_list.append(res)
                
            pass   # end of async for 
        pass
    except json.decoder.JSONDecodeError as e:
        logger.error(f"JSONDecoder Error: {e.__class__}:{str(e)}")
    
    except Exception as e:
        logger.error(f"{e.__class__}: {str(e)}")
        logger.exception(e)
    # got ending
    finally:
        await exit_stack.aclose()
        return response_list

