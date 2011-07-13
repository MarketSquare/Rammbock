import struct

def dec2bin(data, length):
    data = _add_padding_to_string(data, int(length))
    a = ""
    for b in data:
        a += struct.pack('B', ord(b))
    return a

def _add_padding_to_string(data, length):
    return chr(int(data)).rjust(length,'\0')
