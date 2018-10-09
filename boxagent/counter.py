import logging
import asyncio
from datetime import datetime
from .pin import *


async def fast_counter_detect (loop, storage_queue, sampling_rate):
    logger = logging.getLogger(__name__)
    queue = storage_queue
    pin = FAST_COUNTER
    _prev = counter_value(pin)
    _value = 0
    _counting = 0
    _seq_num = 0
    while True:
        await asyncio.sleep(sampling_rate)
        _value = counter_value(pin)
        if _prev == 0 and _value == 1:
            _counting += 1
        _prev = _value

        
        

async def direct_counter_detect (loop, storage_queue, sampling_rate):
    logger = logging.getLogger(__name__)
    queue = storage_queue
    pin = DIRECT_COUNTER
    _prev = counter_value(pin)
    _value = 0
    _counting = 0
    _seq_num = 0
    while True:
        await asyncio.sleep(sampling_rate)
        _value = counter_value(pin)
        if _prev == 0 and _value == 1:
            q = dict()
            q['Eventcode'] = 3106
            q['SequentialNumber'] = _seq_num
            q['RecordDate'] = datetime.utcnow.strftime('%Y-%m-%d %H:%M:%S.%f')
            await queue.put(q)
            _seq_num += 1
        _prev = _value
