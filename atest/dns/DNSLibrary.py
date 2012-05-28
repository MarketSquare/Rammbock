import struct
from Rammbock.binary_tools import to_0xhex


def convert_to_ip(value):
    try:
        return to_0xhex(struct.pack('BBBB', *(int(number) for number in value.split("."))))
    except:
        raise Exception("Malformed IP: %s" % value)

def convert_to_label_sequence(value):
    return "".join(chr(len(a)) + a for a in value.split('.'))
