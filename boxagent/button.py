from .pin import *
import logging
import asyncio


async def button_detect (loop):
    logger = logging.getLogger(__name__)
    led_value_list = [0,0,0,0,0,0]
    led_pin_list = [LED1, LED2, LED3, LED4, LED5, LED6]
    button_pin_value = [0,0,0,0,0,0]
    button_pin_list = [BUTTON1, BUTTON2, BUTTON3, BUTTON4, BUTTON5, BUTTON6]
    blinking_led = None
    for led in led_pin_list:
        value = led_value_list[led_pin_list.index(led)]
        led_value(led, value)
    while True:
        await asyncio.sleep(0.1)
        for led in led_pin_list:
            value = led_value_list[led_pin_list.index(led)]
            led_value(led, value)       
            value ^= 1
            led_value_list[led_pin_list.index(led)] = value
        for button in button_pin_list:
            value = button_value(button)
            button_pin_value[button_pin_list.index(button)] = value

        logger.info(button_pin_value)
