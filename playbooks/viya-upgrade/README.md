# SAS Viya Administration Resource Kit (SAS Viya ARK) - SAS Viya Upgrade Task Playbooks
This area of SAS Viya ARK provides two playbooks which help automate some of the tasks from the SAS Viya upgrade process:
* ```viya-pre-upgrade.yml```:   This playbook automates some of the tasks required prior to performing a SAS Viya upgrade.
* ```viya-post-upgrade.yml```:  This playbook automates some of the tasks required after performing a SAS Viya upgrade.


# Instructions
The SAS Viya upgrade process is used to deploy a new SAS Viya order that may contain significant feature changes or improvements to deployed software or add-on products to be installed as part of the process. These instructions provide guidance on the order in which these steps should be performed in tandem with the documented instructions for upgrading SAS Viya in the deployment guide.

> **Note**: The Ansible ```--check``` mode is not supported by the SAS Viya Upgrade Task Playbooks.

1. Follow the instructions in the appropriate section of the *SAS Viya 3.4 for Linux: Deployment Guide* or *SAS Viya 3.5 for Linux: Deployment Guide*, located [here for SAS Viya 3.4](https://go.documentation.sas.com/?docsetId=dplyml0phy0lax&docsetTarget=n07ugb1h3rhjqjn1equl5zhx8hhd.htm&docsetVersion=3.4&locale=en) and [here for SAS Viya 3.5](https://go.documentation.sas.com/?docsetId=dplyml0phy0lax&docsetTarget=n07ugb1h3rhjqjn1equl5zhx8hhd.htm&docsetVersion=3.5&locale=en). When that document directs you to return to this page, continue with the instructions below.
2. Clone or download the SAS Viya ARK project into the new ```sas_viya_playbook``` directory. The directory structure of this project must be preserved. For example: ```sas_viya_playbook/viya-ark/playbooks/viya-upgrade/```
3. If you are upgrading to SAS Viya 3.4 or SAS Viya 3.5 from earlier versions of Viya, the [Pre-installation of Viya System Requirements](../pre-install-playbook) can be run to ensure the latest Viya system requirements are met.
4. Modify the viya-upgrade variables file ```viya-ark/playbooks/viya-upgrade/vars.yml``` to set the following properties:
  * ```SAS_ADMIN_USERNAME```, ```SAS_ADMIN_PASSWORD```: provide SAS Administrator credentials. This is required for certain tasks to perform.
  * ```SAS_TENANT_DETAILS```: if using a multi-tenant deployment, provide a list of each tenant ID and SAS Administrator credentials.
5. If you are using Ansible 2.8 with a downloaded Viya-ARK project, create a required symlink (**Note**: This step is not required if the Viya-ARK project was cloned or if you are using Ansible 2.7 or earlier). From the ```sas_viya_playbook``` directory, run:
```commandline
cd viya-ark/playbooks/viya-upgrade
ln -sf ../deployment-report/library/ .
cd ../../..
```
6. Run the Pre-Upgrade playbook from the new ```sas_viya_playbook``` directory:
```
ansible-playbook viya-ark/playbooks/viya-upgrade/viya-pre-upgrade.yml
```
7. After the Pre-Upgrade playbook has completed, it will generate a pre-upgrade summary HTML report that can be opened in any browser to view the results: ```sas_viya_playbook/viya_upgrade_output/viya_pre_upgrade_summary_<timestamp>.html```
If there are any errors listed in the report, remediate the issue and then run the Pre-Upgrade playbook again. Repeat this step until the playbook runs without errors.
8. Return to the *SAS Viya 3.4 for Linux: Deployment Guide* or *SAS Viya 3.5 for Linux: Deployment Guide* and continue the instructions there until directed to return to this page.
9. After the SAS Viya upgrade deployment has completed successfully, run the Post-Upgrade playbook from the new ```sas_viya_playbook``` directory:
```
ansible-playbook viya-ark/playbooks/viya-upgrade/viya-post-upgrade.yml
```
10. After the Post-Upgrade playbook has completed, it generates a post-upgrade summary HTML report that can be opened in any browser to view the results: ```sas_viya_playbook/viya_upgrade_output/viya_post_upgrade_summary_<timestamp>.html```
If there are any errors listed in the report, remediate the issue and then run the Post-Upgrade playbook again. Repeat this step until the playbook runs without errors.
11. Return to the *SAS Viya 3.4 for Linux: Deployment Guide* or *SAS Viya 3.5 for Linux: Deployment Guide* to complete the post-upgrade tasks.

## Pre-Upgrade Task Details
The following tagged tasks are automated as part of the ```viya-pre-upgrade.yml``` playbook, which can be run individually using the ansible ```--tags``` command line parameter, or skipped using ```--skip-tags```, if desired:
* ```tag: run-deployment-report```: Record the pre-upgrade state of installed services and packages
* ```tag: check-disk-space```: Check disk space prior to upgrade
* ```tag: verify-postgres-server```: Verify health of the SAS Infrastructure Data Server
* ```tag: stop-tenant-services```: Stop all tenant services
* ```tag: update-casuser```: Add a non-default casenv_user to the sas group
* ```tag: delete-default-backup-job```: Delete the default backup schedule job
* ```tag: save-vta-topics-tables```: Save SAS Visual Text Analytics topics tables
* ```tag: delete-mmlibs-caslib```: Delete mmLibs caslib if it exists

## Post-Upgrade Task Details
The following tagged tasks are automated as part of the ```viya-post-upgrade.yml``` playbook, which can be run individually using the ansible ```--tags``` command line parameter, or skipped using ```--skip-tags```, if desired:
* ```tag: run-deployment-report```: Record the post-upgrade state of installed services and packages
* ```tag: cas-user-formats```: Copy default user formats from casstartup.lua_*epoch file to casstartup_usermods.lua
* ```tag: add-new-caslib-controls```: Update access controls on SAS-created caslibs
* ```tag: update-guest-access-rules```: Update guest access authorization rules

## Additional Upgrade Playbooks
The following plays are run separate from the pre-upgrade and post-upgrade playbooks:
- ##### Archive Obsolete Log Folders
  - The `archive_obsolete_log_folders.yml` playbook archives a specific set of directories that are related to services and components from previous SAS Viya versions that have now been discontinued or have merged with other services and components.
  - The playbook contains the list of obsoleted directories for archiving. By default, the playbook looks for these directories under _/opt/sas/viya/config/var/log_ and moves them to _/opt/sas/viya/config/var/log/archived_.
  - The playbook has `become_user` set to "sas" and all tasks are run as the sas user by default.
  - The log directory path is set in variable `viya_log_path` and is _/opt/sas/viya/config/var/log_ by default.  The archive path is set in variable `viya_log_archive_path` and is _/opt/sas/viya/config/var/log/archived_ by default. You can override the defaults by editing the variables in the playbook file, or on the command line by setting the variables using the -e option:
````
ansible-playbook archive_obsolete_log_folders.yml -i inventory -e "viya_log_archive_path=/example/writable/path"
```` 

## Useful Optional Arguments
* ```-v through -vvvv```: Lets you increase the verbosity of the script output; -vvvv enables connection debugging.
* ```--tags <tag-name>,<another-tag>```: Runs only task(s) with specific tag(s), comma separated if more than one.
* ```--skip-tags <tag-name>,<another-tag>```: Skips task(s) with specific tag(s), comma separated if more than one.
* ```--list-tasks```: Displays all tags in a playbook.

Copyright (c) 2019-2020, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
SPDX-License-Identifier: Apache-2.0

