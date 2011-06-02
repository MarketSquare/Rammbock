
def encode_to_bin(message):
    whole_message = ""
    whole_message += _get_headers_from_msg_object(message)
    whole_message += _get_ie_from_msg_object(message)
    return whole_message

def _get_headers_from_msg_object(message):
    headers = ""
    for header in message.header:
        headers += header.name + " "
        headers += header.data + " "
        return headers
        
def _get_ie_from_msg_object(message):
    ies = ""
    for ie in message.ie:
        print ie.name
        ies += ie.name + " "
        ies += ie.data + " "
        return ies