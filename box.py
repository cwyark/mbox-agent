import os
import logging
import asyncio
import serial_asyncio
from asyncio import Queue
from datetime import datetime
from packet import RequestPacket, ResponsePacket

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
                self.logger.debug(self.buffer)
                # Need to alloc a new object to put in the queue
                self.queue.put_nowait(bytearray(self.buffer))
            else:
                self.logger.info("frame error")
            self.buffer.clear()
    def connection_lost(self, exc):
        self.logger.info("Connection lost")
        asyncio.get_event_loop.stop()

    async def consumer(self):
        self.datetime_now = datetime.now()
        self.file_counter = 0
        while True:
            frame = await self.queue.get()
            box_packet = RequestPacket(frame)

            now = datetime.now()
            if now.second % 10 == 0:
                self.datetime_now = now
                self.file_counter += 1

            if box_packet.crc_validate() is True:
                self.logger.info(box_packet)
                if box_packet.command_code == 1002:
                    global zigbee_device_list_cache
                    zigbee_id_int = int.from_bytes(box_packet.zigbee_id, byteorder='little')
                    if zigbee_id_int not in zigbee_device_list_cache:
                        zigbee_device_list_cache[zigbee_id_int] = 0
                    await self.response_packet(box_packet)

                if box_packet.command_code >= 3301 and box_packet.command_code <= 3306:
                    index = box_packet.command_code - 3300
                    self.logging_data("Mbox", "RfId{}".format(index), \
                            "{:x}".format(int.from_bytes(box_packet.payload[3:8], byteorder='little')), box_packet)
                    await self.response_packet(box_packet)

                if box_packet.command_code >= 3100 and box_packet.command_code <= 3105:
                    index = box_packet.command_code + 1 - 3100
                    self.logging_data("Mbox", "Button{}".format(index), \
                            "{:d}".format(box_packet.payload[3]), box_packet)
                    await self.response_packet(box_packet)

                if box_packet.command_code == 3106:
                    self.logging_data("Mbox", "Sensor1", \
                            int.from_bytes(box_packet.payload[3:7], byteorder='little'), box_packet)
                    await self.response_packet(box_packet)

                if box_packet.command_code == 3201:
                    self.logging_data("Mbox", "Counter1", \
                            int.from_bytes(box_packet.payload[3:5], byteorder='little'), box_packet)
                    await self.response_packet(box_packet)

            else:
                self.logger.info("crc validate failed, packet: {}".format(box_packet))

    async def response_packet(self, packet):
        payload = (1000).to_bytes(2, byteorder='little') + \
                (packet.command_code).to_bytes(2, byteorder='little') + \
                b'\x01'
        response_packet = ResponsePacket.builder(zigbee_id = packet.zigbee_id, \
                counter = packet.counter, payload = payload)
        self.logger.info("response {} packet: {}".format(packet.command_code, response_packet))
        self.logger.info("raw {}".format(response_packet.msg))
# Add 0.08 secs delay in case of the module would received faulty
        await asyncio.sleep(0.1)
        self.transport.write(response_packet.to_bytes)

    def logging_data(self, prefix, data_name, data, packet):
        filename = os.path.join(DATA_FILE_PATH_PREFIX, "{} {}-{}.txt".format( \
                prefix, \
                #int.from_bytes(packet.device_id, byteorder='big'), \
                self.datetime_now.strftime("%Y-%m-%d-%H-%M-%S")), \
                self.file_counter
                )
        with open(filename, "a+") as f:
            f.write("INSERT VALUE InputsTableRaspberry (MBoxId,RecordDate,EventCode,{},SequentialNumber) VALUES ({:x}, '{}', {}, {}, {})\n".format(data_name, \
                    int.from_bytes(packet.device_id, byteorder='big'), \
                    self.datetime_now.strftime("%Y-%m-%d %H:%M:%S"), \
                    packet.command_code, \
                    data, \
                    packet.counter
                    ))
