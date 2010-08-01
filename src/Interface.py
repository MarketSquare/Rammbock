import os
class Interface:
    """Interface class for interface handling"""
    
    def create_interface(self, int_alias, ifname, ip_address, netmask):
        """ Creates interface """
        i = 1
        while if_ip_address  == "":
            virtual_if_name = ifname+":"+i
            if_ip_address == self.get_ip_address(virtual_if_name)
            if if_ip_address = "":
                os.popen("ifconfig "+ifname+":1 "+ip_address+" netmask "+netmask)
            else:
                i++

    def check_interface (self, ifname):
        """Checks if interface have ip address. Returns False or True"""
        ipaddress= self.get_ip_address(ifname)
        print "ipaddress=" +ipaddress 
        if ipaddress == "":
            return False
        else:
            return True

    def del_interface (self, ifname):
        """Deletes given interface"""
        os.popen("ifconfig "+ifname+" down")

    def get_ip_address(self, ifname):
        """
        Returns ip address from local machine. interface name is given as an parameter.
        get_ip_address | <interface>
        e.g. get_ip_address | eth0
        """
        ipAddressList = os.popen("/sbin/ifconfig "+ifname+" | grep inet | awk '{print $2}' | sed -e s/.*://").readlines()
        ipAddress = "".join(ipAddressList)
        ipAddress = ipAddress.strip()
        print ipAddress
        return ipAddress 
