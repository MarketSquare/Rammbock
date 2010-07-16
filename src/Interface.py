import socket

class Interface:
    """Interface class for socket"""
    
    s = None
    def use_interface(self, int_alias, ifname, virtual_interface = None, ip_address = None, netmask = None):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print self.s
        print 'Hello World!'

    def is_interface_up (self, int_alias, ifname, virtual_interface = None, ip_address = None, netmask = None):
        if self.s == None:
            return True
        else:
            return False
