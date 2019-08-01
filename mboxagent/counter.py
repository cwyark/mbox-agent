import logging
import asyncio
from datetime import datetime
from .pin import *
from .button import turn_blinking_led

_fast_counting = {}
_direct_counting = False

async def fast_counter_report (loop, storage_queue, eventcode):
    logger = logging.getLogger(__name__)
    global _fast_counting
    evt_str = str(eventcode)
    while True:
        now = datetime.now()
        await asyncio.sleep(0.05)
        if now.second == 0:
            logger.info("FAST counter collection: {}:{}".format(evt_str, _fast_counting[evt_str]))
            q = dict()
            q['EventCode'] = eventcode
            q['RecordDate'] = now.strftime('%Y-%m-%d %H:%M:%S.%f')
            q['Value'] = _fast_counting[evt_str]
            await storage_queue.put(q)
            _fast_counting[evt_str] = 0
            await asyncio.sleep(1)


async def fast_counter_detect (loop, storage_queue, sampling_rate, eventcode = 3201,
        pin = FAST_COUNTER, led = FAST_COUNTER_LED):
    logger = logging.getLogger(__name__)
    queue = storage_queue
    pin = pin
    led = led
    evt_str = str(eventcode)
    _prev = counter_value(pin)
    _value = 0
    global _fast_counting
    _fast_counting[evt_str] = 0
    _counting = 0
    loop.create_task(fast_counter_report(loop, storage_queue, eventcode))
    while True:
        await asyncio.sleep(sampling_rate)
        _value = counter_value(pin)
        led_value(led, _value^1)
        if _prev == 0 and _value == 1:
            _fast_counting[evt_str] += 1
        _prev = _value

async def direct_counter_report (loop, storage_queue, eventcode):
    logger = logging.getLogger(__name__)
    global _direct_counting
    evt_str = str(eventcode)
    while True:
        now = datetime.now()
        await asyncio.sleep(0.05)
        if now.second == 0:
            logger.info("DIRECT counter collection: {}:{}".format(evt_str, _direct_counting))
            q = dict()
            q['EventCode'] = eventcode
            q['RecordDate'] = now.strftime('%Y-%m-%d %H:%M:%S.%f')
            await storage_queue.put(q)
            _direct_counting = False
            await asyncio.sleep(1)

async def direct_counter_detect (loop, storage_queue, sampling_rate):
    """
    Direct counter only send one event to cloud per seconds.
    """
    global blinking_led
    logger = logging.getLogger(__name__)
    queue = storage_queue
    pin = DIRECT_COUNTER
    led = DIRECT_COUNTER_LED
    _prev = counter_value(pin)
    _value = 0
    _counting = 0
    loop.create_task(direct_counter_report(loop, storage_queue, 3106))
    while True:
        await asyncio.sleep(sampling_rate)
        _value = counter_value(pin)
        led_value(led, _value^1)
        if _prev == 0 and _value == 1:
            turn_blinking_led()
            _direct_counting = True
        _prev = _value
