from .pin import *
from .driver import MFRC522
import asyncio
import logging
from datetime import datetime

async def RC522Runner (loop, storage_queue):
    logger = logging.getLogger(__name__)
    reader = MFRC522.MFRC522()
    led_off(RC522_DETECT_LED)
    await asyncio.sleep(5)
    # a workaround, I don't know why the first time run, rc522 can not work, it needs reset again
    del reader
    reader = MFRC522.MFRC522()
    while True:
        (status, tag_type) = reader.MFRC522_Request(reader.PICC_REQIDL)
        (status, uid) = reader.MFRC522_Anticoll()
        if status == reader.MI_OK:
            uid_number = (uid[3] << 24) + (uid[2] << 16) + (uid[1] << 8) + uid[0]
            q = dict()
            q['EventCode'] = 3600
            q['RecordDate'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            q['rfid1'] = uid_number
            led_on(RC522_DETECT_LED)
            await storage_queue.put(q)
            await asyncio.sleep(0.5)
            led_off(RC522_DETECT_LED)
        await asyncio.sleep(2)
