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

class BOXPacket:
    def __init__(self, msg):
        self.msg = msg
        self.logger = logging.getLogger('box.BoxPacket')
        if type(msg) != bytes:
            raise ValueError("BOXPacket: msg type is not bytes")
        
    @property
    def end(self):
        """
        The end character of the end of message
        """
        return self.msg[-1]

    @property
    def head(self):
        """
        The head character of the start message
        """
        return self.msg[0]
    
    @property
    def count(self):
        """
        The counter of this message, range will be from 
        0x00000001 to 0xFFFFFFFF
        """
        return int(self.msg[1:5])


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
            else:
                logging.info("frame error")
            self.buffer.clear()
    def connection_lost(self, exc):
        self.logger.info("Connection lost")
        asyncio.get_event_loop.stop()
