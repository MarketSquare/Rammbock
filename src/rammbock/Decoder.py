def string2object(message, data):
    _get_headers(message, data)
    _get_information_elements(message,data)

def _get_headers(message, data):
    splitted = data.split()
    _get_headers_from_string(message, splitted)

def _get_information_elements(message, data):
    splitted = data.split()
    _get_ies_from_string(message, splitted)

def _get_headers_from_string(message, all_headers):
    message.header.append(['Request Method', all_headers[0]])
    message.header.append(['Request URI', all_headers[1]])
    message.header.append(['Request Version', all_headers[2]])

def _get_ies_from_string(message, splitted):
    for ie in splitted[2:]:
        message.ie.append(":".strip(ie))
