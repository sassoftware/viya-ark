# SAS Viya Administration Resource Kit (Viya-ARK) - Viya Deployment Report Playbook

## Introduction
This playbook gathers information about SAS Viya software and the hosts where it is deployed.
The data gathered is then written to disk as a YAML-formatted data file and a static web-page for
easily viewing the data. 

Deployment attributes in the report include:
* Operating system information and architecture
* The SAS-defined Ansible host groups installed on a host
* A snapshot of memory, filesystem, and SAS installation root resources
* A listing of all SAS RPM packages installed on a host and each package's attributes
* A listing of all system services delivered by SAS and each service's attributes

The deployment report playbook does not make any changes to the hosts in the provided inventory file,
unless that host is also the Ansible controller, where the YAML-formatted data file and static web-page
are written to disk.

The output files written to the `sas_viya_playbook/` are:
* viya_deployment_report_data_*\<timestamp\>*.yml
* viya_deployment_report_*\<timestamp\>*.html

## Prerequisites for running the Deployment Report Playbook
* Install Ansible. Version 2.4.1 or later is recommended.
* Install SAS Viya software using the SAS-provided `sas_viya_playbook`.
* Obtain a local copy of the inventory file used when deploying the SAS Viya software.
* Verify that the user has sudoers privileges.

## Running the Playbook
To run the playbook, execute the following command:
  ```bash
  ansible-playbook viya-deployment-report.yml -i <inventory_file>
  ```
> **Note**: `inventory_file` should be replaced by the path to the inventory file used when deploying the SAS Viya software.

## Optional Arguments

To create a report which contains a listing of files installed by each package:
  ```bash
  ansible-playbook viya-deployment-report.yml -i <inventory_file> -e "include_package_files=true"
  ```
> **Note**: including this option will greatly increase the size of the report and report data.

To create a report using existing data:
  ```bash
  ansible-playbook viya-deployment-report.yml -i <inventory_file> -e "existing_data_file=<path_to_data_file>"
  ```

To exclude the static web-page and only create the report data:
  ```bash
  ansible-playbook viya-deployment-report.yml -i <inventory_file> -e "exclude_html=true"
  ```

To force the creation of the report files into the current directory:
  ```bash
  ansible-playbook viya-deployment-report.yml -i <inventory_file> -e 'output_dir=./'
  ```
