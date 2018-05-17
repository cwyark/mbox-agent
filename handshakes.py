import logging
import asyncio 
import netifaces as ni

logging.basicConfig(level=logging.DEBUG, 
        format="%(asctime)s %(name)-12s %(levelname)-8s $(message)", 
        datefmt="%m-%d %H:%M",
        handlers = [logging.FileHandler('box.log', 'w', 'utf-8'),]
        )

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

async def internet_connection_checker(nic_name):
    logger = logging.getLogger('handshakes.internet_connection_checker')
    UP = 1
    DOWN = 0

    def check_nic_ip(nic_name):
        try:
            nic = ni.ifaddresses(nic_name)
            nic_ip = nic[ni.AF_INET][0]['addr']
            nic_mask = nic[ni.AF_INET][0]['netmask']
            nic_gateway = nic[ni.AF_INET][0]['broadcast']
            connection = UP
        except ValueError as err:
            connection = DOWN
        return connection

    # First check the connection status
    _prev_conn = check_nic_ip(nic_name)
    logger.info("NIC {} first check complete, connection status: {}".format(nic_name, _prev_conn))
    while True:
        _current_conn = check_nic_ip(nic_name)
        if _current_conn != _prev_conn:
            await asyncio.sleep(10)
            logger.info("Found NIC {} connection changed !".format(nic_name))
        # Do not poll the network so fast! poll it every 10 ms
        await asyncio.sleep(1)
        _prev_conn = _current_conn
        logger.info("NIC {} status = {}".format(nic_name, _current_conn))
