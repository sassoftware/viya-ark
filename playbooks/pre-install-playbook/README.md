# SAS Viya Administration Resource Kit (Viya-ARK) - Pre-installation Playbook

## Introduction
This playbook verifies and optionally performs many of the tasks that are required to prepare the environment for a typical SAS Viya deployment.

Use this playbook to prepare for a deployment of SAS Viya 3.4.

This playbook does not require you to provide the details of your software order.  It will therefore apply all usual pre-reqs for SAS Visual Analytics, SAS Visual Statistics, and SAS Visual Data Mining and Machine Learning, on all machines, regardless of their role. 


## Prerequisites for Running the Pre-installation Playbook
Before running this playbook, take the following steps:
* Install a supported version of Ansible.
* Verify that the user has sudoers privileges.
* Be aware that the playbook makes modifications to the system unless it is run with the --check option.
* The base inventory file that SAS Viya-ARK provides contains only localhost and will only run on the machine where it was installed. 
To run the playbook on multiple machines, you can update the inventory file to include additional hosts. See the [Ansible Documentation](http://docs.ansible.com/ansible/latest/intro_inventory.html) for instructions.

## Running the Playbook
To run the playbook, execute the following command:
  ```
  ansible-playbook viya_pre_install_playbook.yml -i pre-install.inventory.ini
  ```

## Useful Optional Arguments
* ```--check```: Executes a "dry run" of the playbook. Runs the playbook without making changes to the system. Any modules that are instrumented to support "check mode"  will report the changes that they would have made rather than make the changes.
* ```-v through -vvvv```: Lets you increase the verbosity of the script output; -vvvv enables connection debugging.
* ```-i <host-inventory-file>```: Lets you use a different host inventory file instead of the default /etc/ansible/host file.
* ```--tags <tag-name>```: Runs only task(s) with specific tag(s).
* ```--skip-tags <tag-name>```: Skips task(s) with specific tag(s).
* ```--list-tasks```: Displays all tags in a playbook.

# Index of Tags for Requirement Checks within the Playbook
To see a list of tasks that you can run:
  ```
  ansible-playbook viya_pre_install_playbook.yml -i pre-install.inventory.ini --list-tasks
  ```
Here's an example of running only a specific check or configuration:
  ```
  ansible-playbook viya_pre_install_playbook.yml -i pre-install.inventory.ini --tags memory_check
  ```
