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
    _max31865 = max31865.max31865(SPI_CS, SPI_MISO, SPI_MOSI, SPI_CLK)
    while True:
        await asyncio.sleep(10)
        _max31865.readTemp()
        _temp = round(_max31865.tempC, 1)
        logger.info("get temperature = {}".format(_temp))
        if _temp != _prev_temp:
            q = dict()
            q['EventCode'] = 3500
            q['RecordDate'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
            q['Sensor1'] = round(_temp * 10)
            await storage_queue.put(q)
        _prev_temp = _temp
