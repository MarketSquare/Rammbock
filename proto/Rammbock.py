# API prototype
"""Start defining a new protocol template.

All messages sent and received from a connection after calling 'Use protocol' have to use the same protocol template. Protocol template fields can be used to search messages from buffer.
"""
def new_protocol(protocol):
    raise Exception('Not yet done')

"""End protocol definition."""
def end_protocol():
    raise Exception('Not yet done')
    
def start_udp_server(host, ip, _server=None):
    raise Exception('Not yet done')
    
def start_udp_client(ip=None, port=None, _client=None):
    raise Exception('Not yet done')
    
"""Connect a client to certain host and port."""
def connect(host, port, _client=None):
    raise Exception('Not yet done')
    
"""Take a certain protocol into use in server or client.

From this moment on (until another protocol is taken into use) all messages received and sent have to confirm to this protocol template."""
def use_protocol(protocol, _server=None, _client=None):
    raise Exception('Not yet done')
    
"""Send raw binary data."""
def send_binary(message, _server=None, _client=None, *params):
    raise Exception('Not yet done')
    
"""Receive raw binary data."""
def receive_binary(_server=None, _client=None, *params):
    raise Exception('Not yet done')
    
"""Define a new message pdu template.

Parameters have to be header fields."""
def new_pdu(*params):
    raise Exception('Not yet done')
    
"""Send a pdu.

Parameters have to be pdu fields."""
def send_pdu(*params):
    raise Exception('Not yet done')
    
"""Receive a message object.

Parameters that have been given are validated against message fields."""
def receive_pdu(*params):
    raise Exception('Not yet done')
    
def u8(name, default_value=None):
    raise Exception('Not yet done')
    
def u16(name, default_value=None):
    raise Exception('Not yet done')
    
def u32(name, default_value=None):
    raise Exception('Not yet done')
    
"""Defines the pdu in protocol template.

Length must be the name of a previous field in template definition."""
def pdu(length):
    raise Exception('Not yet done')
    
def hex_to_bin(hex):
    raise Exception('Not yet done')
    