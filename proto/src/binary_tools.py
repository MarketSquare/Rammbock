import binascii
import struct

try:
    if bin(0):
        pass
except NameError, name_error:
    def bin(value):
        """
        Support for Python 2.5
        Based on a recipe by Benjamin Wiley Sittler.
        http://code.activestate.com/recipes/219300-format-integer-as-binary-string/
        """
        if value < 0:
            return '-' + bin(-value)
        out = []
        if value == 0:
            out.append('0')
        while value > 0:
            out.append('01'[value & 1])
            value >>= 1
        try:
            return '0b' + ''.join(reversed(out))
        except NameError:
            out.reverse()
        return '0b' + ''.join(out)

LONGLONG = struct.Struct('>Q')

def to_bin(string_value):
    string_value = str(string_value)
    if string_value.startswith('0x'):
        return _hex_to_bin(string_value)
    elif string_value.startswith('0b'):
        return _int_to_bin(int(string_value.replace('0b','').replace(' ',''), 2))
    return _int_to_bin(int(string_value))

def _int_to_bin(integer):
    if integer >= 18446744073709551616L:
        return to_bin(hex(integer))
    result = LONGLONG.pack(integer).lstrip('\x00')
    return result or '\x00'

def _hex_to_bin(string_value):
    value = string_value.replace('0x','').replace(' ','').replace('L','')
    if len(value) %2 == 1:
        value = '0' + value
    return binascii.unhexlify(value)

def to_bin_of_length(length, string_value):
    bin = to_bin(string_value)
    if len(bin) > length:
        raise AssertionError('Too long binary value %s (max length %d)'
            % (string_value, length))
    return bin.rjust(length, '\x00')

def to_hex(binary):
    return binascii.hexlify(binary)

def to_0xhex(binary):
    return '0x' + to_hex(binary)

def log_hex(message, level='INFO'):
    print '*%s* %s' % (level, to_hex(message)) 

def to_binary_of_length(length, bytes):
    result = bin(int(to_0xhex(bytes), 16))
    if len(result) < length+2:
        result = '0b' + '0' * (length - len(result) + 2) + result[2:]
    return result