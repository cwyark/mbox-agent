from .pin import *
from .driver import max31865
import asyncio
import logging


async def get_temperature (loop, storage_queue):
    logger = logging.getLogger(__name__)
    while True:
        await asyncio.sleep(1)
        logger.info("get temperature")
        
