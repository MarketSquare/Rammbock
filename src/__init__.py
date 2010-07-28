import socket
from Interface import Interface

def use_interface(int_alias, ifname, ip_address = None, netmask = None, virtual_interface = False):
    if virtual_interface != False:
        Interface().create_interface(int_alias, ifname, ip_address, netmask)
    else:
        raise NotImplementedError("This is not ready yet!")

def is_interface_up(ifname):
    interface_state =  Interface().check_interface(ifname)
    return interface_state

def delete_interface(ifname):
    Interface().del_interface(ifname)
       
