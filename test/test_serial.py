import pytest
import asyncio
import uvloop
from boxagent.core import IngressTunnel

@pytest.yield_fixture()
def loop():
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.mark.asyncio
async def test_hello(loop):
    await asyncio.sleep(0.5)
    assert True
