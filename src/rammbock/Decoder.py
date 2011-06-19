from itertools import izip_longest

def string2object(message, data):
    splitteddata = data.split()
    _get_object_from_data(message, splitteddata)

 #   splitted = data.split()
 #   _get_headers_from_list(message, splitted[:len(message.header)], message.header)
 #   _get_ies_from_list(message,splitted[len(message.header):])


def _get_object_from_data(message, data):
    header_value = []
    for item in message.items:
        if item == 'Header':
            header_value +=  [data.pop()]
        if item ==  'IE':
            tmp_ie =[]
            tmp_ie = [data.pop()]
            print tmp_ie
            message.ie += tmp_ie
            foo = data.pop()

    message.header = zip(message.header, header_value)
    print message.header
    print message.ie
