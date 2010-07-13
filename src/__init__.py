import socket

def use_interface(int_alias, ifname, virtual_interface = None, ip_address = None, netmask = None):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print s
    print 'Hello World!'