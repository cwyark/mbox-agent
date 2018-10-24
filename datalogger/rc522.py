from .pin import *
from .driver import MFRC522
import asyncio
import logging
from datetime import datetime

async def RC522Runner (loop, storage_queue):
    logger = logging.getLogger(__name__)
    reader = MFRC522.MFRC522())
    while True:
        (status, tag_type) = reader.MRFC522_REquest(reader.PICC_REQIDL)
        (status, uid) = reader.MRFC522_Anticoll()
        if status == reader.MI_OK:
            uid_number = (uid[3] << 24) + (uid[2] << 16) + (uid[1] << 8) + uid[0]
            q = dict()
            q['EventCode'] = 360
            q['RecordDate'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
            q['rfid1'] = uid_number
            await storage_queue.put(q)
        await asyncio.sleep(0.5)
