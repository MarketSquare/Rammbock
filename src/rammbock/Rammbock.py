from Client import Client
from Server import Server
from rammbock.Interface import VirtualInterface, PhysicalInterface

class Rammbock(object):

    def __init__(self):
            self.interfaces = {}
            self._client = Client()
            self._server = Server(self.interfaces)

    def create_virtual_interface(self, if_alias, ifname, ip_address, netmask):
        print "create_virtual_interface " + if_alias
        if if_alias in self.interfaces and  self.interfaces[if_alias].ifUp:
            raise Exception('Interface "%s" already exists' % if_alias)
        self.interfaces[if_alias] = VirtualInterface(if_alias, ifname, ip_address, netmask)

    def use_interface(self, if_alias, ifname, ip_address=None, netmask=None):
        print "use_interface " + if_alias
        self.interfaces[if_alias] = PhysicalInterface(if_alias, ifname, ip_address, netmask)

    def is_interface_up(self, ifname):
        print "is_interface_up " + ifname
        return self.interfaces[ifname].check_interface()

    def delete_interface(self, ifname):
        print "delete_interface " + ifname
        return self.interfaces[ifname].del_interface()

    def start_server(self, if_alias, port):
        self._server.server_startup(if_alias, port)

    def connect_to_server(self, host, port):
        self._client.establish_connection_to_server(host, port)

    def close_server(self):
        self._server.close_server()

    def close_client(self):
        self._client.close_client()

    def client_send_packet_over_udp(self, packet): 
        self._client.send_packet_over_udp(packet)

    def server_receive_packet_over_udp(self):
        return self._server.receive_packet_over_udp()

    def server_send_packet_over_udp(self, packet): 
        self._server.send_packet_over_udp(packet)

    def client_receive_packet_over_udp(self):
        return self._client.receive_packet_over_udp()
