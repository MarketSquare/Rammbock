
RECEIVED_MESSAGES = []

def handle_sample(rammbock, msg):
    RECEIVED_MESSAGES.append(msg)

def get_rcvd_msg():
    return RECEIVED_MESSAGES

