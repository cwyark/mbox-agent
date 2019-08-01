import logging
import asyncio
import shutil
import psutil
from datetime import datetime


async def disk_capacity_event(loop, queue, interval):
    seq_number = 0
    logger = logging.getLogger(__name__)
    while True:
        seq_number += 1
        logger.info("Disk Total Capacity")
        total = psutil.disk_usage("/").total
        q = dict()
        q['EventCode'] = 5001
        q['SequentialNumber'] = seq_number
        q['RecordDate'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        q['Value'] = total
        await storage.put(q)
        await asyncio.sleep(interval)

async def disk_usage_event(loop, queue, interval):
    seq_number = 0
    logger = logging.getLogger(__name__)
    while True:
        seq_number += 1
        logger.info("Disk Current Usage")
        used = shutil.disk_usage("/").used
        q = dict()
        q['EventCode'] = 5002
        q['SequentialNumber'] = seq_number
        q['RecordDate'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        q['Value'] = used
        await storage.put(q)
        await asyncio.sleep(interval)

async def cpu_usage_event(loop, queue, interval):
    seq_number = 0
    logger = logging.getLogger(__name__)
    while True:
        seq_number += 1
        logger.info("Disk Current Usage")
        cpu_usage = psutil.cpu_percent(interval=0.5)
        q = dict()
        q['EventCode'] = 5100
        q['SequentialNumber'] = seq_number
        q['RecordDate'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        q['Value'] = cpu_usage
        await storage.put(q)
        await asyncio.sleep(interval)

async def mem_usage_event(loop, queue, interval):
    seq_number = 0
    logger = logging.getLogger(__name__)
    while True:
        seq_number += 1
        logger.info("Disk Current Usage")
        used = psutil.virtual_memory().used
        q = dict()
        q['EventCode'] = 5200
        q['SequentialNumber'] = seq_number
        q['RecordDate'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        q['Value'] = used
        await storage.put(q)
        await asyncio.sleep(interval)
