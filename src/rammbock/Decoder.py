def string2object(message, data):
    splitteddata = data.split()
    _get_object_from_data(message, splitteddata)

def _get_object_from_data(message, data):
    header_value = []
    tmp_ie_values = []
    #TODO: try to get rid of this reverse
    data.reverse()
    for item in message.items:
        if item == 'Header':
            header_value +=  [data.pop()]
        if item ==  'IE':
            #TODO: create check that tmp_ie_name and expected ie does match
            tmp_ie_name = [data.pop()]
            tmp_ie = [data.pop()]
            tmp_ie_values += tmp_ie
    message.ie = zip(message.ie, tmp_ie_values)
    message.header = zip(message.header, header_value)
