# SAS Viya Administration Resource Kit (Viya-ARK) - Viya Multi-Machine Services Utilities Playbooks

## Introduction
The Viya Multi-Machine Services Utilities repository contains a set of playbooks to start or stop the SAS Viya services gracefully across the 1 - n machines that are identified in the inventory.ini file.

## Requirements for Running the Viya Multi-Machine Services Utilities Playbooks
* All services must have an Up status after the deployment has completed.
  See "Running the Playbooks" for instructions on listing the status of SAS Viya services.
* The Viya Multi-Machine Services Utilities playbooks must be placed under the sas_viya_playbook directory where SAS Viya was deployed. 
  The directory structure of this project must be preserved. 
  For example: ```sas_viya_playbook/viya-ark/playbooks/viya-mmsu/```
* Support Multi-tenant deployment.
* Verify that the sas-viya-all-services script is exempted from system reboots. This step prevents the script from executing automatically when the machine is restarted.

## Running the Playbooks
To list the status of all SAS Viya services and URLs, execute:
```
ansible-playbook viya-ark/playbooks/viya-mmsu/viya-services-status.yml
```
To exempt sas-viya-all-services from system reboot, execute:
```
ansible-playbook viya-ark/playbooks/viya-mmsu/viya-services-disable.yml
```
To stop all services gracefully, execute:
```
ansible-playbook viya-ark/playbooks/viya-mmsu/viya-services-stop.yml
```
To start all services gracefully, execute:
```
ansible-playbook viya-ark/playbooks/viya-mmsu/viya-services-start.yml
```
To restart all services gracefully, execute:
```
ansible-playbook viya-ark/playbooks/viya-mmsu/viya-services-restart.yml
```

## Tips
* When running playbook viya-services-stop.yml and seeing sas stray processes:
```
    "msg": [
        "Please examine the following stray process(es)",
        "If enable_stray_cleanup=true, it will be cleaned up automatically",
        "This playbook can be rerun to clean up the child procsses",
        [
          ...
        ]
    ]
```
  If the processes listed are ok to be cleaned up, user may issue command as below:
```
    ansible-playbook viya-ark/playbooks/viya-mmsu/viya-services-stop.yml -e "enable_stray_cleanup=true"
```
  or modify viya-services-vars.yml file as following then rerun the playbook.
```
    enable_stray_cleanup: true 
```

