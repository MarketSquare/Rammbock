
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
    return _get_data_from_ie("", message.ie)
 
def _get_data_from_ie(ies, list):
    for ie in list:
        if ie is None:
            continue
        if hasattr(ie, "ie"): 
            ies = _get_data_from_ie(ies, ie.ie)
        else:
            ies += _format_ie(ie)
    return ies

def _format_ie(ie):
    return ie.name + " " + ie.data + " "