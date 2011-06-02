
def encode_to_bin(message):
    whole_message = ""
    for header in message.header:
        whole_message += header.name + " "
        whole_message += header.data + " "
    whole_message += " "
    for ie in message.ie:
        print ie.name
        whole_message += ie.name + " "
        whole_message += ie.data + " "
        print whole_message
    return whole_message