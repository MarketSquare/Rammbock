import struct


def convert_to_ip(value):
    return struct.pack('cccc', (number for number in value.split(".")))