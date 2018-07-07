import os
import pytest
import asyncio
import pty
import serial
import uvloop
from boxagent.core import IngressTunnel

def test_response_packet(loop):
    queues = (asyncio.Queue(), asyncio.Queue())
