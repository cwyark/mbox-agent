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

    @classmethod
    def builder(cls, device_id, counter, payload=b'\x00\x00'):
        # A workaround
        device_id = int.from_bytes(device_id.to_bytes(4, byteorder='little'), byteorder='big')
        total_bytes = (1 + 4 + len(payload) + 2) & 0xFF
        buffer = bytearray(Struct("<BBLBLHBB").pack(0xAA, 0xD1, device_id, total_bytes, \
                counter, 0x00, 0xD0, 0x55))
        # Fill up payload
        buffer[11:11] = payload
        # Fill up CRC
        buffer[-4:-2] = crc(buffer[6:-4]).to_bytes(2, byteorder='little')
        return cls(buffer)

    def unpack(self):
        payload = self.frame[4:-4]
        data = self.frame[:4] + self.frame[-4:]
        try:
            self.header_1, self.header_2, self.device_id, \
                    self.total_bytes, self.counter, self.crc, \
                    self.end = Struct("<BBLBLHBB").unpack(data)
        except:
            self.logger.error("<payload deserialize not work>")
        self.payload = payload
