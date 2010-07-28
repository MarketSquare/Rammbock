import os
class Interface:
    """Interface class for interface handling"""
    
    def create_interface(self, int_alias, ifname, ip_address, netmask):
        """ Creates interface """
        os.popen("ifconfig "+ifname+":1 "+ip_address+" netmask "+netmask)

    def check_interface (self, ifname):
        """Checks if interface have ip address. Returns False or True"""
        ipaddress= self.get_ip_address(ifname)
        if ipaddress == None:
            print "1"
            return False
        else:
            print "2"
            return True

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
