
RECEIVED_MESSAGES = []


def handle_sample(rammbock, msg):
    RECEIVED_MESSAGES.append(msg)


def reset_received_messages():
    while RECEIVED_MESSAGES:
        RECEIVED_MESSAGES.pop()


def respond_to_sample(rammbock, msg):
    RECEIVED_MESSAGES.append(msg)
    rammbock.save_template("__backup_template")
    try:
        rammbock.load_template("sample response")
        rammbock.client_sends_message()
    finally:
        rammbock.load_template("__backup_template")


def get_rcvd_msg():
    return RECEIVED_MESSAGES
