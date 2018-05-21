import os
import logging
import asyncio
import serial_asyncio
from crc import crc
from asyncio import Queue
from datetime import datetime

# Set up default timeout 
SERIAL_RECV_TIMEOUT = 1.5 # seconds

DATA_FILE_PATH_PREFIX = "/home/pi/Desktop/BoxData"

class BoxPacket:
    def __init__(self, msg):
        self.msg = msg
        self.logger = logging.getLogger('box.BoxPacket')
        if type(msg) != bytearray:
            raise ValueError("BOXPacket: msg type is not bytes")

    def __repr__(self):
        return "<ZigbeeID>{zigbee_id}, <TotalBytes>{total_bytes}, <DeviceID>{device_id}, <counter>{counter}, <payload>{payload}, <crc>{crc}".format(zigbee_id=self.zigbee_id, total_bytes=self.total_bytes, device_id=self.device_id, counter=self.counter, payload=self.payload, crc=self.crc)
    
    @classmethod
    def builder(cls, zigbee_id, device_id, counter, payload=b'\x00\x00'):
        buffer = bytearray(12)
        # start bytes 0xaa 0xd1 (byte 0 ~ 1)
        buffer[0:2] = b'\xaa\xd1'
        # zigbee id byte 2 ~ 3
        buffer[2:4] = zigbee_id
        # total bytes  byte 4 (total byte 1B + zigbee id 4B + device id 4B + payload 2 ~ 128B) & 0xFF
        buffer[4:4] = ((1+4+4+len(payload)+2)&0xFF).to_bytes(1, byteorder='little')
        # device id byte 5 ~ 8
        buffer[5:9] = device_id
        # counter byte 9 ~ 12 
        buffer[9:13] = counter.to_bytes(4, byteorder='little')
        # payload start from byte 13
        buffer[13:13] = payload
        # crc 
        buffer += (crc(buffer[4:])).to_bytes(2, byteorder='little')
        # end bytes
        buffer += b'\x0d\x55'
        return cls(buffer)

    @property
    def head(self):
        return self.msg[0:2]
    
    @property
    def zigbee_id(self):
        return self.msg[2:4]
    
    @property
    def total_bytes(self):
        return self.msg[4]
    
    @property
    def device_id(self):
        return self.msg[5:9]

    @property
    def counter(self):
        return int.from_bytes(self.msg[9:13], byteorder='little')

    @property
    def crc(self):
        return int.from_bytes(self.msg[-4:-2], byteorder='little')

    def crc_validate(self):
        return (self.crc == crc(self.msg[4:-4]))

    @property
    def payload(self):
        data = self.msg[13:-4]
        return data

    @property
    def end(self):
        return self.msg[-2]
    
    @property
    def command_code(self):
        payload = self.payload
        return int.from_bytes(payload[0:2], byteorder='little')
    
    @property
    def to_bytes(self):
        return bytes(self.msg)


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
        while True:
            frame = await self.queue.get()
            box_packet = BoxPacket(frame)
            if box_packet.crc_validate() is True:
                self.logger.info(box_packet)
                if box_packet.command_code == 1002:
                    await self.response_packet(box_packet)

                if box_packet.command_code >= 3301 and box_packet.command_code <= 3306:
                    index = box_packet.command_code - 3300
                    self.logging_data("RFID", "Rfid{}".format(index), \
                            "{:x}".format(int._from_bytes(box_packet.payload[3:8], byteorder='little')), box_packet)
                    await self.response_packet(box_packet)

                if box_packet.command_code >= 3100 and box_packet.command_code <= 3105:
                    index = box_packet.command_code + 1 - 3100
                    self.logging_data("BUTTON", "Button{}".format(index), \
                            "{:d}".format(box_packet.payload[3]), box_packet)
                    await self.response_packet(box_packet)

                if box_packet.command_code == 3106:
                    self.logging_data("SENSOR", "Sensor1", \
                            int.from_bytes(box_packet.payload[3:7], byteorder='little'), box_packet)
                    await self.response_packet(box_packet)

                if box_packet.command_code == 3201:
                    self.logging_data("COUNTER", "Counter1", \
                            int.from_bytes(box_packet.payload[3:5], byteorder='little'), box_packet)
                    await self.response_packet(box_packet)

            else:
                self.logger.info("crc validate failed, packet: {}".format(box_packet))

    async def response_packet(self, packet):
        payload = (1000).to_bytes(2, byteorder='little') + \
                (packet.command_code).to_bytes(2, byteorder='little') + \
                b'\x01'
        response_packet = BoxPacket.builder(zigbee_id = packet.zigbee_id, \
                device_id = packet.device_id, \
                counter = packet.counter, payload = payload)
        self.logger.info("response {} packet: {}".format(packet.command_code, response_packet))
        self.transport.write(response_packet.to_bytes)

    def logging_data(self, prefix, data_name, data, packet):
        now = datetime.now()
        filename = os.path.join(DATA_FILE_PATH_PREFIX, "{}_{:x}-{}.txt".format( \
                prefix, \
                int.from_bytes(packet.device_id, byteorder='big'), \
                now.strftime("%Y_%m_%d_%H_%M"))
                )
        with open(filename, "a+") as f:
            f.write("INSERT VALUE InputsTableRaspberry (MBoxId,RecordDate,EventCode,{},SequentialNumber) VALUES ('{:x}', '{}', {}, {}, {})\n".format(data_name, \
                    int.from_bytes(packet.zigbee_id, byteorder='big'), \
                    now.strftime("%Y-%m-%d %H:%M:%S"), \
                    packet.command_code, \
                    data, \
                    packet.counter
                    ))
