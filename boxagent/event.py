import logging
import asyncio 
import netifaces as ni
from .packet  import BasePacket
from datetime import datetime
from struct import Struct, pack, unpack

def _int_to_bcd(n):
    """
    Encode a one or two digits number to the BCD.

    """
    bcd = 0
    for i in (n // 10, n % 10):
    	for p in (8, 4, 2, 1):
            if i >= p:
                bcd += 1
                i -= p
            bcd <<= 1
    return bcd >> 1

async def internet_connection_checker(nic_name):
    logger = logging.getLogger(__name__)
    UP = 1
    DOWN = 0

    def check_nic_ip(nic_name):
        try:
            nic = ni.ifaddresses(nic_name)
            try:
                nic_ip = nic[ni.AF_INET][0]['addr']
                nic_mask = nic[ni.AF_INET][0]['netmask']
                nic_gateway = nic[ni.AF_INET][0]['broadcast']
                connection = UP
            except KeyError:
                connection = DOWN
        except ValueError:
            connection = DOWN
        except KeyError:
            connection  = DOWN
        return connection

    # First check the connection status
    _prev_conn = check_nic_ip(nic_name)
    logger.info("start detecting network {} change event, initial status is {}".format(nic_name, _prev_conn))
    while True:
        _current_conn = check_nic_ip(nic_name)
        if _prev_conn != _current_conn:
            logger.info("network interface {} changed, it change to {}".format(nic_name, _current_conn))
        await asyncio.sleep(2)
        _prev_conn = _current_conn
