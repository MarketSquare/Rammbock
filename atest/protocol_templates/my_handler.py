
RECEIVED_MESSAGES = []


def handle_sample(rammbock, msg):
    RECEIVED_MESSAGES.append(msg)


def respond_to_sample(rammbock, msg):
    pass


def get_rcvd_msg():
    return RECEIVED_MESSAGES
