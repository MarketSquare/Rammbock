from Rammbock import logger
import sys


RECEIVED_MESSAGES = []
SERVER_SENT = {'sample': 0, 'another': 0}


def handle_sample(rammbock, msg):
    RECEIVED_MESSAGES.append(msg)


def reset_received_messages():
    while RECEIVED_MESSAGES:
        RECEIVED_MESSAGES.pop()


def respond_to_sample(rammbock, msg, client):
    RECEIVED_MESSAGES.append(msg)
    sys.__stdout__.write("Sending 11111 DWR '%s'" % client.name)
    foo = "adding Extra Variable to replicate ArgCount bug"
    bar = "adding Extra Variable to replicate ArgCount bug"
    template, fields, headers = rammbock.get_template('sample response')
    rammbock.client_sends_given_message(template, fields, headers, 'name=%s' % client.name)


def respond_to_sample2(rammbock, msg, client):
    RECEIVED_MESSAGES.append(msg)
    sys.__stdout__.write("Sending DWR '%s'" % client.name)
    foo = "adding Extra Variable to replicate ArgCount bug"
    bar = "adding Extra Variable to replicate ArgCount bug"
    template, fields, headers = rammbock.get_template('sample response')
    rammbock.client_sends_given_message(template, fields, headers, 'name=%s' % client.name)

def server_respond_to_another_max_100(rammbock, msg, server, connection):
    RECEIVED_MESSAGES.append(msg)
    if SERVER_SENT['another'] < 100:
        SERVER_SENT['another'] = SERVER_SENT['another'] + 1
        template, fields, headers = rammbock.get_template('another')
        rammbock.server_sends_given_message(template, fields, headers, 'name=%s' % server.name, 'connection=%s' % connection.name)
    else:
        logger.warn("Reached 100 in another")


def server_respond_to_sample_response_max_100(rammbock, msg):
    RECEIVED_MESSAGES.append(msg)
    if SERVER_SENT['sample'] < 100:
        SERVER_SENT['sample'] = SERVER_SENT['sample'] + 1
        template, fields, headers = rammbock.get_template('sample')
        rammbock.server_sends_given_message(template, fields, headers)
    else:
        logger.warn("Reached 100 in sample")


def get_rcvd_msg():
    return RECEIVED_MESSAGES
