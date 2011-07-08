import struct

def string2object(message, data):
    splitteddata = data.split()
    print repr(splitteddata)
    _get_object_from_data(message, splitteddata)

def _get_object_from_data(message, data):
    i = 0
    for a, item in enumerate(message.items):
        if item['type'] == 'HEADER':
            message.items[a] = {'type': 'HEADER', 'name': item['name'], 'value': data[i]}
            i += 1
        elif item['type'] == 'IE':
            message.items[a] = _get_value_to_item(item, data[i][:-1], data[i+1])
            i += 2
        elif item['type'] == 'BINARY':
            message_temp = ""
            temp = list(data[i])
            temp.reverse()
            for d in range(0, int(item['length'])):
                message_temp += str(struct.unpack('B', temp.pop())[0])
            print temp
            print "debug: " + message_temp, repr(message_temp)
            temp.reverse()
            data[i] = temp
            print temp
            message.items[a]['value'] = str(int(message_temp))

def _get_value_to_item(item, name, value):
    if name != item['name']:
        raise Exception("Wrong information element: '" + name + "' Expected: '"+item['name']+"'")
    else:
        return {'type': 'IE', 'name': item['name'], 'value': value}



