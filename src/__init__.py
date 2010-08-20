import socket
from Interface import Interface


interfaces = {}

def use_interface(if_alias, ifname, ip_address = None, netmask = None, virtual_interface = False):
    global interfaces
    print "use_interface " + if_alias
    if virtual_interface != False:
        interfaces[if_alias] = Interface()
        interfaces[if_alias].create_interface(if_alias, ifname, ip_address, netmask)
        print interfaces
    else:
        raise NotImplementedError("This is not ready yet!")

def is_interface_up(ifname):
    global interfaces
    print interfaces
    print "is_interface_up " + ifname
    print interfaces[ifname]
    return interfaces[ifname].check_interface()

def delete_interface(ifname):
    global interfaces
    print "delete_interface " + ifname
    return interfaces[ifname].del_interface()
