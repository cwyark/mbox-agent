import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

INTERNET_LED = 19
POWER_LED = 26
FAST_COUNTER_LED = 5
DIRECT_COUNTER_LED = 6

FAST_COUNTER = 23
DIRECT_COUNTER = 24


LED1 = 18
LED2 = 25
LED3 = 8
LED4 = 7
LED5 = 12
LED6 = 16

BUTTON1 = 2
BUTTON2 = 3
BUTTON3 = 4
BUTTON4 = 17
BUTTON5 = 27
BUTTON6 = 22

def led_on(pin):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

def led_off(pin):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)

def led_value(pin, value):
    if value == 1:
        led_on(pin)
    else:
        led_off(pin)

def button_value(pin):
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    return GPIO.input(pin)
    

def counter_value(pin):
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    return GPIO.input(pin)
