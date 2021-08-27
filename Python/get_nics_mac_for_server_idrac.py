import os
import re
import GetSystemHWInventoryREDFISH_network

server_idrac_username = 'root'
server_idrac_password = os.environ['IDRAC_ROOT_PASSWORD']
dict_server_port_mac = {}

def get_nics_mac_for_server_idrac(server_idrac_ip):
        # reach out to iDRAC and get the MAC address as dict values for server_port keys
        GetSystemHWInventoryREDFISH_network.sys.argv = [server_idrac_ip, server_idrac_username, server_idrac_password]
        # above saves the network cards inventory from Dell PowerEdge server to local file hw_inventory.txt
        pattern = "^AssociatedNetworkAddresses"
        file = open("hw_inventory.txt", "r")
        lines = file.read()
        lines = lines.splitlines()
        for j, line in enumerate(lines):
                if re.search(pattern, line):
                        next_line = lines[j + 6]
                        print(line)
                        print(next_line)
                        # AssociatedNetworkAddresses: ['78:AC:44:0A:86:42']
                        # Id: NIC.Integrated.1-1
                        # :
                        # AssociatedNetworkAddresses: ['40:A6:B7:3E:83:E1']
                        # Id: NIC.Slot.1-2

                        # choose to collect MAC only for slot NIC cards, as only those go to switches:
                        if "NIC.Slot" in next_line:
                                server_port_mac = line.split('[')[1].split(']')[0]
                                server_port_nic = 'NIC{}-P{}'.format(next_line.split('.')[-1].split('-')[0],
                                                                                                                next_line.split('.')[-1].split('-')[1])
                                dict_server_port_mac[server_port_nic] = server_port_mac
                        else:
                                continue
        print('For server {} the MAC addresses are: \n {}'.format(server_idrac_ip, dict_server_port_mac))

get_nics_mac_for_server_idrac("192.168.70.41")
