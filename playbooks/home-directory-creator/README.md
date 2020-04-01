# SAS Viya Administration Resource Kit (SAS Viya ARK) - Home Directory Creator Playbook

## Introduction
This playbook enables the automatic creation of user home directories in SAS 9.x and SAS Viya environments. Home directories are required for users of multiple SAS Viya products, including SAS Studio and SAS Visual Data Mining and Machine Learning. They are also required for users of multiple SAS 9 applications.

It was inspired by [a blog post from Paul Homes](https://platformadmin.com/blogs/paul/2017/04/sas-user-linux-home-dir-auto-creation/). (Read the post for some background information).

The Home Directory Creator playbook modifies various sasauth files so that they call a script that triggers the creation of a user's home directory. This method should work for both SAS 9.x and SAS Viya.

## Prerequisites for Running the Home Directory Creator Playbook
Before running this playbook, take the following steps:
* Install Ansible. Version 2.3.2 is recommended.
* Be aware that the playbook makes modifications to the system unless it is run with the ```--check``` option.
* To run the playbook on multiple machines, you can update the inventory file to include additional hosts.
  * See the [Ansible Documentation](http://docs.ansible.com/ansible/latest/intro_inventory.html) for instructions.
  * By default, this playbook will execute on all machines in the sas_all host group.
* Do not use a softlink for sasauth in /etc/pam.d.
* Review the list labeled "sasauth_locations" in the vars section of home-directory-creator.yml and verify that it covers the auth files that you need.

## Running the Playbook

To run this playbook, execute the following command:
```
ansible-playbook home-directory-creator.yml -i <your.inventory.ini>
```

## Useful Optional Arguments

* ```--check```: Executes a "dry run" of the playbook. Runs the playbook without making changes to the system. Any modules that are instrumented to support "check mode" will report the changes that they would have made rather than make them.
* ```-v``` through ```-vvvv```: Lets you increase the verbosity of the script output; ```-vvvv``` enables connection debugging.
* ```-i <host-inventory-file>```: Lets you use a different host inventory file instead of the default /etc/ansible/host file.
* ```--tags <tag-name>```: Runs only task(s) with specific tag(s).
* ```--skip-tags <tag-name>```: Skips task(s) with specific tag(s).
* ```--list-tasks```: Displays all tags in a playbook.

To see a list of tasks that you can run:
```
ansible-playbook home-directory-creator.yml -i inventory --list-tasks
```
These specific tags run the code that performs the home directory configuration checks and changes:
* service
* script
* authfilemodif

Copyright (c) 2019, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
SPDX-License-Identifier: Apache-2.0 

