def string2object(message, data):
    splitteddata = data.split()
    print repr(splitteddata)
    _get_object_from_data(message, splitteddata)

def _get_object_from_data(message, data):
    i = 0
    for a, item in enumerate(message.items):
        if item['type'] == 'HEADER':
            message.items[a] = {'type': 'HEADER', 'name': item['name'], 'value': data[i]}
        elif item['type'] == 'IE':
            message.items[a] = _get_value_to_item(item, data[i][:-1], data[i+1])
            i += 1
        i += 1

def _get_value_to_item(item, name, value):
    if name != item['name']:
        raise Exception("Wrong information element: '" + name + "' Expected: '"+item['name']+"'")
    else:
        return {'type': 'IE', 'name': item['name'], 'value': value}
