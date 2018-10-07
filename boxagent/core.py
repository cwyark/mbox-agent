import os
import logging
import asyncio
import json
from asyncio import Queue
from datetime import datetime
from struct import Struct, pack, unpack
from .crc import crc
from .packet import BasePacket

class IngressTunnel(asyncio.Protocol):
    def __init__(self, queues):
        self.rx_queue, self.tx_queue = queues

    def connection_made(self, transport):
        self.logger = logging.getLogger(__name__)
        self.transport = transport
        self.buffer = bytearray()
        self.transport.loop.create_task(self.postman())
    
    def data_received(self, data):
        _header = b'\x02\x30\x43\x45'
        _end = b'\x0d\x0a\x03'
        self.buffer += data
        if _end in data:
            index_of_end = self.buffer.index(_end)
            if _header in self.buffer:
                index_of_header = self.buffer.index(_header)
                # Need to alloc a new object to put in the queue
                frame = self.buffer[index_of_header:index_of_end+2]
                self.rx_queue.put_nowait(frame)
            else:
                self.logger.error("<Frame error> <{}>".format(BasePacket.format_bytearray(self.buffer)))
            self.buffer = self.buffer[index_of_end+2:]

    def connection_lost(self, exc):
        self.transport.loop.close()

    async def postman(self):
        while True:
            frame = await self.tx_queue.get()
            # Add 0.2 secs delay in case of the zigbee module would received faylty
            await asyncio.sleep(0.2)
            self.logger.debug("delivery packet <{}>".format(BasePacket.format_bytearray(frame)))
            self.transport.write(frame)

class PacketCosumer:
    def __init__(self, loop, queues, packet_queue, config):
        self.rx_queue, self.tx_queue = queues
        self.packet_queue = packet_queue
        self.loop = loop
        self.logger = logging.getLogger(__name__)
    
    async def run(self):
        while True:
            frame = await self.rx_queue.get()
            try:
                packet = BasePacket(frame)
                self.logger.info("<got packet> <{!s}>".format(packet))
                q = dict()
                q['EventCode'] = packet.event_code
                q['Value'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.packet_queue.pyt_nowait(q)
            except Exception as e:
                self.logger.error("<runner frame error> {}: <{}>".format(str(e), BasePacket.format_bytearray(frame)))
