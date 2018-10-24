from .pin import *
from .driver import max31865
import asyncio
import logging
from datetime import datetime

async def TemperatureRunner (loop, storage_queue):
    logger = logging.getLogger(__name__)
    _temp = 0
    _prev_temp = 0
    _max31865 = None
    _max31865 = max31865.max31865(csPin,misoPin,mosiPin,clkPin)
    while True:
        await asyncio.sleep(10)
        _temp = _max31865.readTemp()
        if _temp != _prev_temp:
            q = dict()
            q['EventCode'] = 350
            q['RecordDate'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
            q['Sensor1'] = _temp
            await storage_queue.put(q)
        _prev_temp = _temp
