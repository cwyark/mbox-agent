import logging
from crc import crc

class BasePacket:
    def __init__(self, msg):
        self.msg = msg
        self.logger = logging.getLogger('packet.BasePacket')
        if type(msg) != bytearray:
            raise ValueError("BasePacket: msg type is not bytearray")

    def __repr__(self):
        return "<ZigbeeID>{zigbee_id}, <TotalBytes>{total_bytes}, <DeviceID>{device_id}, <counter>{counter}, <payload>{payload}, <crc>{crc}".format(zigbee_id=self.zigbee_id, total_bytes=self.total_bytes, device_id=self.device_id, counter=self.counter, payload=self.payload, crc=self.crc)
    
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
    def to_bytes(self):
        return bytes(self.msg)

class RequestPacket(BasePacket):

    def __repr__(self):
        return "RequestPacket<ZigbeeID>{zigbee_id}, <TotalBytes>{total_bytes}, <DeviceID>{device_id}, <counter>{counter}, <payload>{payload}, <crc>{crc}".format(zigbee_id=self.zigbee_id, total_bytes=self.total_bytes, device_id=self.device_id, counter=self.counter, payload=self.payload, crc=self.crc)
    
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

class ResponsePacket(BasePacket):

    def __repr__(self):
        return "ResponsePacket<ZigbeeID>{zigbee_id}, <TotalBytes>{total_bytes}, <counter>{counter}, <payload>{payload}, <crc>{crc}".format(zigbee_id=self.zigbee_id, total_bytes=self.total_bytes, counter=self.counter, payload=self.payload, crc=self.crc)
    
    @classmethod
    def builder(cls, zigbee_id, counter, payload=b'\x00\x00'):
        buffer = bytearray(8)
        # start bytes 0xaa 0xd1 (byte 0 ~ 1)
        buffer[0:2] = b'\xaa\xd1'
        # zigbee id byte 2 ~ 3
        buffer[2:4] = zigbee_id
        # total bytes  byte 4 (total byte 1B + zigbee id 4B + payload 2 ~ 128B) & 0xFF
        buffer[4:4] = ((1+4+len(payload)+2)&0xFF).to_bytes(1, byteorder='little')
        # counter byte 5 ~ 8 
        buffer[5:9] = counter.to_bytes(4, byteorder='little')
        # payload start from byte 13
        buffer[9:9] = payload
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
    def counter(self):
        return int.from_bytes(self.msg[5:9], byteorder='little')

    @property
    def crc(self):
        return int.from_bytes(self.msg[-4:-2], byteorder='little')

    def crc_validate(self):
        return (self.crc == crc(self.msg[4:-4]))

    @property
    def payload(self):
        data = self.msg[9:-4]
        return data

    @property
    def end(self):
        return self.msg[-2]
    
    @property
    def to_bytes(self):
        return bytes(self.msg)
