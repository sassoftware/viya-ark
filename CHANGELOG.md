# Changelog for SAS Viya ARK

<!-- LATEST RELEASE START -->
## Viya34-ark-1.7 - August 22, 2019

- **Summary**:
    Introducing playbooks to automate tasks required prior to and after performing a SAS Viya upgrade.  Add support for Ansible 2.8.
- Issues addressed:
    - DEPENB-1813 - Ansible 2.8 support in pre-install playbook.
    - DEPENB-1687 - Create pre-upgrade and post-upgrade controller playbooks.
    - DEPENB-1857 - Inventory file hostgroup names now use underscores rather than hyphens (Ansible 2.8).
    - DEPENB-1619 - Provide playbook to assist merging deployment files.
- Ansible Support: Ansible 2.5 - Ansible 2.8

## Viya34-ark-1.6 - August 13, 2019

- **Summary**:
    Temporary workaround for issues related to updating systemd to latest (currently version 219-67)
- Issues addressed:
    - DEPENB-2009 - Do not update systemd on RHEL7 with pre-install playbook. 
- Ansible Support: Ansible 2.5 - Ansible 2.7

<!-- LATEST RELEASE END -->

## Viya34-ark-1.5 - July 11, 2019

- **Summary**: 
    Enhancements around sudo checks & storage checks.  Updates to host group naming.  Documentation changes and Fixes.
- Issues addressed: 
    - DEPENB-962 - Sudo user checks
    - DEPENB-1173 - Storage checks for /opt & /var/cache
    - DEPENB-1667 - cgconfig service enable set to yes.
    - DEPENB-1827 - Future Ansible version enhancent
    - DEPENB-1828 - Main README bad releases link removed.  Access 'releases' link on github repo landing page.
    - DEPENB-1857 - Host group name references with hyphens changed to underscores.  Future Ansible version compliance.
- Ansible Support: Ansible 2.5 - Ansible 2.7

## Viya34-ark-1.4 - June 5, 2019

- **Summary**: 
    Changes to supported Ansible versions.  Documentation changes.
- Issues addressed: 
    - DEPENB-1810 - Ansible 2.4 no longer supported.  
    - DEPENB-1708 - SUPPORT.md documentation added.
    - DEPENB-1822 - SAS Viya Deployment Assistant for Windows reference added to README.md
- Ansible Support: Ansible 2.5 - Ansible 2.7

## Viya34-ark-1.3 - May 6, 2019

- **Summary**: 
    Bug fixes.
- Issues addressed: 
    - DEPENB-1716 - Fix jq installation issues on remote hosts
- Ansible Support: Ansible 2.4 - Ansible 2.7

## Viya34-ark-1.2 - May 1, 2019

- **Summary**: 
    LDAP validator tool.  VI pre-install playbook support.  Documentation updates.  Bug fixes.
- Issues addressed: 
    - DEPENB-1686 - Unclear the master branch of SAS Viya ARK is associated with SAS Viya 3.4
    - DEPENB-876 - LDAP validator
    - DEPENB-1689 - Fix for no report when error hit gathering data.
    - DEPENB-1635 - Incorporate VI specific prereqs
    - DEPENB-1713 - Deployment Report: memory uninitialized if service down.
- Ansible Support: Ansible 2.4 - Ansible 2.7

## Viya34-ark-1.1 - April 18, 2019

- **Summary**: 
    Adding descriptions of numbering scheme and changelog.  Legacy branches replicated to this repo.  Bug fixes.
- Issues addressed: 
    - DEPENB-1270 - Addition of the files [VERSIONS](VERSIONS.md) and [CHANGELOG](CHANGELOG.md)
    - DEPENB-1633 - [README](README.md) updates.  Replicated [viya-3.2](../../viya-3.2) & [viya-3.3](../../viya-3.3) legacy branches to this repo.
    - DEPENB-1566 - Add package update available notifications to deployment report
    - DEPENB-1637 - Pre-install playbook local check rejected LOCALE en_US.
    - DEPENB-1664 - Deployment report playbook filename change and not creating report as root user.

## Viya34-ark-1.0 - April 10, 2019

- **Summary**: 
    Minor fixes, and first release using the new numbering scheme. 
- Issues addressed: 
    - DEPENB-1367 - Convert fail tasks to assert tasks for better user experience (https://github.com/sassoftware/virk/issues/57)

## v0.3 - April 10, 2019

- **Summary**:
    Simple [fix](https://github.com/sassoftware/viya-ark/commit/c44bcf824aa3307fbc20594bda76739adb46b622) for an issue that shows up when using `--check` mode
- Issues addressed: 
    - [Issue with the LOCALE verification when run in --check mode](https://github.com/sassoftware/viya-ark/issues/2)

## v0.2 - March 29, 2019

- **Summary**:
    Small improvements to the pre-requisite playbooks, addition of the Deployment Reporting tool, and multi-tenant support addition for the Viya Multi-Machine Services Utilities  
- Issues addressed:
    - DEPENB-1370 - Added locale checking to the pre-req playbook.
    - DEPENB-1551 - yum_repo check now checks for correct return value
- New Functionality/Products
    - DEPENB-842 - Deployment reporting tool playbook added.
    - DEPENB-1132 - MMSU now has multi-tenant support.

## v0.1 - March 8, 2019

- **Summary**:
    Initial code push, from older "virk" project 
- Issues addressed:
    - DEPENB-1362 - Version Check of systemd was not reflective of documentation.
    - DEPENB-1366 - CAS Resource Mgmt needed additional packages.
    - DEPENB-1373 - Remove vi / va specific pre-install playbooks.
    - DEPENB-1552 - Name of disable SELinux task was incorrect.
    - DEPENB-1557 - Maximum Number of OS Tasks changes when running pre-install playbook with --check option
    - DEPENB-1561 - Inconsistency between hostname length checking and actual hostname length.
    - DEPENB-1392 - Validate hostname meets RFC952 criteria & SAS limitations
