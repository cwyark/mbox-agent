import pytest
import asyncio
import uvloop

@pytest.yield_fixture()
def loop():
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
