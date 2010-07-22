import socket
from Interface import Interface

def use_interface(int_alias, ifname, ip_address = None, netmask = None, virtual_interface = False):
    if virtual_interface != False:
        interface.create_interface(int_alias, ifname, virtual_interface, ip_address, netmask)
    else:
        raise Exeption, "No code here yet"
   
