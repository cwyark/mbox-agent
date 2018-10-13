import logging 
import asyncio
from datetime import datetime
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
        q['RecordDate'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

        await storage_queue.put(q)
        await asyncio.sleep(interval)
