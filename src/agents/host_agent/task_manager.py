import asyncio
from concurrent.futures import ThreadPoolExecutor

from .agent import execute
from configs import get_logger
logger = get_logger("HOST_AGENT__"+__name__)

async def run(payload):
    return await execute(payload)


from common.a2a_client import call_agent

FLIGHT_URL = "http://localhost:8001/run"
STAY_URL = "http://localhost:8002/run"
ACTIVITIES_URL = "http://localhost:8003/run"


def call_agent_wrapper(url, payload):
    try:
        return url, asyncio.run(call_agent(url, payload))
    except Exception as e:
        return url, f"Error: {str(e)}"


async def run(payload):
    # Print what the host agent is sending
    print("Incoming payload:", payload)
    with ThreadPoolExecutor() as executor:
        # 提交所有任务
        futures = [
            executor.submit(call_agent_wrapper, url, payload)
            for url in [FLIGHT_URL, STAY_URL, ACTIVITIES_URL]
        ]

        # 等待并收集结果
        results = {future.result()[0]: future.result()[1] for future in futures}

        # flights = await call_agent(FLIGHT_URL, payload)
        # stay = await call_agent(STAY_URL, payload)
        # activities = await call_agent(ACTIVITIES_URL, payload)
        # Log outputs
        # print("flights:", flights)
        # print("stay:", stay)
        # print("activities:", activities)
        # Ensure all are dicts before access
        # flights = flights if isinstance(flights, dict) else {}
        # stay = stay if isinstance(stay, dict) else {}
        # activities = activities if isinstance(activities, dict) else {}
        # return {
        #     "flights": flights.get("flights", "No flights returned."),
        #     "stay": stay.get("stays", "No stay options returned."),
        #     "activities": activities.get("activities", "No activities found."),
        # }
        return {
            "flights": results[FLIGHT_URL],
            "stay": results[STAY_URL],
            "activities": results[ACTIVITIES_URL],
        }
