import serial
import click
import time
import logging
from struct import Struct, pack, unpack
from boxagent.packet import BasePacket

@click.command()
@click.option('--device', help='device name')
@click.option('--times', default=10, help='repeat times')
@click.option('--command', default=1002, help='command code')
def main(device, times, command):
    logging.getLogger().setLevel(logging.INFO)
    logging.info('start main')
    ser = serial.Serial(device)
    # test 1002 command
    exec_command(ser, command, times)


def exec_command(ser, command_code, times):
    if command_code == 1002:
        for i in range(times):
            time.sleep(0.2)
            payload = Struct("<HHH24s").pack(1002, 0, 0, b'M-BOX 2010M-BOX 2210 Ver')
            packet = BasePacket.builder(0x12345678, i, payload = payload)
            logging.info("sending packet:  {!r}".format(packet))
            ser.write(packet.frame)
    elif command_code == 3300:
        for i in range(times):
            for j in range(1,7):
                time.sleep(0.2)
                payload = Struct("<H5B").pack(3300+j, 0x12, 0x34, 0x56, 0x78, 0x90)
                packet = BasePacket.builder(0x12345678, i, payload = payload)
                logging.info("sending packet:  {!r}".format(packet))
                ser.write(packet.frame)
    elif command_code == 3100:
        for i in range(times):
            for j in range(0,6):
                time.sleep(0.2)
                payload = Struct("<HB").pack(3100+j, 1)
                packet = BasePacket.builder(0x12345678, i, payload = payload)
                logging.info("sending packet:  {!r}".format(packet))
                ser.write(packet.frame)
    elif command_code == 3106:
        for i in range(times):
            time.sleep(0.2)
            payload = Struct("<HBBBBB").pack(3106, 1, 2, 3, 4, 5)
            packet = BasePacket.builder(0x12345678, i, payload = payload)
            logging.info("sending packet:  {!r}".format(packet))
            ser.write(packet.frame)
    elif command_code == 3201:
        for i in range(times):
            time.sleep(0.2)
            payload = Struct("<HH").pack(3201, 10000)
            packet = BasePacket.builder(0x12345678, i, payload = payload)
            logging.info("sending packet:  {!r}".format(packet))
            ser.write(packet.frame)
    elif command_code == 3800:
        payload = Struct("<HHB").pack(1000, 3800, 1)
        packet = BasePacket.builder(0x12345678, 1, payload = payload)
        logging.info("sending packet: {!r}".format(packet))
        ser.write(packet.frame)
    else:
        pass

if __name__ == "__main__":
    main()
