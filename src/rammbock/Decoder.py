from itertools import izip_longest

def string2object(message, data):
    splitteddata = data.split()
    _get_object_from_data(message, splitteddata)

 #   splitted = data.split()
 #   _get_headers_from_list(message, splitted[:len(message.header)], message.header)
 #   _get_ies_from_list(message,splitted[len(message.header):])


def _get_object_from_data(message, data):
    header_value = []
    tmp_ie_values = []
    tmp_ie_names = []
    data.reverse()
    for item in message.items:
        if item == 'Header':
            header_value +=  [data.pop()]
        if item ==  'IE':

            tmp_ie_name = [data.pop()]
            tmp_ie = [data.pop()]
            tmp_ie_values += tmp_ie
            tmp_ie_names += tmp_ie_name
    print tmp_ie_names
    print tmp_ie_values
    message.ie = zip(message.ie, tmp_ie_values)
    print message.ie
    message.header = zip(message.header, header_value)
