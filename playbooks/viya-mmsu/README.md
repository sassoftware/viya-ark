# SAS Viya Administration Resource Kit (Viya-ARK) - Viya Multi-Machine Services Utilities Playbooks

## Introduction
The Viya Multi-Machine Services Utilities repository contains a set of playbooks to start or stop the SAS Viya services gracefully across the 1 - n machines that are identified in the inventory.ini file.

## Requirements for Running the Viya Multi-Machine Services Utilities Playbooks
The Viya Multi-Machine Services Utilities playboooks require a successful SAS Viya deployment for 1 - n machines.
* All services must have an Up status after the deployment has completed.
  See "Running the Playbooks" for instructions on listing the status of SAS Viya services.
* The Viya Multi-Machine Services Utilities playbooks must be placed under the sas_viya_playbook directory where SAS Viya was deployed. 
  The directory structure of this project must be preserved.
  For example: ```sas_viya_playbook/viya-ark/playbooks/viya-mmsu/```
* The Viya Multi-Machine Services Utilities playbooks must be run from the same Ansible controller with SAS Viya deployment playbooks in place.
* Multi-tenant deployments are not supported.
* Verify that the sas-viya-all-services script is exempted from system reboots. This step prevents the script from executing automatically when the machine is restarted.

## Running the Playbooks
To list the status of all SAS Viya services and URLs, execute:
```
ansible-playbook viya-ark/playbooks/viya-mmsu/viya-services-status.yml
```
To exempt sas-viya-all-services from system reboots, execute:
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
