# SAS Viya Administration Resource Kit (SAS Viya ARK) - Merge SAS Viya Deployment Files Playbook
This playbook compares and merges user-edited values from configuration files that were used in a previous SAS Viya deployment with new configuration files used for the SAS Viya upgrade process. The configuration files the playbook handles are ```ansible.cfg```, ```vars.yml```, and ```inventory.ini```.

When you run the playbook, it will prompt you for the location of the current inventory file (which is assumed to be in the same directory as the current ansible.cfg and vars.yml files). You can also provide the location from the command line.

The playbook will create time-stamped backups of your files and write them in place. The merged information is included so that they are ready to use. Your inventory file and vars.yml might include a new host group, ```? choose-target-host```, if you do not pass the merge-playbook argument -e "merge_default_host=<your deployTarget>. In this case, you must manually replace that value in inventory.ini and vars.yml with a valid host name to avoid Ansible warnings and failures. 

The differences between the current and newer inventory files are written to ```sas_viya_playbook/inventory_diff.txt```, and the output of the python script is written to ```sas_viya_playbook/merge_viya_deployment_files.log```.

The playbook will copy the default inventory.ini and vars.yml from the playbook root directory to a time-stamped folder and then update them with the merged information included so that they are ready to use. If your inventory file and vars.yml include a new host group value ```? choose-target-host```, you must manually replace that value to avoid Ansible warnings and failures.

## Requirements for running the Playbook
* Install "ruamel.yaml" in your Python installation by running `pip install ruamel.yaml`
* The Merge SAS Viya Deployment Files playbooks must be placed under a new generated sas_viya_playbook directory where SAS Viya will be deployed, separate from the sas_viya_playbook directory that was previously deployed from.
  The directory structure of this project must be preserved. For example: ```sas_viya_playbook/viya-ark/playbooks/merge-playboook/```
* The following SAS Viya configuration files that were used in the previous deployment must exist in the ```sas_viya_playbook``` directory:
  * ```inventory.ini```
  * ```ansible.cfg```
  * ```vars.yml```


## Running the Playbook
To run the playbook, execute the following example command:
```
ansible-playbook viya-ark/playbooks/merge-playbook/merge-viya-deployment-files.yml -e "current_inventory_file=/local/sas_viya_playbook_CURRENT/inventory.ini -e "merge_default_host=deployTarget"
```
> **Note**: The playbook will prompt you for a fully qualified file path of the current version of the `inventory.ini` file. The current versions of `ansible.cfg and vars.yml` must be in the same directory. You can pass the file path location and the merge default host deployTarget by using the -e option when you run the playbook.


To run the playbook and merge multi-tenant configuration files, execute the following example command:
```
ansible-playbook viya-ark/playbooks/merge-playbook/merge-viya-deployment-files.yml -e "current_inventory_file=/local/sas_viya_playbook_CURRENT/inventory.ini" -e "tenantID_list=acme,intech,york" -e "merge_default_host=deployTarget"
```
> **Note**: The ```<tenantID>_vars.yml``` file is assumed to be in the same directory where the current version of the `inventory.ini` file is saved.

## After the run
The merged configuration files, differences between the current configuration files and the merged ones, and logs can be found in:
```/local/sas_viya_playbook/viya-ark/playbooks/merge-playbook/merged_files/<time_stamp>/```
* ```ansible.cfg```
* ```inventory.ini```
* ```inventory.ini.default```
* ```vars.yml```
* ```merge_viya_deployment_files.log```
* ```inventory_diff.txt```
* ```vars_yml_diff.txt```
* ```ansible_cfg_diff.txt```
* ```<tenantID>_vars.yml```
* ```<tenantID>_vars_yml_diff.txt```

Copyright (c) 2019-2020, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
SPDX-License-Identifier: Apache-2.0
