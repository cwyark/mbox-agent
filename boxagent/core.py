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
    def __init__(self, loop, queues, packet_queue, config):
        self.rx_queue, self.tx_queue = queues
        self.packet_queue = packet_queue
        self.loop = loop
        self.logger = logging.getLogger(__name__)
        self.device_list = list()
        self.heartbeat_counter = 0
        self.heartbeat_interval = int(config['default']['heartbeat'])
        device_list_config = config['default'].get('device_list')
        if device_list_config is not None:
            if type(device_list_config) is list:
                self.device_list = list(map(int, device_list_config))
            elif type(device_list_config) is str:
                self.device_list.append(int(device_list_config))
            else:
                pass
            self.logger.info("found pre-defined device list: {}".format(self.device_list))
        self.loop.call_soon(self.heartbeat)
    
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
                self.logger.error("<runner frame error> {}: <{}>".format(str(e), BasePacket.format_bytearray(frame)))

    def response_packet(self, packet):
        response_packet = packet.response_packet()
        self.logger.info("<reply packet> <{!s}>".format(response_packet))
        self.logger.debug("<reply frame> <{!r}>".format(response_packet))
        self.tx_queue.put_nowait(response_packet.frame)

    async def handle_heartbeat_timeout(self):
        self.logger.info("waiting for the heartbeat timeout")
        await asyncio.sleep(self.heartbeat_interval)
        self.logger.info("heartbeat timeout, log this")
        for device_id in self.device_list:
            q = dict()
            q['MBoxId'] = device_id
            q['RecordDate'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            q['EventCode'] = 3800
            q['SequentialNumber'] = 0
            q['ConnectionStatus']  = 0x02
            self.logger.info("putting timeout queue, {}".format(q))
            await self.packet_queue.put(q)


    def heartbeat(self):
        def _int_to_bcd(n):
            """
                Encode a one or two digits number to the BCD.
            """
            bcd = 0
            for i in (n // 10, n % 10):
                for p in (8, 4, 2, 1):
                    if i >= p:
                        bcd += 1
                        i -= p
                    bcd <<= 1
            return bcd >> 1
        self.logger.debug('heart beat')
        now = datetime.now()
        payload = Struct("<HBBBBBBBB").pack(3800, \
                _int_to_bcd(now.year - 2000), \
                _int_to_bcd(now.month), \
                _int_to_bcd(now.day), \
                _int_to_bcd(now.weekday() + 1), \
                _int_to_bcd(now.hour), \
                _int_to_bcd(now.minute), \
                _int_to_bcd(now.second), \
                1)
        for device_id in self.device_list:
            packet = BasePacket.builder(device_id, self.heartbeat_counter, payload = payload)
            self.logger.info("Building heartbeat packet for device : {}".format(device_id))
            self.tx_queue.put_nowait(packet.frame)
        self.heartbeat_counter += 1
        self.loop.call_later(self.heartbeat_interval, self.heartbeat)
        self.heartbeat_timeout_task = asyncio.ensure_future(self.handle_heartbeat_timeout())

    def dispatcher(self, packet):
        command_code = packet.command_code

        q = dict()

        q['MBoxId'] = packet.device_id
        q['RecordDate'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        q['EventCode'] = packet.command_code
        q['SequentialNumber'] = packet.counter+1

        if command_code == 1000:
            self.logger.info('get 1000 command: {!s}'.format(packet))
            self.logger.debug('get 1000 command: {!r}'.format(packet))
            # Record 3800's response
            _, response_code, result = Struct("<HHB").unpack(packet.payload)
            if response_code == 3800:
                q['ConnectionStatus'] = result
                q['EventCode'] = 3800
                if self.heartbeat_timeout_task is not None:
                    if not self.heartbeat_timeout_task.cancelled():
                        self.heartbeat_timeout_task.cancel()
                        self.heartbeat_timeout_task = None
                        self.logger.info("cancel the heartbeat timeout task")
                self.packet_queue.put_nowait(q)
        elif command_code == 1002:
            self.response_packet(packet)
            q['Mbox-model-and-Version'] = "'{!s}'".format(packet.payload[6:30].decode())
            if packet.device_id not in self.device_list:
                self.device_list.append(packet.device_id)
            self.packet_queue.put_nowait(q)
        elif command_code >= 3301 and command_code <= 3306:
            index = packet.command_code - 3300
            self.response_packet(packet)
            q["RfId{}".format(index)] = "{:x}".format(int.from_bytes(packet.payload[2:7], \
                    byteorder='big'))
            self.packet_queue.put_nowait(q)
        elif command_code >= 3100 and command_code <= 3105:
            index = packet.command_code + 1 - 3100
            self.response_packet(packet)
            q["Button{}".format(index)] = "{:d}".format(packet.payload[2])
            self.packet_queue.put_nowait(q)
        elif command_code == 3106:
            self.response_packet(packet)
            q["Sensor1"] = int.from_bytes(packet.payload[2:6], byteorder='little')
            self.packet_queue.put_nowait(q)
        elif command_code == 3201:
            self.response_packet(packet)
            q["Counter1"] = int.from_bytes(packet.payload[2:4], byteorder='little')
            self.packet_queue.put_nowait(q)
        else:
            self.logger.error("<unknown packet> code: {}".format(command_code))
            return
        

