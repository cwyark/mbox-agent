import logging
from .crc import crc
from struct import Struct, pack, unpack

class BasePacket:
    def __init__(self, frame):
        self.frame = frame
        self.logger = logging.getLogger(__name__)
        if type(frame) != bytearray:
            raise ValueError("<BasePacket: frame type is not bytearray>")
        self.unpack()

    def __repr__(self):
        return BasePacket.format_bytearray(self.frame)

    @classmethod
    def format_bytearray(cls, buf):
        return ' '.join('{:02x}'.format(x) for x in buf)

    def __str__(self):
        return "RFID EventCode:{event_code} Value:{value}".format(event_code=self.event_code, value=self.value)

    def unpack(self):
        payload = self.frame[5:-2]
        data = self.frame[:5] + self.frame[-2:]
        try:
            self.header, self.event_code, self.end =  \
                    Struct("<LBH").unpack(data)
            self.value = payload.decode('ascii')
        except:
            self.logger.error("<frame deserialize not work>")

