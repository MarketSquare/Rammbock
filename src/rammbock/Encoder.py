import struct

def object2string(message):
    whole_message =  _generate_message_from_object(message)
    return whole_message

def _generate_message_from_object(message):
    whole_message = ""
    for index, item in enumerate(message.items):
        if item['type'] is 'BINARY':
            whole_message += dec2bin(item['value'], item['length'])
        elif item['type'] is 'STRING':
            whole_message += item['value']
    return whole_message

def dec2bin(data, length):
    data = _add_padding_to_string(data, int(length))
    a = ""
    for b in data:
        a += struct.pack('B', ord(b))
    return a

def _add_padding_to_string(data, length):
    return chr(int(data)).rjust(length,'\0')
