import logging
import asyncio
from datetime import datetime
from .pin import *
from .button import turn_blinking_led

_fast_counting = 0

async def counter_led_blink (led):
    led_on(led)
    await asyncio.sleep(1)
    led_off(led)

async def fast_counter_report (storage_queue):
    logger = logging.getLogger(__name__)
    global _fast_counting
    _seq_num = 0
    while True:
        now = datetime.utcnow()
        await asyncio.sleep(0.05)
        if now.second == 0:
            logger.info("FAST counter collection: {}".format(_fast_counting))
            q = dict()
            q['EventCode'] = 3201
            q['RecordDate'] = now.strftime('%Y-%m-%d %H:%M:%S.%f')
            q['SequentialNumber'] = _seq_num
            q['Value'] = _fast_counting
            await storage_queue.put(q)
            _fast_counting = 0
            _seq_num += 1
            await asyncio.sleep(1)


async def fast_counter_detect (loop, storage_queue, sampling_rate):
    logger = logging.getLogger(__name__)
    queue = storage_queue
    pin = FAST_COUNTER
    led = FAST_COUNTER_LED
    _prev = counter_value(pin)
    _value = 0
    global _fast_counting
    _counting = 0
    _seq_num = 0
    loop.create_task(fast_counter_report(storage_queue))
    while True:
        await asyncio.sleep(sampling_rate)
        _value = counter_value(pin)
        if _prev == 0 and _value == 1:
            _fast_counting += 1
        _prev = _value

async def direct_counter_detect (loop, storage_queue, sampling_rate):
    global blinking_led
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
            turn_blinking_led()
            q = dict()
            q['Eventcode'] = 3106
            q['SequentialNumber'] = _seq_num
            q['RecordDate'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
            await queue.put(q)
            _seq_num += 1
            logger.info("Direct counter triggered")
            loop.create_task(counter_led_blink(led))
        _prev = _value
