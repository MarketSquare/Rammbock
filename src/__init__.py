import socket
from Interface import Interface

def use_interface(int_alias, ifname, ip_address = None, netmask = None, virtual_interface = False):
    if virtual_interface != False:
        Interface().create_interface(int_alias, ifname, ip_address, netmask)
    else:
        raise Exception, "No code here yet"
   
