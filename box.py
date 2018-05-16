import logging
import asyncio
import serial_asyncio

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
        self.logger.info("<head>{head}, <ZigbeeID>{zigbee_id}, <TotalBytes>{total_bytes}, <DeviceID>{device_id}, <CRC>{crc}, <end>{end}".format(head=self.head, zigbee_id=self.zigbee_id, total_bytes=self.total_bytes, device_id=self.device_id, crc=self.crc, end=self.end))
        
    @property
    def end(self):
        """
        The end character of the end of message
        """
        return self.msg[-2]

    @property
    def head(self):
        """
        The head characters of the start message
        """
        return self.msg[0:2]
    
    @property
    def zigbee_id(self):
        id = self.msg[2:4]
        return int.from_bytes(id, byteorder='little')
    
    @property
    def total_bytes(self):
        return self.msg[4]
    
    @property
    def device_id(self):
        id = int.from_bytes(self.msg[5:9])
        return id

    @property
    def counter(self):
        """
        The counter of this message, range will be from 
        0x00000001 to 0xFFFFFFFF
        """
        return int.from_bytes(self.msg[9:13], byteorder='little')

    @property
    def crc(self):
        return int.from_bytes(self.msg[-4:-2], byteorder='little')


class BoxPacketReceiver(asyncio.Protocol):
    buffer = bytearray()
    def connection_made(self, transport):
        self.logger = logging.getLogger('box.BoxPacketReceiver')
        self.logger.info("Connection made")
        self.transport = transport
    def data_received(self, data):
        self.buffer += data
        if b'\x55' in data:
            if self.buffer[0] in b'\xaa' and self.buffer[1] in b'\xd1':
                print(self.buffer)
                box_packet = BoxPacket(self.buffer)
                print(box_packet)
            else:
                self.logger.info("frame error")
            self.buffer.clear()
    def connection_lost(self, exc):
        self.logger.info("Connection lost")
        asyncio.get_event_loop.stop()
