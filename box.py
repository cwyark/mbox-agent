import logging
import asyncio
import serial_asyncio
from collections import deque

# Set up the logging subsystem
logging.basicConfig(level=logging.DEBUG, 
        format="%(asctime)s %(name)-12s %(levelname)-8s $(message)", 
        datefmt="%m-%d %H:%M",
        handlers = [logging.FileHandler('box.log', 'w', 'utf-8'),]
        )

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# Set up default timeout 
SERIAL_RECV_TIMEOUT = 1.5 # seconds

class BoxPacket:
    def __init__(self, msg):
        self.msg = msg
        self.logger = logging.getLogger('box.BoxPacket')
        if type(msg) != bytearray:
            raise ValueError("BOXPacket: msg type is not bytes")

    def __repr__(self):
        return "<ZigbeeID>{zigbee_id}, <TotalBytes>{total_bytes}, <DeviceID>{device_id}, <CRC>{crc}, <payload>{payload}".format(zigbee_id=self.zigbee_id, total_bytes=self.total_bytes, device_id=self.device_id, crc=self.crc, payload=self.payload)
        
    @property
    def head(self):
        return self.msg[0:2]
    
    @property
    def zigbee_id(self):
        #id = self.msg[2:4]
        #return int.from_bytes(id, byteorder='little')
        return self.msg[2:4].hex()
    
    @property
    def total_bytes(self):
        return self.msg[4]
    
    @property
    def device_id(self):
        #id = int.from_bytes(self.msg[5:9], byteorder='little')
        return self.msg[5:9].hex()

    @property
    def counter(self):
        return int.from_bytes(self.msg[9:13], byteorder='little')

    @property
    def crc(self):
        return int.from_bytes(self.msg[-4:-2], byteorder='little')

    @property
    def payload(self):
        data = self.msg[13:-4]
        return data

    @property
    def end(self):
        return self.msg[-2]


class BoxPacketReceiver(asyncio.Protocol):
    buffer = bytearray()
    def connection_made(self, transport):
        self.logger = logging.getLogger('box.BoxPacketReceiver')
        self.logger.info("Connection made")
        self.transport = transport
        self.queue = deque()
        asyncio.Task(self.cusumer())
    def data_received(self, data):
        self.buffer += data
        if b'\x55' in data:
            if self.buffer[0] in b'\xaa' and self.buffer[1] in b'\xd1':
                self.logger.debug(self.buffer)
                box_packet = BoxPacket(self.buffer)
                self.logger.info(box_packet)
                self.queue.append(box_packet)
            else:
                self.logger.info("frame error")
            self.buffer.clear()
    def connection_lost(self, exc):
        self.logger.info("Connection lost")
        asyncio.get_event_loop.stop()

    def cusumer(self):
        while True:
            data = self.queue.pop()
            self.logger.info(data)
            await asyncio.sleep(1)
