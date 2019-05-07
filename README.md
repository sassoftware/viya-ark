# SAS Viya Administration Resource Kit (Viya-ARK)

SAS Viya-ARK provides interoperating tools and utilities to help SAS customers prepare for a SAS(R) Viya(R) deployment.

## Introduction
SAS Viya-ARK is a collection of resources to automate and streamline tasks that are required to prepare an environment for a SAS Viya deployment.

The master branch supports the latest release of SAS Viya.   Visit the [releases](releases) page for specific information about SAS Viya-ARK and related SAS Viya product releases.

SAS Viya-ARK provides the following types of assistance:

  * Pre-deployment assessment and optional configuration
  * Post-deployment automation
  * Post-deployment utilitites
  * Infrastructure templates

## Prerequisites for Viya-ARK
Each item that is included in the resource kit provides a document that describes its specific prerequisites and functionality.

For example, a functioning [Ansible Controller](http://docs.ansible.com/ansible/latest/intro_installation.html) is required to run  the Ansible playbooks that are included below in the [Pre-installation Playbook](playbooks/pre-install-playbook) section. A list of the available playbooks is provided.

## Index of Tools
Tool support for the latest release of SAS Viya

* [Pre-installation Playbook](playbooks/pre-install-playbook)
* [Home Directory Creator Playbook](playbooks/home-directory-createor)
* [SAS Data Server Utility Script](utilities/postgres/viya)
* [Viya Multi-Machine Services Utilities](playbooks/viya-mmsu)
* [Deployment Report Playbook](playbooks/deployment-report)

## License

This project is licensed under the [Apache 2.0 License](LICENSE).