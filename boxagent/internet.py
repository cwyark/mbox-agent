import logging
import asyncio 
import netifaces as ni
import RPi.GPIO as GPIO
from .packet  import BasePacket
from datetime import datetime
from struct import Struct, pack, unpack
from .pin import *

GPIO.setmode(GPIO.BCM)

async def ping(loop, target, dump=False):
    create =  asyncio.create_subprocess_exec('ping', '-c', '5', target,
                                          stdout=asyncio.subprocess.PIPE)
    proc = await create
    lines = []
    while True:
        line = await proc.stdout.readline()
        if line == b'':
            break
        l = line.decode('utf8').rstrip()
        if dump:
            print(l)
        lines.append(l)
    transmited, received = [int(a.split(' ')[0]) for a
                            in lines[-2].split(', ')[:2]]
    stats, unit = lines[-1].split(' = ')[-1].split(' ')
    min_, avg, max_, stddev = [float(a) for a in stats.split('/')]
    return transmited, received, unit, min_, avg, max_, stddev

async def ping_connection_checker(loop, storage_queue, interval):
    logger = logging.getLogger(__name__)
    TARGET_SERVER = "www.bing.com"
    _interval = interval
    while True:
        logger.info("Start ping {}".format(TARGET_SERVER))
        try:
            ping_result = await ping(loop, TARGET_SERVER)
            led_on(INTERNET_LED)
            logger.info("ping result {}".format(ping_result))
            _interval = interval
        except:
            logger.info("ping failed")
            led_off(INTERNET_LED)
            _interval = 60
        await asyncio.sleep(_interval)

async def device_connection_checker(storage_queue, nic_name):
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
            await storage_queue.put(q)
        await asyncio.sleep(2)
        _prev_conn = _current_conn
