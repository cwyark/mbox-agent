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
DATA_LOG_FORMAT = "INSERT INTO InputsTableRaspberry (MBoxId,ZigbeeId,RecordDate,EventCode,{},SequentialNumber) VALUE ('{:x}', '{:x}', '{}', {}, {}, {})\n"

zigbee_device_list_cache = dict()

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
        if b'\x55' in data and b'\x0d' in self.buffer:
            if self.buffer[0] in b'\xaa' and self.buffer[1] in b'\xd1':
                # Need to alloc a new object to put in the queue
                self.queue.put_nowait(bytearray(self.buffer))
            else:
                self.logger.info("[EVT]<PKT> [CAUSE]<frame error> [MSG]<{}>".format(' '.join('{:02}'.format(x) for x in self.buffer)))
            self.buffer.clear()

    def connection_lost(self, exc):
        asyncio.get_event_loop.stop()

    async def response_packet(self, packet):
        payload = Struct("<HHB").pack(1000, packet.command_code, 1)
        response_packet = ResponsePacket.builder(zigbee_id = packet.zigbee_id, \
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
                while self.sql_queue.empty() is not True:
                    q = self.sql_queue.get_nowait()
                    self.logger.info("[EVT]<SQL> [CAUSE]<get q> [MSG]<{}>".format(q))
                    with open(os.path.join(DATA_FILE_PATH_PREFIX, file_name), "a+") as f:
                        f.write(q)
                        self.logger.info("[EVT]<SQL> [CAUSE]<write to file> [MSG]<{}>".format(file_name))

    async def consumer(self):
        while True:
            frame = await self.queue.get()
            packet = RequestPacket(frame)
            self.logger.info("[EVT]<PKT> [CAUSE]<got message> [MSG]<{!s}> [RAW]<{!r}>".format(packet, packet))
            if packet.crc_validate() is True:

                if packet.command_code == 1002:
                    global zigbee_device_list_cache
                    if packet.zigbee_id not in zigbee_device_list_cache:
                        zigbee_device_list_cache[packet.zigbee_id] = 0
                    await self.response_packet(packet)

                    SQL_STMT = DATA_LOG_FORMAT.format(\
                            "Mbox-model-and-Version", \
                            packet.device_id,\
                            packet.zigbee_id, \
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), \
                            packet.command_code, \
                            "'{!s}'".format(packet.payload[2:30].decode()), \
                            packet.counter
                        )
                    self.sql_queue.put_nowait(SQL_STMT)

                if packet.command_code >= 3301 and packet.command_code <= 3306:
                    index = packet.command_code - 3300
                    await self.response_packet(packet)

                    SQL_STMT = DATA_LOG_FORMAT.format(\
                            "RfId{}".format(index), \
                            packet.device_id,\
                            packet.zigbee_id, \
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), \
                            packet.command_code, \
                            "{:x}".format(int.from_bytes(packet.payload[2:7], byteorder='big')), \
                            packet.counter
                        )
                    self.sql_queue.put_nowait(SQL_STMT)

                if packet.command_code >= 3100 and packet.command_code <= 3105:
                    index = packet.command_code + 1 - 3100
                    await self.response_packet(packet)

                    SQL_STMT = DATA_LOG_FORMAT.format(\
                            "Button{}".format(index), \
                            packet.device_id,\
                            packet.zigbee_id, \
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), \
                            packet.command_code, \
                            "{:d}".format(packet.payload[2]), \
                            packet.counter
                        )
                    self.sql_queue.put_nowait(SQL_STMT)

                if packet.command_code == 3106:
                    await self.response_packet(packet)

                    SQL_STMT = DATA_LOG_FORMAT.format(\
                            "Sensor1", \
                            packet.device_id,\
                            packet.zigbee_id, \
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), \
                            packet.command_code, \
                            int.from_bytes(packet.payload[2:6], byteorder='little'), \
                            packet.counter
                        )
                    self.sql_queue.put_nowait(SQL_STMT)

                if packet.command_code == 3201:
                    await self.response_packet(packet)

                    SQL_STMT = DATA_LOG_FORMAT.format(\
                            "Counter1", \
                            packet.device_id,\
                            packet.zigbee_id, \
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), \
                            packet.command_code, \
                            int.from_bytes(packet.payload[2:4], byteorder='little'), \
                            packet.counter
                        )
                    self.sql_queue.put_nowait(SQL_STMT)

                self.logger.info("[EVT]<SQL> [CAUSE]<none> [MSG]<{}>".format(SQL_STMT))

            else:
                self.logger.info("[EVT]<SQL> [CAUSE]<CRC Error> [MSG]<{!r}>".format(packet))
