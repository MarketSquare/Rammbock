def object2string(message):
    whole_message =  _generate_message_from_object(message)
    return whole_message




def _generate_message_from_object(message):
    whole_message = ""
    message.header.reverse()
    message.ie.reverse()
    for i,j in izip_l(message.items, message.items[1:]):
    #TODO: this is looking bad. try to do something about it
        if i == 'Header':
            whole_message += _return_header_from_obj(message)
            if j != 'Header':
                whole_message += '\r\n'
        elif i == 'IE':
            whole_message += _return_ie_from_obj(message)
        else:
            raise Exception(NameError, 'Unwknown type %s' %i)

    return whole_message + '\r\n'

def izip_l(x,y):
    pad = lambda l1,l2: l1 + [None for _ in range(max(len(l2) -
                                                      len(l1), 0))]
    return zip(pad(x,y), pad(y,x))

def _return_header_from_obj(message):
    _, header = message.header.pop()
    return header + " "

def _return_ie_from_obj(message):
    ie = message.ie.pop()
    return ": ".join(ie) + "\r\n"
