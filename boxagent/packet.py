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
        return "BasePacket DeviceID:0x{device_id:08x} TotalBytes:{total_bytes} Counter:{counter} Payload({payload}) CmdCode:{command_code} CRC:0x{crc:04x}".format(device_id=self.device_id, \
                total_bytes=self.total_bytes, counter=self.counter, payload=BasePacket.format_bytearray(self.payload), command_code=self.command_code, crc=self.crc)

    @property
    def command_code(self):
        return int.from_bytes(self.payload[0:2], byteorder='little')

    @classmethod
    def builder(cls, device_id, counter, payload=b'\x00\x00'):
        total_bytes = (1 + 4 + len(payload) + 2) & 0xFF
        buffer = bytearray(Struct("<BBLBLHBB").pack(0xAA, 0xD1, device_id, total_bytes, \
                counter, 0x00, 0xD0, 0x55))
        # Fill up payload
        buffer[11:11] = payload
        # Fill up CRC
        buffer[-4:-2] = crc(buffer[6:-4]).to_bytes(2, byteorder='little')
        return cls(buffer)

    def response_packet(self, result = True):
        # A workaround
        self.device_id = int.from_bytes(self.device_id.to_bytes(4, byteorder='little'), byteorder='big')
        payload = Struct("<HHB").pack(1000, self.command_code, result)
        return BasePacket.builder(device_id = self.device_id, \
                counter = self.counter, payload = payload)

    def unpack(self):
        payload = self.frame[11:-4]
        data = self.frame[:11] + self.frame[-4:]
        try:
            self.header_1, self.header_2, self.device_id, \
                    self.total_bytes, self.counter, self.crc, \
                    self.end_1, self.end_2 = Struct("<BBLBLHBB").unpack(data)
            # A workaround
            self.device_id = int.from_bytes(self.device_id.to_bytes(4, byteorder='little'), byteorder='big')
        except:
            self.logger.error("<payload deserialize not work>")
        self.payload = payload

    def crc_validate(self):
        if self.crc != crc(self.frame[6:-4]):
            # For some cases, crc value might be as the same as D0 55
            return True if self.crc == crc(self.frame[6:-2]) else False
        else:
            return True
