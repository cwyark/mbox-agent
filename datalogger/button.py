from .pin import *
import logging
from datetime import datetime
import asyncio

blinking_led = None
led_pin_list = [LED1, LED2, LED3, LED4, LED5, LED6]
led_perment_value = [0,0,0,0,0,0]

def turn_blinking_led():
    global blinking_led
    blinking_led = None

async def led_blink_routing ():
    global blinking_led
    global led_pin_list
    global led_perment_value
    led_cache = [0,0,0,0,0,0]
# Turn off all LED first
    for led in led_pin_list:
        value = led_cache[led_pin_list.index(led)]
        led_value(led, value)
    while True:
        await asyncio.sleep(0.5)
        for led in led_pin_list:
            _index = led_pin_list.index(led)
            if blinking_led == led:
                led_cache[_index] ^= 1
                led_perment_value[_index] = 1
            else:
                led_cache[_index] = 0
                led_perment_value[_index] = 0
            led_value(led, led_cache[_index])

async def button_detect (loop, storage_queue):
    global blinking_led
    global led_pin_list
    global led_perment_value
    seq_number = 0
    logger = logging.getLogger(__name__)
    button_cache = [0,0,0,0,0,0]
    button_perment_value = [0,0,0,0,0,0]
    button_pin_list = [BUTTON1, BUTTON2, BUTTON3, BUTTON4, BUTTON5, BUTTON6]
    blinking_led = None
    loop.create_task(led_blink_routing())
    while True:
        await asyncio.sleep(0.05)
        for button in button_pin_list:
            _index = button_pin_list.index(button)
            _value = button_value(button)
            _prev_value = button_cache[_index]
            button_cache[_index] = _value
            if _prev_value == 1 and _value == 0:
                blinking_led = led_pin_list[_index]
                button_perment_value[_index] ^= 1
                if led_perment_value[_index] == 1:
                    led_perment_value[_index] = 0 
                    blinking_led = None
                q = dict()
                q['EventCode'] = 3100 + _index
                q['SequentialNumber'] = seq_number
                q['RecordDate'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
                q['Value'] = button_perment_value[_index]
                await storage_queue.put(q)
                seq_number += 1
