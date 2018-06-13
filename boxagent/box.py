import os
import logging
import asyncio
import json
from asyncio import Queue
from datetime import datetime
from struct import Struct, pack, unpack
from .crc import crc
from .packet import RequestPacket, ResponsePacket

# Set up default timeout 
SERIAL_RECV_TIMEOUT = 1.5 # seconds

DATA_FILE_PATH_PREFIX = "/home/pi/Desktop/BoxData"
DATA_LOG_FORMAT = "INSERT INTO InputsTableRaspberry (MBoxId,RecordDate,EventCode,{},SequentialNumber) VALUES ('{:x}', '{}', {}, {}, {})\n"

device_list_cache = dict()

class BoxPacketReceiver(asyncio.Protocol):
    buffer = bytearray()
    def connection_made(self, transport):
        self.logger = logging.getLogger(__name__)
        self.transport = transport
        self.queue = Queue()
        self.sql_queue = Queue()
        self.transport.loop.create_task(self.consumer())
        self.transport.loop.create_task(self.data_logger_task())
        directory = os.path.dirname(DATA_FILE_PATH_PREFIX)
        if not os.path.exists(DATA_FILE_PATH_PREFIX):
            self.logger.debug("[EVT]<LOGGING> [CAUSE]<none> [MSG]<{} not found, create a new one>".format(DATA_FILE_PATH_PREFIX))
            os.makedirs(DATA_FILE_PATH_PREFIX)

    def data_received(self, data):
        self.buffer += data
        if b'\x55' in data and b'\xd0' in self.buffer:
            if self.buffer[0] in b'\xaa' and self.buffer[1] in b'\xd1':
                # Need to alloc a new object to put in the queue
                if b'\xaa\xd1\x80\x03\x11\x55' in self.buffer or b'\xaa\xd1\x80\x05\x11\x55' in self.buffer:
                    # A wrokaround because some times module send out aa d1 80 03 11 55 
                    self.buffer = self.buffer[6:]
                self.queue.put_nowait(bytearray(self.buffer))
            else:
                self.logger.error("[EVT]<PKT> [CAUSE]<frame error> [MSG]<{}>".format(' '.join('{:02}'.format(x) for x in self.buffer)))
            self.buffer.clear()

    def connection_lost(self, exc):
        asyncio.get_event_loop.stop()

    async def response_packet(self, packet):
        payload = Struct("<HHB").pack(1000, packet.command_code, 1)
        response_packet = ResponsePacket.builder(device_id = packet.device_id, \
                counter = packet.counter, payload = payload)
        self.logger.info("[EVT]<PKT> [CAUSE]<reply message> [MSG]<{!s}> [RAW]<{!r}>".format(response_packet, response_packet))
# Add 0.2 secs delay in case of the zigbee module would received faulty
        await asyncio.sleep(0.2)
        self.transport.write(response_packet.frame)

    async def data_logger_task(self):
        self.file_counter = 0
        while True:
            now = datetime.now()
            await asyncio.sleep(0.7)
            if now.second % 10 == 0:
                file_name = "Mbox {}-{}.txt".format( \
                        now.strftime("%Y-%m-%d-%H-%M-%S"), \
                        self.file_counter
                        )
                if self.sql_queue.empty() is not True:
                    self.file_counter += 1
                    q_list = []
                    while self.sql_queue.empty() is not True:
                        q = self.sql_queue.get_nowait()
                        q_list.append(q)
                        self.logger.info("[EVT]<SQL> [CAUSE]<get q> [MSG]<{}>".format(q))
                    with open(os.path.join(DATA_FILE_PATH_PREFIX, file_name), "a+") as f:
                        f.write(json.dumps(q_list))
                        self.logger.info("[EVT]<SQL> [CAUSE]<write to file> [MSG]<{}>".format(file_name))

    async def consumer(self):
        while True:
            frame = await self.queue.get()
            try:
                packet = RequestPacket(frame)
                self.logger.info("[EVT]<PKT> [CAUSE]<got message> [MSG]<{!s}> [RAW]<{!r}>".format(packet, packet))
                if packet.crc_validate() is True:

                    q = dict()

                    if packet.command_code == 1002:
                        global device_list_cache
                        if packet.device_id not in device_list_cache:
                            device_list_cache[packet.device_id] = 0
                        await self.response_packet(packet)

                        q['MBoxId'] = packet.device_id
                        q['RecordDate'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        q['EventCode'] = packet.command_code
                        q['Mbox-model-and-Version'] = "'{!s}'".format(packet.payload[2:27].decode())
                        q['SequentialNumber'] = packet.counter

                    if packet.command_code >= 3301 and packet.command_code <= 3306:
                        index = packet.command_code - 3300
                        await self.response_packet(packet)

                        q['MBoxId'] = packet.device_id
                        q['RecordDate'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        q['EventCode'] = packet.command_code
                        q["RfId{}".format(index)] = "{:x}".format(int.from_bytes(packet.payload[2:7], byteorder='big'))
                        q['SequentialNumber'] = packet.counter


                    if packet.command_code >= 3100 and packet.command_code <= 3105:
                        index = packet.command_code + 1 - 3100
                        await self.response_packet(packet)

                        q['MBoxId'] = packet.device_id
                        q['RecordDate'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        q['EventCode'] = packet.command_code
                        q["Button{}".format(index)] = "{:d}".format(packet.payload[2])
                        q['SequentialNumber'] = packet.counter

                    if packet.command_code == 3106:
                        await self.response_packet(packet)

                        q['MBoxId'] = packet.device_id
                        q['RecordDate'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        q['EventCode'] = packet.command_code
                        q["Sensor1"] = int.from_bytes(packet.payload[2:6], byteorder='little')
                        q['SequentialNumber'] = packet.counter

                    if packet.command_code == 3201:
                        await self.response_packet(packet)

                        q['MBoxId'] = packet.device_id
                        q['RecordDate'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        q['EventCode'] = packet.command_code
                        q["Counter1"] = int.from_bytes(packet.payload[2:4], byteorder='little')
                        q['SequentialNumber'] = packet.counter

                    self.sql_queue.put_nowait(q)

                    self.logger.info("[EVT]<SQL> [CAUSE]<none> [MSG]<{}>".format(q))

                else:
                    self.logger.error("[EVT]<SQL> [CAUSE]<CRC error> [MSG]<{!r}>".format(packet))
            except Exception as e:
                self.logger.error("[EVT]<PKT> [CAUSE]<loop exception> [MSG]<{!s}>", str(e))
