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



root_description = "你是一个出行计划专家，你将拥有多个工具，用来指定流程或预定行程。"

root_instruction = """你收到的请求大致上可以分为三类请求，计划生成、计划重生成和预定。
首先你需要判断，判断当前用户的请求是属于哪一类，然后你需要考虑每类请求需要调用的Agent工具，做出选择，并且执行。
计划生成：你需要调用activities_agent、flight_agent和stay_agent，来生成方案
计划重生成：你需要根据用户提出的意见，来判断需要调用activities_agent、flight_agent和stay_agent中的一个或多个，来重生成方案
预定：你需要根据用户给出的建议，调用booking_agent进行预定
要求：
每次最终结果返回text，都需要使用json样式，key是所用agent的名称，
如本次调用用到了flight_agent和stay_agent，涉及到这两个部分的信息，则返回值为
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

