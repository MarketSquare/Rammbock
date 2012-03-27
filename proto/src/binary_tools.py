import binascii
import struct

LONGLONG = struct.Struct('>Q')

def to_bin(string_value):
    string_value = str(string_value)
    if string_value.startswith('0x'):
        value = string_value.replace('0x','').replace(' ','')
        if len(value)%2==1:
            value='0'+value
        return binascii.unhexlify(value)
    result = LONGLONG.pack(int(string_value)).lstrip('\x00')
    return result or '\x00'

def to_bin_of_length(length, string_value):
    bin = to_bin(string_value)
    if len(bin) > length:
        raise AssertionError('Too long binary value %s (max length %d)' % (string_value, length))
    return bin.rjust(length, '\x00')

def to_hex(binary):
    return binascii.hexlify(binary)

def to_0xhex(binary):
    return '0x'+to_hex(binary)

def log_hex(message, level='INFO'):
    print '*%s* %s' % (level, to_hex(message)) 
