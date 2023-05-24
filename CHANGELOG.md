# Changelog for SAS Viya ARK

<!-- LATEST RELEASE START -->
## Viya35-ark-1.16 - May 24, 2023
- **Sumary**:
  Changes related to Viya 3.5 support for new range of Ansible versions and new minimum Python version.
- Ansible Support: Ansible 2.12 - Ansible 2.14    
<!-- LATEST RELEASE END -->

## Viya35-ark-1.15 - August 23, 2022
- **Sumary**:
  Changes related to Viya 3.5 support for new range of Ansible versions and new minimum Python version.  Addressed GitHub issue.
- Issues addressed:
  - SAS Viya Pre-Installation Playbook
    - VIYAARK-244 - Support Ansible 2.11 (4.0) in Viya ARK Pre-Install Playbook
    - VIYAARK-263 - Pre-Install: Update the playbook to support Ansible 2.12
    - VIYAARK-264 - Update Ansible and Python support range
    - VIYAARK-269 - Pre-Install Playbook tasks/pre.third_party_check.yml logic flawed
  - SAS Multi-Machine Service Utilties
    - VIYAARK-260 - Address GitHub issue [#86](https://github.com/sassoftware/viya-ark/issues/86)
  - SAS Viya Upgrade Tasks Playbooks
    - VIYAARK-265 - Merge playbook: Support Ansible 2.12
- Ansible Support: Ansible 2.10 - Ansible 2.12    

## Viya35-ark-1.14 - June 4, 2021
- **Sumary**:
  Enhancement of RHEL8 compatibility libraries installation.  Dropping unused feature.  README updates.
- Issues addressed:
  - SAS Viya Pre-Installation Playbook
    - VIYAARK-253 - systemd DefaultTimeout parameters not needed
    - VIYAARK-241 - Install missing RHEL8 compatibility libraries
  - SAS LDAP Validator
    - VIYAARK-185 - Address GitHub issue [#20](https://github.com/sassoftware/viya-ark/issues/20) - anonymousBind usage update
- Ansible Support: Ansible 2.8 - Ansible 2.10  

## Viya35-ark-1.13 - March 23, 2021
- **Sumary**:
  Bug fixes.
- Issues addressed:
  - SAS Multi-Machine Services Utilities
    - VIYAARK-210 - MMSU: Document enable_svs_alternative.
    - VIYAARK-214 - MMSU: Task names for Postgres start/stop need to be clarified.
  - SAS Viya Pre-Installation Playbook
    - VIYAARK-204 - Make yum cachedir path customizable.
  - SAS Viya Deployment Report
    - VIYAARK-242 - Deployment Report not reporting the status of "not ready" services.
- Ansible Support: Ansible 2.8 - Ansible 2.10

## Viya35-ark-1.12 - February 16, 2021 
- **Summary**:
  RHEL8 Support and bug fixes.
- Issues addressed:
  - SAS Multi-Machine Service Utilties
    - VIYAARK-226 - MMSU: Validate RHEL8 
  - SAS Viya Upgrade Tasks Playbooks
    - VIYAARK-227 - Validate RHEL8
    - VIYAARK-237 - Merge playbook using check_invalid_arguments which was removed in Ansible 2.10
    - VIYAARK-240 - Merge Playbook ConfigParser Python2 Python3 Compatibility ()
  - SAS Viya Pre-Installation Playbook
    - VIYAARK-218 - Fails on clientaliveinterval control even when you run the playbook with the exclude option. (GitHub Issue #69)
    - VIYAARK-224 - Validate RHEL8
    - VIYAARK-229 - Get the permissions of the directories TASK fails in checkmode
    - VIYAARK-232 - Check for RHEL8 compatibility packages
    - VIYAARK-238 - Support RHEL8 OS checks
  - SAS Viya Deployment Report
    - VIYAARK-225 - Validate RHEL8
    - VIYAARK-239 - UnicodeEncodeError: 'ascii' codec can't encode character correctly. (GitHub Issue #75)
- Ansible Support: Ansible 2.8 - Ansible 2.10


## Viya35-ark-1.11 - December 18, 2020 
- **Summary**:
  Bug fixes and a couple of enhancments.
- Issues addressed:
  - SAS Multi-Machine Service Utilties
    - VIYAARK-233 - MMSU: playbook encountered issue with starting sas-viya-spawner-default in multi-tenancy env
    - VIYAARK-234 - MMSU: provide better readable information for status in multi-tenancy env
    - VIYAARK-236 - MMSU: provide a check variable to disable pause timer when running stop playbook
  - SAS Viya Upgrade Tasks Playbooks
    - VIYAARK-41  - pre_upgrade fails if Viya 3.5 software order adds ModelServices
    - VIYAARK-222 - Archive Obsolete Log Folders Playbook Fails on Power Linux
- Ansible Support: Ansible 2.8 - Ansible 2.10


## Viya35-ark-1.10 - October 20, 2020 
- **Summary**:
  Changing range of Ansible versions supported.  Enhancing obsolete log archiving.
- Issues addressed:
  - General
    - VIYAARK-188 - Support Ansible 2.10.
    - VIYAARK-216 - Add Bug Report template to GitHub Issue submission.
  - SAS Viya Upgrade Tasks Playbooks
    - VIYAARK-104 - Produce summary report for Archive Obsolete Folders playbook.
- Ansible Support: Ansible 2.8 - Ansible 2.10


## Viya35-ark-1.9 - September 30, 2020
- **Summary**:
  Fix related to MMSU, Pre-Install & Post Upgrade.
- Issues addressed:
  - General
    - VIYAARK-212 - Remove deprecated includes from codebase. MMSU & Post Upgrade.
  - SAS Viya Pre-Installation Playbook
    - VIYAARK-209 - Clean up references to max_num_priv_ips.
  - SAS Multi-Machine Service Utilties
    - VIYAARK-103 - Add a confirmation before stopping
- Ansible Support: Ansible 2.7.2 - Ansible 2.9


## Viya35-ark-1.8 - August 31, 2020
- **Summary**:
  Fix related to Merge Playbook.
- Issues addressed:
  - SAS Viya Upgrade Tasks Playbooks
    - VIYAARK-208  - Merge Playbook: Adding a new property, PERMS_OVERRIDE, to INVOCATION_VARIABLE.
- Ansible Support: Ansible 2.7.2 - Ansible 2.9


## Viya35-ark-1.7 - July 29, 2020
- **Summary**:
  Enhancements and fixes related to Pre-Install playbook & Deployment Report.
- Issues addressed:
  - SAS Viya Pre-Installation Playbook
    - VIYAARK-56  - Multi-nic limitation checks removed.
  - SAS Viya Deployment Report
    - VIYAARK-207 - Deployment Report not working when including hotfixes.
  - General
    - VIYAARK-200 - Develop a list of data to be submitted with github issues.
    - VIYAARK-205 - Home Directory Creator tool removed from SAS Viya ARK.
- Ansible Support: Ansible 2.7.2 - Ansible 2.9


## Viya35-ark-1.6 - July 1, 2020
- **Summary**:
  Enhancements and fixes related to Pre-Install playbook, MMSU & LDAP Validator.
- Issues addressed:
  - SAS Viya Pre-Installation Playbook
    - VIYAARK-11  - SSL Certificate check and validation.
    - VIYAARK-30  - HTTP/HTTPS proxy check and validation.
    - VIYAARK-169 - Import SSL and proxy check tasks to playbook. 
  - SAS Multi-Machine Service Utilties
    - VIYAARK-201 - Update README: programming-only deployment not supported.
  - SAS LDAP Validator
    - VIYAARK-202 - Input (-b) needed for basic connection tasks to work.
- Ansible Support: Ansible 2.7.2 - Ansible 2.9

## Viya35-ark-1.5 - June 4, 2020
- **Summary**:
  Update Support statement and revise Change Log from prior release.
- Issues addressed:
  - General
    - VIYAARK-190 - Update Viya ARK support statement.
- Ansible Support: Ansible 2.7.2 - Ansible 2.9 


## Viya35-ark-1.4 - May 29, 2020
- **Summary**:
  Enhancements and fixes related to Upgrade & Multi-Machine Services Utilities.
- Issues addressed:
  - SAS Multi-Machine Service Utilties
    - VIYAARK-122 - Support using GEL script in start/stop.
    - VIYAARK-124 - Consul logging need to be redirected to stdout.
    - VIYAARK-125 - Rewording message when consul has a slow start.
    - VIYAARK-126 - Tool may not work properly for single machine deployment.
    - VIYAARK-128 - Performance improvement when rerun viya-services-stop.yml.
    - VIYAARK-129 - When running playbook stop, rabbitmq may have process left behind.
    - VIYAARK-130 - Upon failure, playbook viya-services-stop.yml should stop instead of continue.
    - VIYAARK-150 - Parameter LIST should be quoted.
    - VIYAARK-151 - User request to update task name for Data Server Consul Template.
  - SAS Viya Upgrade Tasks Playbooks
    - VIYAARK-184 - Merge playbook fails to parse ansible.cfg correctly for SAS-internal deployment. 
- Ansible Support: Ansible 2.7.2 - Ansible 2.9

## Viya35-ark-1.3 - April 1, 2020
- **Summary**:
  Enhancements and fixes related to Upgrade & Multi-Machine Services Utilities, Pre-Installation playbooks.
- Issues addressed:
  - SAS Viya Upgrade Tasks Playbooks
    - VIYAARK-121 - Pre-upgrade failure due to Ansible 2.7 incompatible function.
    - VIYAARK-105 - hostname comparison should be case insensitive
    - VIYAARK-89  - Merge Playbook should handle multi-NIC inventory/vars 
  - SAS Multi-Machine Service Utilties
    - VIYAARK-118 - Improving code for multiple CAS controllers
    - VIYAARK-113 - Support MMSU when DB node0/pgpool0 is down and DB is functional
  - SAS Viya Pre-Installation Playbook
    - VIYAARK-83  - Check that the SSH ClientAliveInterval is adequate
    - VIYAARK-5   - Catch when no permission to SAS home directory
- Ansible Support: Ansible 2.7.2 - Ansible 2.9


## Viya35-ark-1.2 - February 28, 2020
- **Summary**:
  Enhancements and fixes related to Upgrade, Multi-Machine Services Utilities, Deployment Report, Pre-Installation playbooks and documentation.
- Issues addressed:
  - General
    - VIYAARK-87 - Validation of Python3 support across the applicable tools.
    - VIYAARK-63 - Improve speed of playbook when skipping hyphenated hostname [sas-all] fix
    - VIYAARK-29 - Validation of Linux on Power hosting environment across the tools. (See main README for info on Linux on Power support in SAS Viya 3.5)
  - SAS Viya Upgrade Tasks Playbooks
    - VIYAARK-44 - Archive Obsolete Folders playbook: Addresses the large number of outdated service directories in the logs location for upgrade customers
    - VIYAARK-65 - Improve merge playbook inventory and INVOCATION_VARIABLES when new hostgroups exist
    - VIYAARK-60 - Improve handling of return codes from actions of Pre-Upgrade playbook
    - VIYAARK-42 - Pre-Upgrade playbook disk space check needs to handle no /opt/sas path without failure
  - SAS Multi-Machine Service Utilties 
    - VIYAARK-55 - viya-services-stop.yml message output typo
    - VIYAARK-40 - Honor svc-ignore entries
    - VIYAARK-62 - Provide a reliable startup script for distributed Viya with automatic Consul cleanup
  - SAS Viya Deployment Report
    - VIYAARK-38 - Improve Hotfix deployment report to only show applicable hotfixes per release
    - VIYAARK-86 - deployment-report playbook fails when remote host is using Python 3.x
    - VIYAARK-49 - jQuery XSS vulnerability - moving from v3.3.1 to v3.4.1
    - VIYAARK-88 - Error thrown when run against an incomplete deployment
  - SAS Viya Pre-Installation Playbook
    - VIYAARK-27 - Correct package selection in Linux on Power hosting environment.
    - VIYAARK-14 - Suppress RHEL package version check for Linux on Power RHEL hosting environment.
    - VIYAARK-9  - Playbook tasks using Linux shell command incorrect recap showing Changed > 0 after multiple re-runs of playbook.
- Ansible Support: Ansible 2.7.2 - Ansible 2.9


## Viya35-ark-1.1 - December 19, 2019

- **Summary**:
  Enhancements and fixes related to Upgrade, Deployment Report, Pre-Installation playbooks and documentation.
- Issues addressed:
  - General
    - VIYAARK-64 - Known Issues section added to main README
  - SAS Viya Upgrade Tasks Playbooks
    - VIYAARK-45 - DEFAULT_BACKUP_SCHEDULE job not recreated after upgrade from SAS Viya 3.3 to SAS Viya 3.4/3.5
    - VIYAARK-41 - Pre-Upgrade playbook fails if SAS Viya 3.5 software order adds [ModelServer]
  - SAS Viya Deployment Report
    - VIYAARK-46 - Temporarily disable hotfix report for earlier release
  - SAS Viya Pre-Installation Playbook
    - VIYAARK-43 - Remove libXp.i686 from required software packages
    - VIYAARK-25 - Non-supported Java version check done in normal mode as well as check mode
    - VIYAARK-50 - Kernel semaphore performance configuration task not adjusting settings as expected (Python 2) and failing playbook (Python 3)


## Viya35-ark-1.0 - November 19, 2019

- **Summary**:
    This release of SAS Viya ARK is coincidental to the release of SAS Viya 3.5.
- Issues addressed:
    - DEPENB-1174 - Upgrade Tasks added a playbook to move audit records from SAS Viya 3.3 CAS host to SAS 3.4 Operations host.
    - DEPENB-1531 - Pre-Installation playbook should check if the short hostname is pingable.
    - DEPENB-1578 - Pre-Installation playbook should only update kernel semaphores if they are larger than the current values.
    - DEPENB-1600 - Pre-Installation playbook README updated to reference provided inventory file.
    - DEPENB-1649 - Pre-Installation playbook needs to check for presence of bash shell.
    - DEPENB-1666 - Pre-Installation playbook should check FQDN for hostname length check.
    - DEPENB-1748 - Add hotfix reporting to SAS Viya Deployment Report.
    - DEPENB-1836 - Multi-Machine Services Utilities should display the URLs with https instead of http.
    - DEPENB-1982 - Upgrade Tasks added a playbook to delete mmLibs caslib.
    - DEPENB-2027 - Warn Customers of non-supported Java version
    - DEPENB-2036 - Upgrade Tasks fixed format of default user paths.
    - DEPENB-2054 - Support Ansible 2.9
    - DEPENB-2105 - Pre-Installation playbook needs to support SELinux in "enforced" mode
    - DEPENB-2108 - Upgrade Tasks failed searching for NODE_TYPE which is no longer in vars.yml
    - DEPENB-2110 - LDAP Validator update sitedefault_sample_ad.ym to be consistent with sitedefault_sample_openldap.yml
    - DEPENB-2113 - Remove jq installation from Viya ARK pre-install playbook
    - DEPENB-2120 - Multi-Machine Services Utilities support for postgress 11
    - DEPENB-2137 - viya-upgrade needs to be updated for Viya 3.5 references
    - DEPENB-2171 - Pre-Installation playbook should check for Ansible patch version
    - DEPENB-2182 - merge-playbook fails to handle dir path
    - DEPENB-2183 - Erroneous failure reported for Visual Investigator 3.3 -> 3.5 UIP
    - DEPENB-2189 - Utility sds_micro_service_pg_connection_test.sh script should no longer be used.  README update
    - DEPENB-2192 - Clarify message in pre-upgrade summary for skipping mmlibs step on SUSE
    - DEPENB-2115 - LDAP Validator not reflected in Index of Tools in Viya ARK root README.
    - DEPENB-2200 - Need to check for required curl and nss versions in repo
    - DEPENBDAT-627 - Ansible 2.9 support for viya-upgrade related playbook.
- Ansible Support: Ansible 2.7.2 - Ansible 2.9

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
