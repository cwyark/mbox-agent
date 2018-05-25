import logging
import asyncio 
import netifaces as ni
from packet  import ResponsePacket
from box import zigbee_device_list_cache
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

async def internet_connection_checker(transport, nic_name):
    logger = logging.getLogger('handshakes.internet_connection_checker')
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
    logger.info("NIC {} first check complete, connection status: {}".format(nic_name, _prev_conn))
    while True:
        _current_conn = check_nic_ip(nic_name)
        global zigbee_device_list_cache
        if _current_conn != _prev_conn:
            now = datetime.now()
            for zigbee_device, counter in zigbee_device_list_cache.items():
                payload = Struct("<HBBBBBBBB").pack(1000, \
                        _int_to_bcd(now.year - 2000), \
                        _int_to_bcd(now.month), \
                        _int_to_bcd(now.day), \
                        _int_to_bcd(now.weekday() + 1), \
                        _int_to_bcd(now.hour), \
                        _int_to_bcd(now.minute), \
                        _int_to_bcd(now.second), \
                        1)
                packet = ResponsePacket.builder(zigbee_id = zigbee_device, counter = counter, payload = payload)
                logger.info("EVENT <== {!s}".format(packet))
                logger.info("EVENT <== {!r}".format(packet))
                transport.write(packet.frame)
                zigbee_device_list_cache[zigbee_device] += 1
            logger.info("Found NIC {} connection changed !".format(nic_name))
        # Do not poll the network so fast! poll it every 100 ms
        await asyncio.sleep(2)
        logger.debug("device list = {}".format(zigbee_device_list_cache))
        _prev_conn = _current_conn
