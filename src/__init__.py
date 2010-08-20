import socket
from Interface import Interface

interfaces = {}

def use_interface(if_alias, ifname, ip_address = None, netmask = None, virtual_interface = False):
    print "lsdjflsfj"    
    if virtual_interface != False:
        interfaces[if_alias] = Interface().create_interface(if_alias, ifname, ip_address, netmask)
        print interfaces[if_alias]
    else:
        raise NotImplementedError("This is not ready yet!")

def is_interface_up(ifname):
    print "is_interface_up " + ifname
    print interfaces[ifname].check_interface
    return interfaces[ifname].check_interface

def delete_interface(ifname):
    return interfaces[ifname].del_interface
