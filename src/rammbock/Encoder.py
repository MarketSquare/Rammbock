from itertools import izip_longest

def object2string(message):
    whole_message =  _generate_message_from_object(message)
    print whole_message
    return whole_message

def _generate_message_from_object(message):
    whole_message = ""
    message.header.reverse()
    message.ie.reverse()
    for i,j in izip_longest(message.items, message.items[1:]):
        if i == 'Header':
            tmp = message.header.pop()
            _, x = tmp
            whole_message += x + " "
            if j != 'Header':
                whole_message += '\r\n'
        elif i == 'IE':
            tmp = message.ie.pop()
            print tmp
            tmp = ": ".join(tmp)
            print "tmp =" +tmp
            whole_message += tmp + "\r\n"
        else:
            raise Exception(NameError, 'Unwknown type %s' %i)
        if j == None:
            whole_message += '\r\n'
            return whole_message


def _get_headers_from_msg_object(message):
    return " ".join(x for _ , x in message.header)

def _get_ie_from_msg_object(message):
    return "".join(i + ": " + x + "\r\n" for i , x in message.ie)