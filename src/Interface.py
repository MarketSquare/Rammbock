import os
class Interface:
    """Interface class for interface handling"""
    
    def create_interface(self, int_alias, ifname, ip_address, netmask):
        os.popen("ifconfig "+ifname+":1 "+ip_address+" netmask "+netmask)

    def is_interface_up (int_alias):
        raise NotImplementedError("This is not ready yet!")
