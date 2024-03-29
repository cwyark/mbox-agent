from .pin import *
from .driver import max31865
import asyncio
import logging
from datetime import datetime

async def TemperatureRunner (loop, storage_queue, cs = SPI_CS, miso = SPI_MISO, mosi = SPI_MOSI, clk = SPI_CLK, event_code = 3500):
    logger = logging.getLogger(__name__)
    _temp = 0
    _prev_temp = 0
    _max31865 = None
    _max31865 = max31865.max31865(cs, miso, mosi, clk)
    while True:
        await asyncio.sleep(10)
        _max31865.readTemp()
        _temp = round(_max31865.tempC, 1)
        logger.info("get temperature {} = {}".format(event_code, _temp))
        if _temp != _prev_temp:
            q = dict()
            q['EventCode'] = event_code
            q['RecordDate'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            q['value'] = round(_temp * 10)
            await storage_queue.put(q)
        _prev_temp = _temp
