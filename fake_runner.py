import serial
import click
import time
import logging
from boxagent.packet import BasePacket

@click.command()
@click.option('--device', help='device name')
def main(device):
    logging.getLogger().setLevel(logging.INFO)
    logging.info('start main')
    ser = serial.Serial(device)
    for i in range(100):
        time.sleep(0.5)
        packet = BasePacket.builder(0x12345678, i)
        logging.info("sending packet:  {!r}".format(packet))
        ser.write(packet.frame)

if __name__ == "__main__":
    main()
