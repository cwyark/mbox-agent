import pytest
import boxagent
from boxagent.packet import BasePacket

@pytest.fixture
def frame():
    return bytearray(b'\xaa\xd1\x12\x34\x56\x78\x0d\xf5\x31\x00\x00\x22\x0c\x02\x00\x00\x00\x6f\x15\xd0\x55')

@pytest.fixture
def wrong_frame():
    return bytearray(b'\xaa\xd1\x12\x34\x56\x78\x0d\xf5\x31\x00\x00\x22\x0c\x02\x00\x00\x00\x6f\x05\xd0\x55')

def test_crc_validate(frame, wrong_frame):
    correct_packet = BasePacket(frame)
    wrong_packet = BasePacket(wrong_frame)
    assert correct_packet.crc_validate() == True
    assert wrong_packet.crc_validate() == False

def test_builder():
    device_id = 0x11335577
    counter = 1000
    payload = b'\x01\x02\x03\x04\x05'
    packet = BasePacket.builder(device_id = device_id, counter = 1000, payload = payload)
    assert packet.device_id == device_id
    assert packet.counter == counter
    assert packet.payload == payload

def test_response_packet(frame):
    packet = BasePacket(frame)
    response_packet = packet.response_packet()
    assert response_packet.command_code == 1000


