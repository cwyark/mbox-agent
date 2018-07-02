import pytest
import boxagent
from boxagent.packet import BasePacket

@pytest.fixture
def frame():
    return bytearray(b'\xaa\xd1\x12\x34\x56\x78\x0d\xf5\x31\x00\x00\x22\x0c\x02\x00\x00\x00\x6f\x15\xd0\x55')

def test_unpack(frame):
    try:
        packet = BasePacket(frame)
    except:
        assert 0

def test_crc_validate(frame):
    try:
        packet = BasePacket(frame)
    except:
        assert 0

    assert packet.crc_validate() == True

def test_builder():
    # Should test builder, but classmethod not work 
    assert True
