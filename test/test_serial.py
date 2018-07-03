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
        self.transport = transport

    def data_received(self, data):
        self.transport.write(data)

@pytest.yield_fixture()
def loop():
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.mark.asyncio
async def test_serial_transport(loop):
    master, slave = pty.openpty()
    ser = serial.Serial(os.ttyname(slave))
    os.write(master, b'1234')
