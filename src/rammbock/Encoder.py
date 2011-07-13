import struct

def object2string(message):
    whole_message =  _generate_message_from_object(message)
    return whole_message

def _generate_message_from_object(message):
    whole_message = ""
    for index, item in enumerate(message.items):
        if item['type'] is 'HEADER':
            whole_message += item['value'] + " "
            if _next_item_is_not(message, index, 'HEADER'):
                whole_message += '\r\n'
        elif item['type'] is "IE":
            whole_message += item['name'] + ": " + item['value'] + '\r\n'
        elif item['type'] is 'DELIMITER':
            whole_message += item['value']
        elif item['type'] is 'BINARY':
            whole_message += _convert_to_string(item['value'], item['length'])
        elif item['type'] is 'STRING':
            whole_message += item['value']

    return whole_message

def _next_item_is_not(message, index, name):
    try:
        return message.items[index + 1]['type'] is not name
    except IndexError:
        return False

def _convert_to_string(data, length):
    data = _add_padding_to_string(data, int(length))
    print "'" + data + "'", "'" + repr(data) + "'"
    a = ""
    for b in data:
        a += struct.pack('B', ord(b))
    print "fdsafdsa: " + a + "len: " + str(len(a))
    return a

def _add_padding_to_string(data, length):
    return chr(int(data)).rjust(length,'\0')
