import logging
import asyncio
import serial_asyncio
from asyncio import Queue

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
        return "<ZigbeeID>{zigbee_id}, <TotalBytes>{total_bytes}, <DeviceID>{device_id}, <counter>{counter}, <payload>{payload}, <crc>{crc}".format(zigbee_id=self.zigbee_id, total_bytes=self.total_bytes, device_id=self.device_id, counter=self.counter, payload=self.payload, crc=self.crc)
    
    @classmethod
    def builder(cls, zigbee_id, device_id, counter, payload=b'\x00\x00'):
        buffer = bytearray(12)
        buffer[0:2] = b'\xaa\xd1'
        buffer[2:4] = zigbee_id
        buffer[4:4] = ((1+4+4+len(payload)+2)&0xFF).to_bytes(1, byteorder='little')
        buffer[5:9] = device_id
        buffer[9:13] = counter.to_bytes(4, byteorder='little')
        buffer[13:13] = payload
        buffer += (1024).to_bytes(2, byteorder='little')
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


class BoxPacketReceiver(asyncio.Protocol):
    buffer = bytearray()
    def connection_made(self, transport):
        self.logger = logging.getLogger('box.BoxPacketReceiver')
        self.logger.info("Connection made")
        self.transport = transport
        self.queue = Queue()
        asyncio.ensure_future(self.dispatch_packet_worker())
    def data_received(self, data):
        self.buffer += data
        if b'\x55' in data:
            if self.buffer[0] in b'\xaa' and self.buffer[1] in b'\xd1':
                self.logger.debug(self.buffer)
                box_packet = BoxPacket(self.buffer)
                self.logger.info(box_packet)
                self.queue.put_nowait(box_packet)
                self.response(box_packet)
            else:
                self.logger.info("frame error")
            self.buffer.clear()
    def connection_lost(self, exc):
        self.logger.info("Connection lost")
        asyncio.get_event_loop.stop()

    def response(self, packet):
        logger = logging.getLogger('box.response')
        code = packet.command_code
        if code == 1002:
            response_paket = BoxPacket.builder(zigbee_id = packet.zigbee_id, device_id = packet.device_id, counter = packet.counter, payload=b'\xaa\xbb\xcc\xdd')
            logger.debug(response_paket)
            logger.debug(response_paket.msg)

    async def dispatch_packet_worker(self):
        while True:
            data = await self.queue.get()
