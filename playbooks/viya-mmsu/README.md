# SAS Viya Administration Resource Kit (SAS Viya ARK) - SAS Viya Multi-Machine Services Utilities (MMSU) Playbooks 

## Introduction
The SAS Viya Multi-Machine Services Utilities repository contains a set of playbooks to start or stop the SAS Viya services gracefully across the 1 - n machines that are identified in the inventory.ini file.

## Requirements for Running the MMSU Playbooks
* All services must have an Up status after the deployment has completed.
  See "Running the Playbooks" for instructions on listing the status of SAS Viya services.
* The MMSU playbooks must be placed under the sas_viya_playbook directory where SAS Viya was deployed.
  The directory structure of this project must be preserved.
  For example: ```sas_viya_playbook/viya-ark/playbooks/viya-mmsu/```
* Verify that the sas-viya-all-services script is exempted from system reboots. This step prevents the script from executing automatically when the machine is restarted. This can be done by running viya-services-disable.yml playbook.
* sas-viya-all-services script should not be run manually on any machines when using MMSU playbooks.

## Supported deployment of MMSU Playbooks
* Single-machine deployment
* Multi-machines deployment
* Multi-tenant deployment
* Clustered database deployment

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
	"except database processes which require fix manually to avoid data corruption."
        "This playbook can be rerun to clean up the child processes",
        [
          ...
        ]
    ]
```
  If the processes listed are ok to be cleaned up, the user may issue command as below:
```
    ansible-playbook viya-ark/playbooks/viya-mmsu/viya-services-stop.yml -e "enable_stray_cleanup=true"
```
  The user can also modify viya-services-vars.yml file as follows, then rerun the playbook.
```
    enable_stray_cleanup: true
```
Copyright (c) 2019-2020, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
SPDX-License-Identifier: Apache-2.0
