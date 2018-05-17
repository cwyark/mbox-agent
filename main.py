import logging
import asyncio
import serial_asyncio
import uvloop
from box import BoxPacketReceiver, SERIAL_RECV_TIMEOUT
from handshakes import internet_connection_checker

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

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
