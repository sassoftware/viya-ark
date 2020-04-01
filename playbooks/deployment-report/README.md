# SAS Viya Administration Resource Kit (SAS Viya ARK) - SAS Viya Deployment Report Playbook

## Introduction
This playbook gathers information about SAS Viya software and the hosts where it is deployed.
Furthermore, it optionally compares the packages installed on the system with the most up to 
date versions to determine which hot fixes have not been applied.  The data gathered is then 
written to disk as a YAML-formatted data file and a static web-page for easily viewing the data. 

Hot fix information in the report include:
* The hot fixes not applied
* The release date of each hotfix
* Each package and version associated with the hotfix
* The number and title of each SASNote associated with the hotfix

Deployment attributes in the report include:
* Operating system information and architecture
* The SAS-defined Ansible host groups installed on a host
* A snapshot of memory, filesystem, and SAS installation root resources
* A listing of all SAS RPM packages installed on a host and each package's attributes
* A listing of all system services delivered by SAS and each service's attributes

The deployment report playbook does not make any changes to the hosts in the provided inventory file,
unless that host is also the Ansible controller, where the YAML-formatted data file and static web page
are written to disk.

The output files written to the `sas_viya_playbook/` are:
* viya_deployment_report_data_*\<timestamp\>*.yml
* viya_deployment_report_*\<timestamp\>*.html

## Prerequisites for Running the Deployment Report Playbook
* Install a supported version of Ansible.
* Install SAS Viya software using the SAS-provided `sas_viya_playbook`.
* Obtain a local copy of the inventory file used when deploying the SAS Viya software.
* Verify that the user has sudoers privileges.
* Connectivity to sas.com (for the Hotfix Report Only)

## Running the Playbook
To run the playbook, execute the following command:
  ```bash
  ansible-playbook viya-ark/playbooks/deployment-report/viya-deployment-report.yml
  ```
> **Note**: `inventory_file` should be replaced by the path to the inventory file used when deploying the SAS Viya software.

## Optional Arguments

To create a report which contains a listing of files installed by each package:
  ```bash
  ansible-playbook viya-ark/playbooks/deployment-report/viya-deployment-report.yml -e "include_package_files=true"
  ```
> **Note**: including this option will greatly increase the size of the report and report data.

To create a report using existing data:
  ```bash
  ansible-playbook viya-ark/playbooks/deployment-report/viya-deployment-report.yml -e "existing_data_file=<path_to_data_file>"
  ```

To exclude the static web page and only create the report data:
  ```bash
  ansible-playbook viya-ark/playbooks/deployment-report/viya-deployment-report.yml -e "exclude_html=true"
  ```

To force the creation of the report files into the current directory:
  ```bash
  ansible-playbook viya-ark/playbooks/deployment-report/viya-deployment-report.yml -e "output_dir=./"
  ```

To exclude the hotfix report:
  ```bash
  ansible-playbook viya-ark/playbooks/deployment-report/viya-deployment-report.yml -e "include_hotfix_report=False"
  ```
To specify an alternate location for the published hotfix data:
  ```bash
  ansible-playbook viya-ark/playbooks/deployment-report/viya-deployment-report.yml -e "hotfix_url=<URL_To_Hotfix_List>"
  ```
Copyright (c) 2019-2020, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
SPDX-License-Identifier: Apache-2.0
