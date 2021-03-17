## Ansible playbooks usage for Dell server automation, based on Galaxy collection https://github.com/dell/dellemc-openmanage-ansible-modules

## 0. How to install Ansible Galaxy collection to correct path:

boburciu@WX-5CG020BDT2:~$ ` ansible-config list | grep COLLECTIONS_PATHS -C1 ` # verify default location for the collections, so that the new modules can be read by Ansible cfg
```
    Ansible version
COLLECTIONS_PATHS:
  default: ~/.ansible/collections:/usr/share/ansible/collections
--
  env:
  - name: ANSIBLE_COLLECTIONS_PATHS
  - name: ANSIBLE_COLLECTIONS_PATH
 
boburciu@WX-5CG020BDT2:~$
boburciu@WX-5CG020BDT2:~$
``` 
boburciu@WX-5CG020BDT2:~$ ` ansible-galaxy collection install dellemc.openmanage  --collections-path ~/.ansible/collections ` # installing the collection of roles in proper location
boburciu@WX-5CG020BDT2:~$ ` pip3 install omsdk --upgrade ` # installing Dell EMC OMSDK library 

## 1. How to run:
boburciu@WX-5CG020BDT2: ~$ ` cd ~/dell-ansible-automation ` <br/>
boburciu@WX-5CG020BDT2:~/dell-ansible-automation$  <br/>
boburciu@WX-5CG020BDT2:~/dell-ansible-automation$ ` cat hosts.yml `  <br/>
```
[idrac]
Dell_PowerEdge_R640,   idrac_ip='192.168.201.53',  idrac_user='root',  idrac_password='Orange123#'
Dell_PowerEdge_7640,   idrac_ip='192.168.201.54',  idrac_user='root',  idrac_password='Orange123#'
# docker_netbox_19216820023 ansible_host=192.168.200.23

```
boburciu@WX-5CG020BDT2:~/dell-ansible-automation$ ` ansible-playbook -i ./hosts.yml idrac_system_info.yml -v `  <br/>
```
Using /etc/ansible/ansible.cfg as config file

PLAY [Get system inventory] *****************************************************************************************

TASK [Get system inventory.] ****************************************************************************************
fatal: [Dell_PowerEdge_7640,]: FAILED! => {"ansible_facts": {"discovered_interpreter_python": "/usr/bin/python3"}, "changed": false, "msg": "Could not find device driver for iDRAC with IP Address: 192.168.201.54,"}
fatal: [Dell_PowerEdge_R640,]: FAILED! => {"ansible_facts": {"discovered_interpreter_python": "/usr/bin/python3"}, "changed": false, "msg": "Could not find device driver for iDRAC with IP Address: 192.168.201.53,"}

PLAY RECAP **********************************************************************************************************
Dell_PowerEdge_7640,       : ok=0    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=0
Dell_PowerEdge_R640,       : ok=0    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=0

```
