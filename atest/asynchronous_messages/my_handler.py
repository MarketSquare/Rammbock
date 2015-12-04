from Rammbock import logger


RECEIVED_MESSAGES = []
SERVER_SENT = {'sample': 0,
               'another': 0}


def handle_sample(rammbock, msg):
    RECEIVED_MESSAGES.append(msg)


def reset_received_messages():
    while RECEIVED_MESSAGES:
        RECEIVED_MESSAGES.pop()


def respond_to_sample(rammbock, msg, client):
    foo = "adding Extra Variable to replicate ArgCount bug"
    bar = "adding Extra Variable to replicate ArgCount bug"
    RECEIVED_MESSAGES.append(msg)
    #rammbock.save_template("__backup_template")
    try:
        #rammbock.load_template("sample response")
        template = rammbock.get_template('sample response')[0]
        rammbock.client_sends_given_message(template,'name=%s' % client.name)
    finally:
        pass
        #rammbock.load_template("__backup_template")


def server_respond_to_another_max_100(rammbock, msg, server, connection):
    RECEIVED_MESSAGES.append(msg)
    if SERVER_SENT['another'] < 100:
        SERVER_SENT['another'] = SERVER_SENT['another'] + 1
        #rammbock.save_template("__backup_template")
        try:
            #rammbock.load_template("another")
            template = rammbock.get_template('another')[0]
            rammbock.server_sends_given_message(template, 'name=%s' % server.name, 'connection=%s' % connection.name)
        finally:
            pass
            # rammbock.load_template("__backup_template")
    else:
        pass
        #logger.("Reached 100 in another")


def server_respond_to_sample_response_max_100(rammbock, msg):
    RECEIVED_MESSAGES.append(msg)
    if SERVER_SENT['sample'] < 100:
        SERVER_SENT['sample'] = SERVER_SENT['sample'] + 1
        rammbock.save_template("__backup_template")
        try:
            rammbock.load_template("sample")
            rammbock.server_sends_message()
        finally:
            rammbock.load_template("__backup_template")
    else:
        pass
        #logger.warn("Reached 100 in sample")


def get_rcvd_msg():
    return RECEIVED_MESSAGES
