import logging
import asyncio
import serial_asyncio
import uvloop
from box import BoxPacketReceiver, SERIAL_RECV_TIMEOUT, box_packet_consumer

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    coro = serial_asyncio.create_serial_connection(loop, BoxPacketReceiver, "/dev/ttyS0", baudrate=115200, timeout=SERIAL_RECV_TIMEOUT)
    loop.run_until_complete(coro)
    loop.run_until_complete(box_packet_consumer)
    loop.run_forever()
    loop.close()
