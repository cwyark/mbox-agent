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
        # self.logger.info(BasePacket.format_bytearray(payload))
        # self.logger.info(BasePacket.format_bytearray(data))
        try:
            self.header, self.event_code, self.end =  \
                    Struct("<LBH").unpack(data)
            self.value = str(int(payload.decode("ascii")))
            if self.event_code == 0x35:
                self.event_code = 3301
            elif self.event_code == 0x36:
                self.event_code = 3302
            elif self.event_code == 0x37:
                self.event_code = 3303
            elif self.event_code == 0x38:
                self.event_code = 3304
            elif self.event_code == 0x39:
                self.event_code = 3305
            elif self.event_code == 0x41:
                self.event_code = 3306
            elif self.event_code == 0x42:
                self.event_code = 3307
            elif self.event_code == 0x43:
                self.event_code = 3308
            else:
                pass
        except:
            self.logger.error("<frame deserialize not work>")

