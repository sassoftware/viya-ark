# SAS Viya LDAP Validator

## Purpose

The purpose of this playbook is to validate the accuracy of some of the LDAP properties provided in a sitedefault.yml file.
Running this playbook will try to connect to the LDAP server and fetch some of the attributes of Users and Groups. 

**Important:** The tests performed here are necessary but not exhaustive. That is, you need to at least pass all the tests in this playbook, but that is still not a full guarantee of success, since the playbook is not yet able to check every single parameter for accuracy. 

## Input:

* Inventory file
  * A sample inventory file called `ldaphelper.inventory.ini` is provided with the playbook
  * If you already know which server will host the SAS Viya Core Services, update the provided inventory accordingly, so that this server is the one running the SAS Viya LDAP Validator tests
  * If the future SAS Viya server is not yet available, you can use the default inventory as-is, in which case the tests will be executed from the Ansible Controller itself.
* Sitedefault file
  * Two sample sitedefault files are included: `sitedefault_sample_ad.yml` and `sitedefault_sample_openldap.yml`
  * You should provide your own customized sitedefault file. You can do so in 2 ways:
    * Update the line `    sitedefault_loc: ./sitedefault_sample.yml` in the `viyaldapvalidator.yml` playbook
    * At the prompt, with an ansible override: `ansible-playbook viyaldapvalidator.yml -e 'sitedefault_loc=./sitedefault.yml'`

## How to execute it

1. Go to the same directory as the playbook:

    ```bash
    cd ~
    git clone https://github.com/sassoftware/viya-ark.git
    cd viya-ark/playbooks/ldap-validator/
    ```

2. Update the Inventory and `sitedefault_loc` variable, as mentioned above.

3. Execute the playbook:

    ```bash
    cd viya-ark/playbooks/ldap-validator/
    ansible-playbook viyaldapvalidator.yml
    ```

## Checks executed

The SAS Viya LDAP Validator Playbook will try to validate access to your LDAP in the following ways:

* try to connect to the Ldap server using provided hostname and port
* fetch users[5 users] attributes
* fetch group[5 users] attributes
* fetch the attributes of admin user provided in the `sitedefault.yml` file.

## Success Criteria

If all tasks come back OK (green), it means that all the tests passed. If any test fails, an error message should indicate the reason for the failure. 

## Future improvements

This is a list of future checks that should be added to this playbook:
* verify that all provided field overrides exist in target LDAP
* confirm that SSSD or similar has been configured and that there are matching users
* support passing certificates for the connection to LDAP

Copyright (c) 2019, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
SPDX-License-Identifier: Apache-2.0

