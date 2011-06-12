def string2object(message, data):
    return _get_headers(message, data)

def _get_headers(message, data):
    splitted = data.split()
    _get_headers_from_string(message, splitted)

def _get_headers_from_string(message, all_headers):
    message.header.append(['Request Method', all_headers[0]])
    message.header.append(['Request URI', all_headers[1]])
    message.header.append(['Request Version', all_headers[2]])
    return message
