import asyncio
from concurrent.futures import ThreadPoolExecutor
from .agent import execute
from configs import get_logger
logger = get_logger("BOOKING_AGENT__"+__name__)


async def run(payload):
    print("Incoming payload:", payload)
    return await execute(payload)