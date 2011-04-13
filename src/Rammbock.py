from Interface import Interface
from Client import Client
from Server import Server

class Rammbock(Server, Client):

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        self.interfaces = {}

    def use_virtual_interface(self, if_alias, ifname, ip_address, netmask):
        print "use_virtual_interface " + if_alias
        if self.interfaces.has_key(if_alias) == True:
            if self.interfaces[if_alias].ifUp == True:
		        return
        else:
            self.interfaces[if_alias] = Interface()

        self.interfaces[if_alias].create_virtual_interface(if_alias, ifname, ip_address, netmask)

    def use_interface(self, if_alias, ifname, ip_address = None, netmask = None, 
                      virtual_interface = False):
        print "use_interface " + if_alias
        if virtual_interface:
            self.use_virtual_interface(if_alias, ifname, ip_address, netmask)
        else:
            self.interfaces[if_alias] = Interface()
            self.interfaces[if_alias].create_physical_interface(if_alias, ifname, ip_address, netmask)
 

    def is_interface_up(self, ifname):
        self.interfaces
        print "is_interface_up " + ifname
        return self.interfaces[ifname].check_interface()

    def delete_interface(self, ifname):
        self.interfaces
        print "delete_interface " + ifname
        return self.interfaces[ifname].del_interface()
    
    def start_server(self, if_alias, port):
        Server.server_startup(self, if_alias, port)

    def connect_to_server(self, host, port):
        Client.establish_connection_to_server(self, host, port)

    def close_server(self):
         Server.close_server(self)
         
    def close_client(self):
         Client.close_client(self)
