def encode_to_bin(message):
    whole_message = ""
    whole_message += _get_headers_from_msg_object(message)
    whole_message += _get_ie_from_msg_object(message)
    print whole_message
    return whole_message

def _get_headers_from_msg_object(message):
    return " ".join(x for _ , x in message.header)

def _get_ie_from_msg_object(message):
    return " ".join(x for _ , x in message.ie)