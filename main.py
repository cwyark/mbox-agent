import logging
import asyncio
import uvloop
from box import BoxPacketReceiver

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

def __name__ == "__main__":
    loop = asyncio.get_event_loop()
    coro = serial_asyncio.create_serial_connection(loop, coro, "/dev/ttyS0", baudrate=115200, timeout=1500)
    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()
