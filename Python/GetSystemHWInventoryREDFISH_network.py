#! /usr/bin/env python3

# Gets network cards info from iDRAC and can be imported in another py script, inspired by
# https://github.com/dell/iDRAC-Redfish-Scripting/blob/master/Redfish%20Python/GetSystemHWInventoryREDFISH.py
# Bogdan Adrian Burciu 25/08/2021 vers 1


# Copyright (c) 2018, Dell, Inc.


from datetime import datetime

import argparse
import json
import os
import re
import requests
import sys
import time
import warnings
import logging

warnings.filterwarnings("ignore")


def main(argv=sys.argv[1:]):
    # expects idrac_ip, idrac_username, idrac_password
    try:
        os.remove("hw_inventory.txt")
    except Exception as exc:
        logging.exception(exc)
        pass

    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)
    idrac_ip = sys.argv[0]
    idrac_username = sys.argv[1]
    idrac_password = sys.argv[2]

    file = open("hw_inventory.txt", "a")
    d = datetime.now()
    current_date_time = "- Data collection timestamp: %s-%s-%s  %s:%s:%s\n" % (
        d.month, d.day, d.year, d.hour, d.minute, d.second)
    file.writelines(current_date_time)
    file.close()

    def check_supported_idrac_version():
        response = requests.get('https://%s/redfish/v1/Systems/System.Embedded.1' % idrac_ip, verify=False,
                                auth=(idrac_username, idrac_password))
        if response.status_code != 200:
            print("\n- WARNING, iDRAC version installed does not support this feature using Redfish API")
            sys.exit()
        else:
            pass

    def get_network_information():
        file = open("hw_inventory.txt", "a")
        response = requests.get('https://%s/redfish/v1/Systems/System.Embedded.1/NetworkInterfaces' % idrac_ip,
                                verify=False, auth=(idrac_username, idrac_password))
        data = response.json()
        if response.status_code != 200:
            print("\n- FAIL, get command failed, error is: %s" % data)
            sys.exit()
        message = "\n---- Network Device Information ----"
        file.writelines(message)
        file.writelines("\n")
        print(message)
        network_uri_list = []
        for i in data['Members']:
            network = i['@odata.id']
            network_uri_list.append(network)
        if not network_uri_list:
            message = "\n- WARNING, no network information detected for system\n"
            file.writelines(message)
            file.writelines("\n")
            print(message)
        for i in network_uri_list:
            message = "\n- Network device details for %s -\n" % i.split("/")[-1]
            file.writelines(message)
            file.writelines("\n")
            print(message)
            i = i.replace("Interfaces", "Adapters")
            response = requests.get('https://%s%s' % (idrac_ip, i), verify=False, auth=(idrac_username, idrac_password))
            data = response.json()
            if response.status_code != 200:
                print("\n- FAIL, get command failed, error is: %s" % data)
                sys.exit()
            for ii in data.items():
                if ii[0] == 'NetworkPorts':
                    url_port = ii[1]['@odata.id']
                    response = requests.get('https://%s%s' % (idrac_ip, url_port), verify=False,
                                            auth=(idrac_username, idrac_password))
                    data = response.json()
                    if response.status_code != 200:
                        print("\n- FAIL, get command failed, error is: %s" % data)
                        sys.exit()
                    else:
                        port_uri_list = []
                        for j in data['Members']:
                            port_uri_list.append(j['@odata.id'])
                if ii[0] == '@odata.id' or ii[0] == '@odata.context' or ii[0] == 'Metrics' \
                        or ii[0] == 'Links' or ii[0] == '@odata.type' \
                        or ii[0] == 'NetworkDeviceFunctions' or ii[0] == 'NetworkPorts':
                    pass
                elif ii[0] == "Controllers":
                    file.writelines(message)
                    print(message)
                    message = "FirmwarePackageVersion: %s" % ii[1][0]['FirmwarePackageVersion']
                    file.writelines(message)
                    file.writelines("\n")
                    print(message)
                else:
                    message = "%s: %s" % (ii[0], ii[1])
                    file.writelines(message)
                    file.writelines("\n")
                    print(message)
            for z in port_uri_list:
                response = requests.get('https://%s%s' % (idrac_ip, z), verify=False,
                                        auth=(idrac_username, idrac_password))
                data = response.json()
                if response.status_code != 200:
                    print("\n- FAIL, get command failed, error is: %s" % data)
                    sys.exit()
                else:
                    message = "\n- Network port details for %s -\n" % z.split("/")[-1]
                    file.writelines(message)
                    file.writelines("\n")
                    print(message)
                    for ii in data.items():
                        if ii[0] == '@odata.id' or ii[0] == '@odata.context' or ii[0] == 'Metrics' or ii[
                            0] == 'Links' or \
                                ii[0] == '@odata.type':
                            pass
                        elif ii[0] == 'Oem':
                            try:
                                for iii in ii[1]['Dell']['DellSwitchConnection'].items():
                                    if iii[0] == '@odata.context' or iii[0] == '@odata.type':
                                        pass
                                    else:
                                        message = "%s: %s" % (iii[0], iii[1])
                                        file.writelines(message)
                                        file.writelines("\n")
                                        print(message)
                            except Exception as exc:
                                logging.exception(exc)
                                pass
                        else:
                            message = "%s: %s" % (ii[0], ii[1])
                            file.writelines(message)
                            file.writelines("\n")
                            print(message)
        file.close()

    check_supported_idrac_version()
    get_network_information()


if __name__ == "__main__":
    main()

