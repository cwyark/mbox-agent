import logging
import asyncio
from datetime import datetime
from .pin import *

async def fast_counter_detect (loop, storage_queue, sampling_rate):
    logger = logging.getLogger(__name__)
    queue = storage_queue
    pin = FAST_COUNTER
    led = FAST_COUNTER_LED
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
        now = datetime.utcnow()
        if now.second == 0:
            led_on(led)
            await asyncio.sleep(1)
            logger.info("FAST counter collection: {}".format(_counting))
            q = dict()
            q['EventCode'] = 3201
            q['RecordDate'] = now.strftime('%Y-%m-%d %H:%M:%S.%f')
            q['SequentialNumber'] = _seq_num
            q['Value'] = _counting
            _counting = 0
            await queue.put(q)
            _seq_num += 1
            led_off(led)

async def direct_counter_detect (loop, storage_queue, sampling_rate):
    logger = logging.getLogger(__name__)
    queue = storage_queue
    pin = DIRECT_COUNTER
    led = DIRECT_COUNTER_LED
    _prev = counter_value(pin)
    _value = 0
    _counting = 0
    _seq_num = 0
    while True:
        await asyncio.sleep(sampling_rate)
        _value = counter_value(pin)
        if _prev == 0 and _value == 1:
            led_on(led)
            q = dict()
            q['Eventcode'] = 3106
            q['SequentialNumber'] = _seq_num
            q['RecordDate'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
            await queue.put(q)
            _seq_num += 1
            logger.info("Direct counter triggered")
            await asyncio.sleep(1)
            led_off(led)
        _prev = _value
