import logging
import asyncio
import serial_asyncio
import uvloop
from box import BoxPacketReceiver, SERIAL_RECV_TIMEOUT
from event import internet_connection_checker

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# Set up the logging system
logging.basicConfig(level=logging.DEBUG, 
        format="%(asctime)s %(name)-12s %(levelname)-8s $(message)", 
        datefmt="%m-%d %H:%M",
        handlers = [logging.FileHandler('box.log', 'w', 'utf-8'),]
        )

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    coro = serial_asyncio.create_serial_connection(loop, BoxPacketReceiver, "/dev/ttyS0", baudrate=115200, timeout=SERIAL_RECV_TIMEOUT)
    loop.run_until_complete(asyncio.gather(
        coro,
        internet_connection_checker('eth0'),
        internet_connection_checker('wlan0')
        ))
    loop.run_forever()
    loop.close()
