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
            if data[i].split(':')[0] != item['name']:
                raise Exception("Wrong information element: '"+data[i].split(':')[0]+"' Expected: '"+item['name']+"'")
            else:
                message.items[a] = {'type': 'IE', 'name': item['name'], 'value': data[i+1]}
            i += 1
        i += 1

def _check_ies_vs_ies_in_schema(ies, tmp_ie_names):
    for i in range(len(ies)):
        tmp_ie = tmp_ie_names[i][:-1]
        if ies[i] != tmp_ie:
            raise Exception("Wrong information element: '"+tmp_ie+"' Expected: '"+ies[i]+"'")
