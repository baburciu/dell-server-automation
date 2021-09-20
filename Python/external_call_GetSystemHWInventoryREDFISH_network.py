#! /usr/bin/env python3

# Import a module (py script) from same dir and sent arguments 

import GetSystemHWInventoryREDFISH_network

GetSystemHWInventoryREDFISH_network.sys.argv=['192.168.X.Y', 'root', 'calvin']
GetSystemHWInventoryREDFISH_network.main()

# ubuntu@netbox-vm:~$ python3 external_call_GetSystemHWInventoryREDFISH_network.py
# 
# ---- Network Device Information ----
# 
# - Network device details for NIC.Integrated.1 -
# 
# Assembly: {'@odata.id': '/redfish/v1/Chassis/System.Embedded.1/Assembly'}
# Assembly: {'@odata.id': '/redfish/v1/Chassis/System.Embedded.1/Assembly'}
# FirmwarePackageVersion: 19.5.12
# Controllers@odata.count: 2
# Description: Network Adapter View
# Id: NIC.Integrated.1
# Manufacturer: Intel Corporation
# Model: Intel(R) 2P X710/2P I350 rNDC
# Name: Network Adapter View
# PartNumber: 06VDPG
# SerialNumber: MYFLMIT09502FB
# Status: {'Health': 'OK', 'HealthRollup': 'OK', 'State': 'Enabled'}
# :
# - Network port details for NIC.Slot.1-1 -

# ActiveLinkTechnology: Ethernet
# AssociatedNetworkAddresses: ['40:A6:B7:43:8F:80']
# CurrentLinkSpeedMbps: 25000
# Description: Network Port View
# EEEEnabled: None
# FlowControlConfiguration: None
# FlowControlStatus: None
# Id: NIC.Slot.1-1
# LinkStatus: Up
# Name: Network Port View
# NetDevFuncMaxBWAlloc: [{'MaxBWAllocPercent': None, 'NetworkDeviceFunction': {'@odata.id': '/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters/NIC.Slot.1/NetworkDeviceFunctions/NIC.Slot.1-1-1'}}]
# NetDevFuncMaxBWAlloc@odata.count: 1
# NetDevFuncMinBWAlloc: [{'MinBWAllocPercent': None, 'NetworkDeviceFunction': {'@odata.id': '/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters/NIC.Slot.1/NetworkDeviceFunctions/NIC.Slot.1-1-1'}}]
# NetDevFuncMinBWAlloc@odata.count: 1
# PhysicalPortNumber: 1
# Status: {'State': 'Enabled', 'Health': 'OK', 'HealthRollup': 'OK'}
# SupportedEthernetCapabilities: []
# SupportedEthernetCapabilities@odata.count: 0
# SupportedLinkCapabilities: [{'AutoSpeedNegotiation': True, 'LinkNetworkTechnology': 'Ethernet', 'LinkSpeedMbps': 25000}]
# SupportedLinkCapabilities@odata.count: 1
# VendorId: 8086
# WakeOnLANEnabled: None
