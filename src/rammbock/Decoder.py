def string2object(message, data):
    splitted = data.split()
    _get_headers_from_list(message, splitted[:3])
    _get_ies_from_list(message,splitted[3:])

def _get_headers_from_list(message, all_headers):
    message.header.append(['Request Method', all_headers[0]])
    message.header.append(['Request URI', all_headers[1]])
    message.header.append(['Request Version', all_headers[2]])

def _get_ies_from_list(message, splitted):
    for i in range(len(splitted)):
        #TODO do something about this. it's ugly!
        try:
            message.ie.append([splitted[i][:-1], splitted[i+1]])
        except IndexError:
            return
        i + 1
        