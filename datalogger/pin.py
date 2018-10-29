import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

INTERNET_LED = 19
POWER_LED = 26
FAST_COUNTER_LED = 5
DIRECT_COUNTER_LED = 6

FAST_COUNTER = 23
DIRECT_COUNTER = 24

LED1 = 16
LED2 = 12
LED3 = 7
LED4 = 8
LED5 = 25
LED6 = 18

BUTTON1 = 22
BUTTON2 = 27
BUTTON3 = 17
BUTTON4 = 4
BUTTON5 = 3
BUTTON6 = 2

SPI_CS = 18
SPI_MISO = 9 
SPI_MOSI = 10
SPI_CLK = 11

RC522_DETECT_LED = 13

def led_on(pin):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)

def led_off(pin):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

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
