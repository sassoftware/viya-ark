# SAS Viya Administration Resource Kit (SAS Viya ARK) - Pre-installation Playbook

## Introduction
This playbook verifies and optionally performs many of the tasks that are required to prepare the environment for a typical SAS Viya deployment.

Use this playbook to prepare for a deployment of SAS Viya 3.4 or SAS Viya 3.5.

This playbook does not require you to provide the details of your software order.  It will therefore apply all the pre-requisites for SAS Visual Analytics, SAS Visual Statistics, and SAS Visual Data Mining and Machine Learning, on all machines, regardless of their role.


## Prerequisites for Running the Pre-installation Playbook
Before running this playbook, perform the following steps:
* Install a supported version of Ansible.
* Verify that the user has sudoers privileges.
* Be aware that the playbook makes modifications to the system unless it is run with the --check option.
* The base inventory file that SAS Viya ARK provides contains only localhost and will only run on the machine where it was installed. To run the playbook on multiple machines, you can update the inventory file to include additional hosts. See the [Ansible Documentation](http://docs.ansible.com/ansible/latest/intro_inventory.html) for instructions.
* The machine memory check is based on a single-machine deployment.  If you have a multi-machine deployment with machines containing less than 80.0 GB of RAM, add the --skip-tags skipmemfail argument to the command line to bypass the check.
* Be aware that roles/viya-ark.preinstall/defaults/main.yml may have default values that differ from your environment. For example, an existing group ID may not match the default. The main.yml file can be edited to match your environment before executing the playbook.

## Running the Playbook
To run the playbook, execute the following command:
  ```
  ansible-playbook viya_pre_install_playbook.yml -i pre-install.inventory.ini
  ```

## Useful Optional Arguments
* ```--check```: Executes a "dry run" of the playbook, running the playbook without making changes to the system. Any modules that are instrumented to support "check mode" will report the changes that they would have made rather than make the changes.
* ```-v through -vvvv```: Lets you increase the verbosity of the script output; -vvvv enables connection debugging.
* ```-i <host-inventory-file>```: Lets you use a different host inventory file instead of the default /etc/ansible/host file.
* ```--tags <tag-name>```: Runs only task(s) with specific tag(s).
* ```--skip-tags <tag-name>```: Skips task(s) with specific tag(s).
* ```--list-tasks```: Displays all tags in a playbook.
* ```viya_version```: As an extra parameter, invokes release-specific behavior.  Usage: -e viya_version=3.4

# Index of Tags for Requirement Checks within the Playbook
To see a list of tasks that you can run:
  ```
  ansible-playbook viya_pre_install_playbook.yml -i pre-install.inventory.ini --list-tasks
  ```
Here's an example of running only a specific check or configuration:
  ```
  ansible-playbook viya_pre_install_playbook.yml -i pre-install.inventory.ini --tags memory_check
  ```

## Functional Differences Between SAS Viya 3.4 and SAS Viya 3.5
In SAS Viya 3.5, there are some notable changes to pre-install playbook behavior when compared to SAS Viya 3.4.   The ```viya_version``` parameter in roles/viya-ark.preinstall/defaults/main.yml is defaulted to "3.5" for SAS Viya ARK releases that correspond to the SAS Viya 3.5 product.  Prior releases of SAS Viya ARK will have that parameter defaulted to "3.4".  You can identify Viya ARK releases by visiting the releases page for SAS Viya ARK.

### What Version of SAS Viya is SAS Viya ARK Expecting by Default?
Now that the ```viya_version``` parameter governs release-specific behavior, it may be useful to know, and control, the value of that parameter.   If you don't want to examine the value of this parameter by editing the default/main.yml file, you can determine the default value of ```viya_version``` by running the playbook with the ```show_viya_version``` tag.
   ```
   ansible-playbook viya_pre_install_playbook.yml -i pre-install.inventory.ini -t show_viya_version
   ```
You can control whether SAS Viya 3.5 or SAS Viya 3.4 behavior is exhibited by the pre-install playbook by manipulating ```viya_version``` as an extra parameter.   Since a goal of SAS Viya ARK as is compatiblity with the previous release of SAS Viya, using ```viya_version``` can be useful if you need to run a very recent release of SAS Viya ARK pre-install playbook that defaults to ```viya_version: 3.5``` in an environment being prepared for a SAS Viya 3.4 installation.
   ```
   ansible-playbook viya_pre_install_playbook.yml -i pre-install.inventory.ini [OPTIONS] --extra-vars viya_version=[3.4|3.5]
   ```

### SELinux Configuration
For SAS Viya 3.4, if SELinux is enabled, the pre-install playbook will ensure that the mode is configured to "permissive", a requirement of SAS Viya 3.4.  SAS Viya 3.5 has relaxed that requirement, so the pre-install playbook's behavior is different.   

For SAS Viya 3.5, if SELinux is enabled and the mode is already "permissive" then nothing happens.  Subsequent SELinux-related tasks are skipped.  If the mode is set to "enforcing", the pre-install playbook will fail and a message directing the user to take the necessary actions will be given.

You can elicit the SAS Viya 3.4 behavior by passing in extra parameter ```-e viya_version=3.4```.  **Be aware:** If you do not specify just the ```selinux_config``` task, you might invoke behaviors specific to SAS Viya 3.4 from other parts of the pre-install playbook rather than the default SAS Viya 3.5 behaviors.

### Supported Java Runtime Environment (JRE) Versions
Due to some compatibility issues with some components of SAS Viya 3.5, a minimum version of Java is now required.  That minimum version can be found by examining the  ```min_java_version``` variable in roles/viya-ark.preinstall/defaults/main.yml.

The tasks controlled by the ```required_packages_config``` tag will have different behavior in SAS Viya 3.5.  If there is a previously installed Java and that version is less than the minimum version required for SAS Viya 3.5, the playbook will fail and report the version mismatch.  If no Java is installed, the latest available Java will be installed and the minimum version check tasks will be executed.  The "latest" Java is determined by the value of ```java_openjdk_version``` found in roles/viya-ark.preinstall/vars/(OS-specific).yml.  The actual version of Java that is installed is therefore dependent on what version is available in the repositories set up for the environment.

### Required package version for RHEL deployments
Starting with SAS Viya 3.5, minimum versions of certain packages are now required for standard RHEL deployments; please note that this does NOT apply to deployments on Oracle RHEL, or PowerLinux RHEL (ppc architecture).  The required packages and minimum versions can be found by examining the  ```required_package_versions_rhel``` variable in roles/viya-ark.preinstall/defaults/main.yml. These packages must either be already installed at the minimum version specified, or available in a registered repository at deployment time. The pre-install playbook will fail execution if neither of these conditions are met.

Copyright (c) 2019-2020, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
SPDX-License-Identifier: Apache-2.0
