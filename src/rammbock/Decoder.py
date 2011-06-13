def string2object(message, data):
    splitted = data.split()
    _get_headers_from_list(message, splitted[:3])
    _get_ies_from_list(message,splitted[3:])

def _get_headers_from_list(message, all_headers):
    message.header.append(['Request Method', all_headers[0]])
    message.header.append(['Request URI', all_headers[1]])
    message.header.append(['Request Version', all_headers[2]])

def _get_ies_from_list(message, splitted):
    message.ie += [[splitted[i][:-1], splitted[i+1]] for i in range(0,len(splitted),2)]
