import os
import logging
import asyncio
import serial_asyncio
from asyncio import Queue
from datetime import datetime
from packet import RequestPacket, ResponsePacket
from struct import Struct, pack, unpack

# Set up default timeout 
SERIAL_RECV_TIMEOUT = 1.5 # seconds

DATA_FILE_PATH_PREFIX = "/home/pi/Desktop/BoxData"

zigbee_device_list_cache = dict()

class BoxPacketReceiver(asyncio.Protocol):
    buffer = bytearray()
    def connection_made(self, transport):
        self.logger = logging.getLogger('box.BoxPacketReceiver')
        self.logger.info("Connection made")
        self.transport = transport
        self.queue = Queue()
        self.transport.loop.create_task(self.consumer())
        directory = os.path.dirname(DATA_FILE_PATH_PREFIX)
        if not os.path.exists(DATA_FILE_PATH_PREFIX):
            self.logger.info("{} not found, create a new one".format(DATA_FILE_PATH_PREFIX))
            os.makedirs(DATA_FILE_PATH_PREFIX)

    def data_received(self, data):
        self.buffer += data
        if b'\x55' in data and b'\x0d' in self.buffer:
            if self.buffer[0] in b'\xaa' and self.buffer[1] in b'\xd1':
                # Need to alloc a new object to put in the queue
                self.queue.put_nowait(bytearray(self.buffer))
            else:
                self.logger.info("frame error")
            self.buffer.clear()

    def connection_lost(self, exc):
        self.logger.info("Connection lost")
        asyncio.get_event_loop.stop()

    async def consumer(self):
        while True:
            frame = await self.queue.get()
            packet = RequestPacket(frame)
            self.logger.info("===> {:r}".format(packet))
            self.logger.info("request {:s}".format(packet))
            if packet.crc_validate() is True:
                if packet.command_code == 1002:
                    global zigbee_device_list_cache
                    if packet.zigbee_id not in zigbee_device_list_cache:
                        zigbee_device_list_cache[packet.zigbee_id] = 0
                    await self.response_packet(packet)

                if packet.command_code >= 3301 and packet.command_code <= 3306:
                    index = packet.command_code - 3300
                    await self.response_packet(packet)

                if packet.command_code >= 3100 and packet.command_code <= 3105:
                    index = packet.command_code + 1 - 3100
                    await self.response_packet(packet)

                if packet.command_code == 3106:
                    await self.response_packet(packet)

                if packet.command_code == 3201:
                    await self.response_packet(packet)

            else:
                self.logger.info("CRC , packet: {}".format(packet))

    async def response_packet(self, packet):
        payload = Struct("<HHB").pack(1000, packet.command_code, 1)
        response_packet = ResponsePacket.builder(zigbee_id = packet.zigbee_id, \
                counter = packet.counter, payload = payload)
        self.logger.info("response {:s}".format(response_packet))
        self.logger.info("<=== {:r}".format(response_packet))
# Add 0.1 secs delay in case of the zigbee module would received faulty
        await asyncio.sleep(0.1)
        self.transport.write(response_packet.frame)

    def logging_data(self, prefix, data_name, data, packet):
        self.file_counter += 1
        filename = os.path.join(DATA_FILE_PATH_PREFIX, "{} {}-{}.txt".format( \
                prefix, \
                self.datetime_now.strftime("%Y-%m-%d-%H-%M-%S"), \
                self.file_counter 
                ))
        with open(filename, "a+") as f:
            f.write("INSERT VALUE InputsTableRaspberry (MBoxId,RecordDate,EventCode,{},SequentialNumber) VALUES ({:x}, '{}', {}, {}, {})\n".format(data_name, \
                    int.from_bytes(packet.device_id, byteorder='big'), \
                    self.datetime_now.strftime("%Y-%m-%d %H:%M:%S"), \
                    packet.command_code, \
                    data, \
                    packet.counter
                    ))
