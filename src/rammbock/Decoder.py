def string2object(message, data):
    splitted = data.split()
    _get_headers_from_string(message, splitted[:3])
    #_get_ies_from_string(message,splitted[3:])



def _get_headers_from_string(message, all_headers):
    message.header.append(['Request Method', all_headers[0]])
    message.header.append(['Request URI', all_headers[1]])
    message.header.append(['Request Version', all_headers[2]])

def _get_ies_from_string(message, splitted):
    for i in range(len(splitted)):
        print [":".strip(splitted[i]), splitted[i+1]]
        message.ie.append[":".strip(splitted[i]), splitted[i+1]]
        i + 1
