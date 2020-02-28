# SAS Viya Administration Resource Kit (SAS Viya ARK)

SAS Viya ARK provides interoperating tools and utilities to help SAS customers prepare for a SAS® Viya® deployment.

## Introduction
SAS Viya ARK is a collection of resources to automate and streamline tasks that are required to prepare an environment for a SAS Viya deployment.

The master branch supports the latest release of SAS Viya.   Visit the releases page for specific information about SAS Viya-ARK and related SAS Viya product releases.

SAS Viya ARK provides the following types of assistance:

  * Pre-deployment assessment and optional configuration
  * Post-deployment automation and utilities
  * Upgrade task automation
  * Infrastructure templates

## Prerequisites for SAS Viya ARK
Obtain the latest version of SAS Viya ARK with every new software order.

Each item that is included in the resource kit provides a document that describes its specific prerequisites and functionality.

For example, a functioning [Ansible Controller](http://docs.ansible.com/ansible/latest/intro_installation.html) is required to run  the Ansible playbooks that are included below in the [Pre-installation Playbook](playbooks/pre-install-playbook) section. A list of the available playbooks is provided.

## Index of Tools
Tool support for the latest release of SAS Viya:

* [Pre-installation of SAS Viya System Requirements](playbooks/pre-install-playbook)
* [SAS Viya Deployment Report](playbooks/deployment-report)
* [SAS Viya Multi-Machine Services Utilities](playbooks/viya-mmsu)
* [SAS Viya Upgrade Task Playbooks](playbooks/viya-upgrade)
* [Merge SAS Viya Deployment Files](playbooks/merge-playbook)
* [Home Directory Creator](playbooks/home-directory-creator)
* [SAS Data Server Utility Script](utilities/postgres/viya)
* [SAS Viya LDAP Validator](playbooks/ldap-validator)

Related Tools Not Contained in SAS Viya ARK:
* SAS Viya ARK only supports Linux.  For Windows supporting tools, go to [SAS Viya Deployment Assistant for Windows](https://support.sas.com/en/documentation/install-center/viya/deployment-tools/34/deployment-assistant-windows.html).

## Known Support Issues
The following issues are known and may impact the expected usage or performance of the Viya ARK tools.

* SAS Viya 3.5 supports Linux on Power on a limited availability basis. The SAS Viya ARK tools do not support Linux on Power in the Viya35-ark-1.0 release.

## License

This project is licensed under the [Apache 2.0 License](LICENSE).