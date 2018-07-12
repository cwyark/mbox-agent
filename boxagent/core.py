import os
import logging
import asyncio
import json
from asyncio import Queue
from datetime import datetime
from struct import Struct, pack, unpack
from .crc import crc
from .packet import BasePacket

DATA_LOG_FORMAT = "INSERT INTO InputsTableRaspberry (MBoxId,RecordDate,EventCode,{},SequentialNumber) VALUES ('{:x}', '{}', {}, {}, {})\n"

device_list_cache = dict()

class IngressTunnel(asyncio.Protocol):
    def __init__(self, queues):
        self.rx_queue, self.tx_queue = queues

    def connection_made(self, transport):
        self.logger = logging.getLogger(__name__)
        self.transport = transport
        self.buffer = bytearray()
        self.transport.loop.create_task(self.postman())
    
    def data_received(self, data):
        self.buffer += data
        if b'\x55' in data and b'\xd0' in self.buffer:
            if self.buffer[0] in b'\xaa' and self.buffer[1] in b'\xd1':
                # Need to alloc a new object to put in the queue
                if b'\xaa\xd1\x80\x03\x11\x55' in self.buffer or \
                        b'\xaa\xd1\x80\x05\x11\x55' in self.buffer:
                    # A wrokaround because some times module send out aa d1 80 03 11 55 
                    self.buffer = self.buffer[6:]
                self.rx_queue.put_nowait(bytearray(self.buffer))
            else:
                self.logger.error("<Frame error> <{}>".format(BasePacket.format_bytearray(\
                        self.buffer)))
            self.buffer.clear()

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
    def __init__(self, queues, packet_queue):
        self.rx_queue, self.tx_queue = queues
        self.packet_queue = packet_queue
        self.logger = logging.getLogger(__name__)
    
    async def run(self):
        while True:
            frame = await self.rx_queue.get()
            try:
                packet = BasePacket(frame)
                self.logger.info("<got packet> <{!s}>".format(packet))
                self.logger.debug("<got frame> <{!r}>".format(packet))
                if packet.crc_validate() is True:
                    self.dispatcher(packet)
                else:
                    self.logger.error("<CRC error> <{!r}>".format(packet))
            except Exception as e:
                self.logger.error("<runner frame error> <{}>".format(BasePacket.format_bytearray(frame)))

    def response_packet(self, packet):
        response_packet = packet.response_packet()
        self.logger.info("<reply packet> <{!s}>".format(response_packet))
        self.logger.debug("<reply frame> <{!r}>".format(response_packet))
        self.tx_queue.put_nowait(response_packet.frame)

    def dispatcher(self, packet):
        command_code = packet.command_code

        q = dict()
        q['MBoxId'] = packet.device_id
        q['RecordDate'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        q['EventCode'] = packet.command_code
        q['SequentialNumber'] = packet.counter+1

        if command_code == 1000:
            return
        elif command_code == 1002:
            self.response_packet(packet)
            q['Mbox-model-and-Version'] = "'{!s}'".format(packet.payload[6:30].decode())
        elif command_code >= 3301 and command_code <= 3306:
            index = packet.command_code - 3300
            self.response_packet(packet)
            q["RfId{}".format(index)] = "{:x}".format(int.from_bytes(packet.payload[2:7], \
                    byteorder='big'))
        elif command_code >= 3100 and command_code <= 3105:
            index = packet.command_code + 1 - 3100
            self.response_packet(packet)
            q["Button{}".format(index)] = "{:d}".format(packet.payload[2])
        elif command_code == 3106:
            self.response_packet(packet)
            q["Sensor1"] = int.from_bytes(packet.payload[2:6], byteorder='little')
        elif command_code == 3201:
            self.response_packet(packet)
            q["Counter1"] = int.from_bytes(packet.payload[2:4], byteorder='little')
        else:
            self.logger.error("<unknown packet> code: {}".format(command_code))
            return
        self.packet_queue.put_nowait(q)
        
