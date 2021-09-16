#! /usr/bin/env python3

# Gets info from NetBox for the cabling input and then goes one by one and checks
# server's MAC is learnt via respective switch port - for new cabling (no lag) and traffic received on all ports
# server's MAC is present on LLDP info on respective switch port - for all scenarios
# Bogdan Adrian Burciu 15/09/2021 vers 2

from pprint import pprint
from netbox import NetBox
import GetSystemHWInventoryREDFISH_network
import re
import os
import napalm
import hashlib


def main():
    netbox = NetBox(host='192.168.71.75', port=443, use_ssl=True, ssl_verify=False,
                    auth_token='b99992f551da58dd64758f0a80fea43d1e001007')
    # the list of ToR names as they are in NetBox
    tor_sw_list = ['SW-WE19-TOR1-B4-NEO', 'SW-WE19-TOR2-B4-NEO']
    tor_sw_napalm_driver = "dellos10"
    tor_sw_napalm_username = "netbox.automation"
    tor_sw_napalm_password: str = "2Pl~P,//>tTdoo^/(|}hTy"
    tor_sw_mac_table = {}
    tor_sw_lldp_mac = {}
    dict_server_port_mac = {}
    napalm_devices = {}
    server_idrac_username = 'root'
    server_idrac_password = os.environ['IDRAC_ROOT_PASSWORD']

    def get_netbox_device_type_id(manufacturer, model):
        netbox_device_types = netbox.dcim.get_device_types()
        for index in range(len(netbox_device_types)):
            if netbox_device_types[index]['manufacturer']['name'] == str(manufacturer) \
                    and netbox_device_types[index]['model'] == str(model):
                print('the model type id for manufacturer {0} model {1} is {2}'.
                      format(netbox_device_types[index]['manufacturer']['name'],
                             netbox_device_types[index]['model'],
                             netbox_device_types[index]['id']))
                return netbox_device_types[index]['id']
    # >>> get_netbox_device_type_id('Dell','PowerEdge R640')
    # the model type id for manufacturer Dell model PowerEdge R640 is 64
    # >>>
    # >>> get_netbox_device_type_id('Dell','PowerEdge R740')
    # the model type id for manufacturer Dell model PowerEdge R740 is 57
    # >>>

    def get_mac_for_tor_port_napalm(tor_sw, tor_sw_port):
        for i in range(len(tor_sw_mac_table[tor_sw])):
            if str(tor_sw_mac_table[tor_sw][i]['interface']) == tor_sw_port:
                return tor_sw_mac_table[tor_sw][i]['mac'].upper()
    # >>> get_mac_for_tor_port_napalm('SW-WE19-TOR1-B4-NEO', 'ethernet1/1/6:1')
    # '40:A6:B7:43:3B:A0'
    # >>>

    def get_lldp_mac_for_tor_port_napalm(tor_sw, tor_sw_port):
        for i in range(len(tor_sw_lldp_mac[tor_sw])):
            if str(tor_sw_lldp_mac[tor_sw][i]['interface']) == tor_sw_port:
                return str(tor_sw_lldp_mac[tor_sw][i]['rem-port-id'].upper())
    # >>> get_lldp_mac_for_tor_port_napalm('SW-WE19-TOR1-B4-NEO', 'ethernet1/1/6:1')
    # '40:A6:B7:43:3B:A0'
    # >>>

    def get_tor_port_for_lldp_mac_napalm(tor_sw_port_lldp_mac):
        for tor_sw in tor_sw_lldp_mac.keys():
            for i in range(len(tor_sw_lldp_mac[tor_sw])):
                if str(tor_sw_lldp_mac[tor_sw][i]['rem-port-id'].upper()) == tor_sw_port_lldp_mac:
                    return [tor_sw, str(tor_sw_lldp_mac[tor_sw][i]['interface'])]
    # >>> get_tor_port_for_lldp_mac_napalm('40:a6:b7:43:a1:30'.upper())
    # ['SW-WE19-TOR1-B4-NEO', 'ethernet1/1/13:4']
    # >>>

    def get_nics_mac_for_server_idrac(server_idrac_ip):
        # reach out to iDRAC and get the MAC address as dict values for server_port keys
        GetSystemHWInventoryREDFISH_network.sys.argv = [server_idrac_ip, server_idrac_username, server_idrac_password]
        GetSystemHWInventoryREDFISH_network.main()
        # above saves the network cards inventory from Dell PowerEdge server to local file hw_inventory.txt
        pattern = "^AssociatedNetworkAddresses"
        file = open("hw_inventory.txt", "r")
        lines = file.read()
        lines = lines.splitlines()
        for j, line in enumerate(lines):
            if re.search(pattern, line):
                next_line = lines[j + 6]
                # print(line)
                # print(next_line)
                # AssociatedNetworkAddresses: ['78:AC:44:0A:86:42']
                # Id: NIC.Integrated.1-1
                # :
                # AssociatedNetworkAddresses: ['40:A6:B7:3E:83:E1']
                # Id: NIC.Slot.1-2

                # choose to collect MAC only for slot NIC cards, as only those go to switches:
                if "NIC.Slot" in next_line:
                    server_port_mac = line.split('[\'')[1].split('\']')[0]
                    server_port_nic = 'NIC{}-P{}'.format(next_line.split('.')[-1].split('-')[0],
                                                         next_line.split('.')[-1].split('-')[1])
                    dict_server_port_mac[server_port_nic] = server_port_mac
                else:
                    continue
        print('\tFor server {} the MAC addresses are: \n{}\n'.format(server_idrac_ip, dict_server_port_mac))
        return dict_server_port_mac
        # >>> get_nics_mac_for_server_idrac('192.168.70.41')
        # For server 192.168.70.41 the MAC addresses are: {
        # 'NIC1-P1': "40:A6:B7:3E:83:E0", 'NIC1-P2': "40:A6:B7:3E:83:E1", 'NIC2-P1': "40:A6:B7:3D:C9:B0",
        # 'NIC2-P2': "40:A6:B7:3D:C9:B1", 'NIC3-P1': "40:A6:B7:3D:C0:E0", 'NIC3-P2': "40:A6:B7:3D:C0:E1"}

    # get the MAC address table from each ToR SW
    napalm_driver = napalm.get_network_driver(tor_sw_napalm_driver)
    for tor_sw in tor_sw_list:
        napalm_devices[tor_sw] = napalm_driver(
            hostname=str(netbox.dcim.get_devices(name=tor_sw)[0]['primary_ip']['address']).split('/')[0],
            username=tor_sw_napalm_username,
            password=tor_sw_napalm_password)

    for tor_sw, napalm_device in napalm_devices.items():
        print("Connecting to {} - IP address {} ...".format(tor_sw, napalm_device.hostname))
        napalm_device.open()

        print("Getting switch MAC address table")
        tor_sw_mac_table[tor_sw] = napalm_device.get_mac_address_table()

        print("Getting switch LLDP info to extract MAC address for peer servers from")
        cmd = "show lldp neighbors"
        # >> > cmd = "show lldp neighbors"
        # >> > lldp_macs = device.cli([cmd])[cmd]
        # >> > print(lldp_macs)
        # Loc
        # PortID
        # Rem
        # Host
        # Name
        # Rem
        # Port
        # Id
        # Rem
        # Chassis
        # Id
        # --------------------------------------------------------------------------------------
        # ethernet1 / 1 / 1: 1
        # Not
        # Advertised
        # 40: a6:b7: 43:8
        # f: 80
        # 40: a6:b7: 43:8
        # f: 80
        tor_sw_lldp_mac[tor_sw] = []
        for cmd_output_line in napalm_device.cli([cmd])[cmd].split('\nethernet'):
            if "Not Advertised" in cmd_output_line:
                tor_sw_port = "ethernet" + cmd_output_line.split("Not Advertised")[0].split('\n')[-1].strip()
                tor_sw_port_lldp_mac = cmd_output_line.split("Not Advertised")[1].split('        ')[0].strip()
                tor_sw_lldp_mac[tor_sw].append({'interface': tor_sw_port, 'rem-port-id': tor_sw_port_lldp_mac})

        napalm_device.close()
        print("Done for {} .".format(napalm_device.hostname))

    # >> > pprint(tor_sw_mac_table)
    # {'SW-WE19-TOR1-B4-NEO': [{'active': True,
    #                           'interface': 'port-channel5',
    #                           'last_move': -1.0,
    #                           'mac': '40:a6:b7:3d:c7:20',
    #                           'moves': -1,
    #                           'static': False,
    #                           'vlan': 1},
    #                          {'active': True,
    #                           'interface': 'port-channel9',
    #                           'last_move': -1.0,
    #                           'mac': '40:a6:b7:3d:c9:b0',
    #                           'moves': -1,
    #                           'static': False,
    #                           'vlan': 1},
    #
    # >> > pprint(tor_sw_lldp_mac)
    # {'SW-WE19-TOR1-B4-NEO': [{'interface': 'ethernet1/1/1:1',
    #                           'rem-port-id': '40:a6:b7:43:8f:80'},
    #                          {'interface': 'ethernet1/1/1:2',
    #                           'rem-port-id': '40:a6:b7:43:8f:70'},
    #                          {'interface': 'ethernet1/1/1:3',
    #                           'rem-port-id': '40:a6:b7:45:55:50'},
    #                          {'interface': 'ethernet1/1/1:4',
    #                           'rem-port-id': '40:a6:b7:3d:d9:a0'},

    # get the concatenated list of all Dell PowerEdge server types, as for each one will check MACs seen on ToR SWs
    netbox_devices_r740 = netbox.dcim.get_devices(device_type_id=get_netbox_device_type_id('Dell', 'PowerEdge R740xd'))
    netbox_devices_r640 = netbox.dcim.get_devices(device_type_id=get_netbox_device_type_id('Dell', 'PowerEdge R640'))
    netbox_devices_servers = netbox_devices_r740xd + netbox_devices_r640

    for i in range(len(netbox_devices_servers)):
        # reach out to iDRAC/iLO/iBMC by server_ip and get the MAC addresses for for each server_port
        server = str(netbox_devices_servers[i]['name'])
        server_ip = str(netbox_devices_servers[i]['primary_ip']['address'].split('/')[0])
        # skipping server "Dell_Compute-2", since it's currently (15.09.2021) out of use
        if server == "Dell_Compute-2":
            continue
        else:
            print("Fetching NIC inventory from iDRAC of {} - IP address {} - via Redfish API".format(server, server_ip))
            dict_server_port_mac = get_nics_mac_for_server_idrac(server_ip)

            netbox_device_interfaces = netbox.dcim.get_interfaces(device=netbox_devices_servers[i]['name'])
            for index in range(len(netbox_device_interfaces)):
                # check if interface is connected in NetBox (has a peer)
                if netbox_device_interfaces[index]['cable_peer']:
                    # print('this end device = {0} interface = {1}; '
                    #       '<=> other end device = {2} interface = {3};'.
                    #       format(str(netbox_device_interfaces[index]['device']['display_name']),
                    #              str(netbox_device_interfaces[index]['name']),
                    #              str(netbox_device_interfaces[index]['cable_peer']['device']['name']),
                    #              str(netbox_device_interfaces[index]['cable_peer']['name'])))
                    if str(netbox_device_interfaces[index]['cable_peer']['device']['name']) in tor_sw_list:
                        server_port = str(netbox_device_interfaces[index]['name'])
                        tor_sw_port = str(netbox_device_interfaces[index]['cable_peer']['name'])
                        tor_sw = str(netbox_device_interfaces[index]['cable_peer']['device']['name'])

                        # check MAC learnt via tor_sw_port, lookup in table fetched previously w NAPALM, is server_port
                        # print('{} port {} MAC={} <=> {} port {} MAC={}'
                        #       .format(server, server_port, dict_server_port_mac[server_port],
                        #               tor_sw, tor_sw_port, get_lldp_mac_for_tor_port_napalm(tor_sw, tor_sw_port)))
                        if not dict_server_port_mac[server_port] == get_lldp_mac_for_tor_port_napalm(tor_sw, tor_sw_port):
                            print('There\'s a problem, {}\'s port {} has MAC={} with MAC hash={}, '
                                  'while {}\'s port has {} MAC={} with MAC hash={}'
                                  .format(server, server_port, dict_server_port_mac[server_port],
                                          hash(dict_server_port_mac[server_port]) % 10 ** 8,
                                          tor_sw, tor_sw_port, get_lldp_mac_for_tor_port_napalm(tor_sw, tor_sw_port),
                                          hash(get_lldp_mac_for_tor_port_napalm(tor_sw, tor_sw_port)) % 10 ** 8))
                            print('It looks like {}\'s port {} with MAC={} is connected to {}\'s port {}\n'
                                  .format(server, server_port, dict_server_port_mac[server_port],
                                          get_tor_port_for_lldp_mac_napalm(dict_server_port_mac[server_port])[0],
                                          get_tor_port_for_lldp_mac_napalm(dict_server_port_mac[server_port])[1]))


if __name__ == '__main__':
    main()
