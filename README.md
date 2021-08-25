# Ansible playbooks usage for Dell server automation, based on [Galaxy collection](https://github.com/dell/dellemc-openmanage-ansible-modules) or Python scripts, based on [iDRAC-Redfish](https://github.com/dell/iDRAC-Redfish-Scripting/blob/master/Redfish%20Python/)

## 0. How to install Ansible Galaxy collection to correct path:
boburciu@WX-5CG020BDT2:~$ ` ansible-config list | grep COLLECTIONS_PATHS -C1 ` _# verify default location for the collections, so that the new modules can be read by Ansible cfg_
```
    Ansible version
COLLECTIONS_PATHS:
  default: ~/.ansible/collections:/usr/share/ansible/collections
--
  env:
  - name: ANSIBLE_COLLECTIONS_PATHS
  - name: ANSIBLE_COLLECTIONS_PATH
 
boburciu@WX-5CG020BDT2:~$
``` 
boburciu@WX-5CG020BDT2:~$ ` ansible-galaxy collection install dellemc.openmanage  --collections-path ~/.ansible/collections ` _#installing the collection of roles in proper location_  <br/>

boburciu@WX-5CG020BDT2:~$ ` pip3 install omsdk --upgrade ` _# installing Dell EMC OMSDK library_   <br/>

## 1. How to run:
boburciu@WX-5CG020BDT2:~$ ` cd ~/dell-ansible-automation ` <br/>

boburciu@WX-5CG020BDT2:~/dell-ansible-automation$ ` cat neo_hosts.yml `
```
[idrac]
Dell_Control-3   idrac_ip='127.0.0.1'  idrac_port='44336'  idrac_user='root'  idrac_password='*****' idrac_set_ip='X.X.X.X' idrac_set_gw='X.X.X.Y' idrac_set_mask='255.255.255.0'
:

```
boburciu@WX-5CG020BDT2:~/dell-ansible-automation$ ` ansible-playbook -i neo_hosts.yml --limit Dell_Ceph_server-1:Dell_Control-3 dellemc_get_system_inventory.yml -e 'ansible_python_interpreter="/usr/bin/python3"' -v `  <br/>
