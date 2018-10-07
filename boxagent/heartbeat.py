import logging 
import asyncio
from .pin import *

async def heartbeat (loop, storage_queue, interval):
    seq_number = 0
    logger = logging.getLogger(__name__)
    while True:
        seq_number += 1
        logger.info("Health Check")
        q = dict()
        q['EventCode'] = 3800
        q['SequentialNumber'] = seq_number

        await storage_queue.put(q)
        await asyncio.sleep(interval)
