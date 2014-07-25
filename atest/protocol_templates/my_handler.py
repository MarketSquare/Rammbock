
RECEIVED_MESSAGES = []


def handle_sample(rammbock, msg):
    RECEIVED_MESSAGES.append(msg)


def respond_to_sample(rammbock, msg):
    rammbock.save_template("__backup_template")
    try:
        rammbock.load_template("sample response")
        rammbock.client_sends_message()
    finally:
        rammbock.load_template("__backup_template")


def get_rcvd_msg():
    return RECEIVED_MESSAGES
