import struct
from Rammbock.binary_tools import to_0xhex


def convert_to_ip(value):
    try:
        return to_0xhex(struct.pack('BBBB', *(int(number) for number in value.split("."))))
    except:
        raise Exception("Malformed IP: %s" % value)


def convert_to_label_sequence(value):
    return "".join(chr(len(a)) + a for a in value.split('.'))


def field_should_not_exist(message_struct, field_name):
    if field_name in message_struct:
        raise AssertionError('Field %s was found in %s' % (field_name, message_struct))


def field_should_exist(message_struct, field_name):
    if field_name not in message_struct:
        raise AssertionError('Field %s was not found in %s' % (field_name, message_struct))


def convert_datetime_to_ntp_integer(value):
    raise Exception("Not yet implemented")
