import logging
from crc import crc
from struct import Struct, pack, unpack

class BasePacket:
    def __init__(self, frame):
        self.frame = frame
        self.logger = logging.getLogger('packet.BasePacket')
        if type(frame) != bytearray:
            raise ValueError("BasePacket: frame type is not bytearray")
        self.unpack()


    def __repr__(self):
        return ' '.join('{:02x}'.format(x) for x in self.frame)

    def __str__(self):
        return "BasePacket <ZigbeeID>0x{zigbee_id:x}, <TotalBytes>{total_bytes}, <DeviceID>{device_id:x}, <Counter>{counter}, <Payload>{payload}, <CRC>0x{crc:x}".format(zigbee_id=self.zigbee_id, \
                total_bytes=self.total_bytes, device_id=self.device_id, counter=self.counter, \
                payload=self.payload, crc=self.crc)

    def unpack(self):
        payload = self.frame[13:-4]
        data = self.frame[:13] + self.frame[-4:]
        self.header_1, self.header_2, self.zigbee_id, self.total_bytes, \
                self.device_id, self.counter, self.crc, self.end_1, \
                self.end_2 = Struct("<BBHBLLHBB").unpack(data)
        self.payload = payload

    def crc_validate(self):
        return (self.crc == crc(self.frame[4:-4]))


class RequestPacket(BasePacket):

    def __str__(self):
        return "RequestPacket  <ZigbeeID>0x{zigbee_id:04x}  <TotalBytes>{total_bytes}  <DeviceID>0x{device_id:08x}  <Counter>{counter}  <Command>{command}  <Payload>{payload}  <CRC>0x{crc:04x}".format(zigbee_id=self.zigbee_id, \
                total_bytes=self.total_bytes, device_id=self.device_id, counter=self.counter, \
                command=self.command_code, payload=self.payload, crc=self.crc)

    @classmethod
    def builder(cls, zigbee_id, device_id, counter, payload=b'\x00\x00'):
        total_bytes = (1 + 4 + 4 + len(payload) + 2 ) & 0xFF
        buffer = bytearray(Struct("<BBHBLLHBB").pack(0xAA, 0xD1, zigbee_id, total_bytes, \
                device_id, counter, 0x00, 0x0D, 0x55))
        # Fill up payload
        buffer[13:13] = payload
        # Fill up CRC
        buffer[-4:-2] = crc(buffer[4:-4]).to_bytes(2, byteorder='little')
        return cls(buffer)

    def unpack(self):
        payload = self.frame[13:-4]
        data = self.frame[:13] + self.frame[-4:]
        self.header_1, self.header_2, self.zigbee_id, self.total_bytes, \
                self.device_id, self.counter, self.crc, self.end_1, \
                self.end_2 = Struct("<BBHBLLHBB").unpack(data)
        self.payload = payload
# a workaround
        self.zigbee_id = int.from_bytes(self.zigbee_id.to_bytes(2, byteorder='little'), byteorder='big')
        self.device_id = int.from_bytes(self.device_id.to_bytes(4, byteorder='little'), byteorder='big')
    
    @property
    def command_code(self):
        return int.from_bytes(self.payload[0:2], byteorder='little')

class ResponsePacket(BasePacket):

    def __str__(self):
        return "ResponsePacket  <ZigbeeID>0x{zigbee_id:04x}  <TotalBytes>{total_bytes}  <Counter>{counter}  <Command>{command_code}  <ReplyCode>{reply_code}  <CRC>0x{crc:04x}".format(zigbee_id=self.zigbee_id, \
                total_bytes=self.total_bytes, counter=self.counter, \
                command_code=self.command_code, reply_code=self.reply_code, crc=self.crc)

    @classmethod
    def builder(cls, zigbee_id, counter, payload=b'\x00\x00'):
        total_bytes = (1 + 4 + len(payload) + 2 ) & 0xFF
        buffer = bytearray(Struct("<BBHBLHBB").pack(0xAA, 0xD1, zigbee_id, total_bytes, \
                    counter, 0x00, 0x0D, 0x55))
        # Fill up payload
        buffer[9:9] = payload
        # Fill up CRC
        buffer[-4:-2] = crc(buffer[4:-4]).to_bytes(2, byteorder='little')
        return cls(buffer)

    def unpack(self):
        payload = self.frame[9:-4]
        data = self.frame[:9] + self.frame[-4:]
        self.header_1, self.header_2, self.zigbee_id, self.total_bytes, \
                self.counter, self.crc, self.end_1, \
                self.end_2 = Struct("<BBHBLHBB").unpack(data)
        self.payload = payload
# A workaround
        self.zigbee_id = int.from_bytes(self.zigbee_id.to_bytes(2, byteorder='little'), byteorder='big')

    @property
    def command_code(self):
        return int.from_bytes(self.payload[0:2], byteorder='little')

    @property
    def reply_code(self):
        return int.from_bytes(self.payload[2:4], byteorder='little')
