import os
class Interface:

    def __init__(self):
        self.ifname = ""
        self.ifUp = False
    
    def create_interface(self, int_alias, ifname, ip_address, netmask):
        """ Creates interface """
        if_ip_address = "1"
        i = 1
        while if_ip_address  != "":
            virtual_if_name = ifname + ":" + str(i*100)
            if_ip_address = self.get_ip_address(virtual_if_name)
            if if_ip_address == "":
                command = "ifconfig " + virtual_if_name + " " + ip_address + " netmask " + netmask
                print command
                os.popen(command)
                self.ifname = virtual_if_name                
                self.ifUp = True                
                return self
            else:
                i = i+1
        return self

    def check_interface(self):
        """Checks if interface have ip address. Returns False or True"""
        ipaddress= self.get_ip_address(self.ifname)
        print "ipaddress=" + ipaddress 
        if ipaddress == "":
            return False
        else:
            return True

    def del_interface(self):
        """Deletes given interface"""
        print "ifconfig " + self.ifname + " down"
        os.popen("ifconfig " + self.ifname + " down")
        self.ifUp = False

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
