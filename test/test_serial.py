import os
import pytest
import asyncio
import uvloop
import pty
import serial
from boxagent.serial_transport import SerialTransport, create_serial_connection
from boxagent.core import IngressTunnel

class TestProtocol(asyncio.Protocol):

    def connection_made(self, transport):
        self._transport = transport
        self.buffer = bytearray()

    def data_received(self, data):
        self.buffer += data
        if b'\n' in data:
            self._transport.write(self.buffer)

    def connection_lost(self):
        self._transport.loop.close()

@pytest.fixture
def simple_buffer():
    return b'hello\n'

def test_serial_pingpong_transport(loop, simple_buffer):
    master, slave = pty.openpty()
    ser = serial.Serial(os.ttyname(slave), rtscts=True,dsrdtr=True)
    os.write(master, simple_buffer)

    async def create_serial_connection(loop, protocol_factory, serial_port):
        protocol = protocol_factory()
        transport = SerialTransport(loop, protocol, serial_port)
        return (transport, protocol)

    async def send_message(msg):
        os.write(master, msg)

    coro = create_serial_connection(loop, TestProtocol, ser)
    loop.run_until_complete(coro)
    loop.run_until_complete(send_message(simple_buffer))
    # Should be run_forever() here, but it seems loop.stop() can not stop the loop
    #loop.run_forever()
    ret = os.read(master, len(simple_buffer))
    assert ret == simple_buffer
