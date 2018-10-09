from .pin import *
import logging
import asyncio


async def button_detect (loop, storage_queue):
    seq_number = 0
    logger = logging.getLogger(__name__)
    led_value_list = [0,0,0,0,0,0]
    led_pin_list = [LED1, LED2, LED3, LED4, LED5, LED6]
    button_pin_value = [0,0,0,0,0,0]
    button_pin_list = [BUTTON1, BUTTON2, BUTTON3, BUTTON4, BUTTON5, BUTTON6]
    blinking_led = None
    for led in led_pin_list:
# Turn off all LED first
        value = led_value_list[led_pin_list.index(led)]
        led_value(led, value)
    while True:
        await asyncio.sleep(0.1)
        for led in led_pin_list:
            if blinking_led == led:
                value = led_value_list[led_pin_list.index(blinking_led)]
                value ^=1 
            else:
                value = 0
            led_value_list[led_pin_list.index(led)] = value
            led_value(led, value)

        for button in button_pin_list:
            _value = button_value(button)
            _prev_value = button_pin_value[button_pin_list.index(button)]
            button_pin_value[button_pin_list.index(button)] = _value
            if _prev_value == 1 and _value == 0:
                blinking_led = led_pin_list[button_pin_list.index(button)]
                q = dict()
                q['EventCode'] = 3100 + button_pin_list.index(button)
                q['SequentialNumber'] = seq_number
                q['Value'] = 0
                logger.info("12413")
                await storage_queue.put(q)
            elif _prev_value == 0 and _value == 1:
                q = dict()
                q['EventCode'] = 3100 + button_pin_list.index(button)
                q['SequentialNumber'] = seq_number
                q['Value'] = 1
                await storage_queue.put(q)
            else:
                pass
        seq_number += 1
        logger.info(button_pin_value)
