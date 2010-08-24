import socket
from Interface import Interface

class Rammbock:

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        print "Init **************************"
        self.interfaces = {}

    def use_interface(self, if_alias, ifname, ip_address = None, netmask = None, virtual_interface = False):
        print "use_interface " + if_alias
        if virtual_interface != False:
            if self.interfaces.has_key(if_alias) == False:
                self.interfaces[if_alias] = Interface()
                self.interfaces[if_alias].create_interface(if_alias, ifname, ip_address,netmask)
            print self.interfaces
        else:
            raise NotImplementedError("This is not ready yet!")

    def is_interface_up(self, ifname):
        self.interfaces
        print self.interfaces
        print "is_interface_up " + ifname
        print self.interfaces
        return self.interfaces[ifname].check_interface()

    def delete_interface(self, ifname):
        self.interfaces
        print "delete_interface " + ifname
        return self.interfaces[ifname].del_interface()
