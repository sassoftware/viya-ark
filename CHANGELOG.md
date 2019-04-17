# Changelog for SAS Viya-ARK

<!-- LATEST RELEASE START -->
## Viya34-ark-1.1 - April 18, 2019

- **Summary**: 
    Adding descriptions of numbering scheme and changelog.  Legacy branches replicated to this repo.  Bug fixes.
- Issues addressed: 
    - DEPENB-1270 - Addition of the files [VERSIONS](VERSIONS.md) and [CHANGELOG](CHANGELOG.md)
    - DEPENB-1633 - [README](README.md) updates.  Replicated [viya-3.2](../../viya-3.2) & [viya-3.3](../../viya-3.3) legacy branches to this repo.
    - DEPENB-1566 - Add package update available notifications to deployment report
    - DEPENB-1637 - Pre-install playbook local check rejected LOCALE en_US.
    - DEPENB-1664 - Deployment report playbook filename change and not creating report as root user.

<!-- LATEST RELEASE END -->

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
