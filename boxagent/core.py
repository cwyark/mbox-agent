import os
import logging
import asyncio
import json
import zmq
import zmq.asyncio
from asyncio import Queue
from datetime import datetime
from struct import Struct, pack, unpack
from .crc import crc
from .packet import BasePacket

DATA_FILE_PATH_PREFIX = "/home/pi/Desktop/BoxData"
DATA_LOG_FORMAT = "INSERT INTO InputsTableRaspberry (MBoxId,RecordDate,EventCode,{},SequentialNumber) VALUES ('{:x}', '{}', {}, {}, {})\n"

device_list_cache = dict()

class IngressTunnel(asyncio.Protocol):
    buffer = bytearray()
    def connection_made(self, transport):
        self.logger = logging.getLogger(__name__)
        self.transport = transport
        self.queue = Queue()
        self.transport.loop.create_task(self.consumer())
    
    def data_received(self, data):
        self.buffer += data
        if b'\x55' in data and b'\xd0' in self.buffer:
            if self.buffer[0] in b'\xaa' and self.buffer[1] in b'\xd1':
                # Need to alloc a new object to put in the queue
                if b'\xaa\xd1\x80\x03\x11\x55' in self.buffer or \
                        b'\xaa\xd1\x80\x05\x11\x55' in self.buffer:
                    # A wrokaround because some times module send out aa d1 80 03 11 55 
                    self.buffer = self.buffer[6:]
                self.queue.put_nowait(bytearray(self.buffer))
            else:
                self.logger.error("<Frame error> <{}>".format(' '.join('{:02x}'.format(x) for x in self.buffer)))
            self.buffer.clear()

    def connection_lost(self, exc):
        asyncio.get_event_loop.stop()

    async def response_packet(self, packet):
        payload = Struct("<HHB").pack(1000, packet.command_code, 1)
        response_packet = BasePacket.builder(device_id = packet.device_id, \
                counter = packet.counter, payload = payload)
        self.logger.info("[EVT]<PKT> [CAUSE]<reply message> [MSG]<{!s}> [RAW]<{!r}>".format(response_packet, response_packet))
# Add 0.2 secs delay in case of the zigbee module would received faulty
        await asyncio.sleep(0.2)
        self.transport.write(response_packet.frame)

    async def consumer(self):
        while True:
            frame = await self.queue.get()
            try:
                packet = BasePacket(frame)
                self.logger.info("<got message> <{!s}> <{!r}>".format(packet, packet))
                if packet.crc_validate() is True:
                    pass
                else:
                    self.logger.error("<CRC error> <{!r}>".format(packet))
            except Exception as e:
                self.logger.error("<Frame error> <{}>".format(' '.join('{:02x}'.format(x) for x in frame)))
