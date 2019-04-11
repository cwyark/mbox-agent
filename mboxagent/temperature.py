from .pin import *
from .driver import max31865
import asyncio
import logging
from datetime import datetime

async def TemperatureRunner (loop, storage_queue, cs = SPI_CS, temp_no = 1):
    logger = logging.getLogger(__name__)
    _temp = 0
    _prev_temp = 0
    _max31865 = None
    _max31865 = max31865.max31865(cs, SPI_MISO, SPI_MOSI, SPI_CLK)
    while True:
        await asyncio.sleep(10)
        _max31865.readTemp()
        _temp = round(_max31865.tempC, 1)
        logger.info("get temperature {} = {}".format(temp_no, _temp))
        if _temp != _prev_temp:
            data_attri = "Sensor{}".format(temp_no)
            q = dict()
            q['EventCode'] = 3500
            q['RecordDate'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            q[data_attri] = round(_temp * 10)
            await storage_queue.put(q)
        _prev_temp = _temp
