#!/usr/bin/python

####################################################################
# ### process_sas_host_details.py                                ###
####################################################################
# ### Author: SAS Institute Inc.                                 ###
####################################################################
#
# Copyright (c) 2019-2020, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
from ansible.module_utils.basic import AnsibleModule
import ast
import traceback
import xml.etree.ElementTree as ET
# Python 2
try:
    import urllib2 as web_request
    import urllib2 as web_error
# Python 3
except ImportError:
    import urllib.request as web_request
    import urllib.error   as web_error

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['release'],
    'supported_by': 'SAS'
}

DOCUMENTATION = '''
---
module: process_sas_host_details

short_description: Processes and formats collected SAS host details and generates hotfix report.

description: >
    Collects all SAS host details returned by get_sas_host_details and processes the data before creating the
    sas_deployment_details.yml and sas_deployment_details.html files.

options:
    hostvars:
        description:
            - The hostvars information for all hosts in the deployment.
        required: true
    report_timestamp:
        description:
            - The timestamp captured at the beginning of the report creation.
        required: true
    registered_dict_name:
        description:
            - The name of the dict object registered with hostvars which will contain the host details.
        required: true
    include_hotfix_report:
        description:
            - Whether or not to include the hotfix report.
        required:  false
        default:   true
    hotfix_url:
        description:
            -  The URL to look for the published hotfixes.
        require:  False
        default:  http://ftp.sas.com/techsup/download/hotfix/HF2/util01/Viya/data/
'''

EXAMPLES = '''
# Process SAS deployment information
- name: Process SAS deployment
  process_sas_host_details:
    hostvars: "{{ hostvars }}"
    report_timestamp: "{{ report_timestamp }}"
'''

RETURN = '''
sas_deployment_details:
    description: An aggregated and processed summary of all host details in the deployment.
    type: dict
'''

#Print the full hot fix dictionary.  Generally, this will only be for debugging purposes.
def print_Full_Report( fullReport):
    for currennt_hotfix in fullReport:
        print("  " + currennt_hotfix)
        print("    * Release Date : " + fullReport[currennt_hotfix]["release_date"])
        print("    * Installed    : %s " % fullReport[currennt_hotfix]["installed"])
        print("    * Up To Date   : %s " % fullReport[currennt_hotfix]["upToDate"])

        print("    * SAS Notes:")
        if "sasnote" in fullReport[currennt_hotfix]:
            for current_sasnote in fullReport[currennt_hotfix]["sasnote"]:
                print("      - " + current_sasnote + " : " + fullReport[currennt_hotfix]["sasnote"][current_sasnote])
        print("    * Packages:")
        if "package" in fullReport[currennt_hotfix]:
            for current_package in fullReport[currennt_hotfix]["package"]:
                print("      - " + current_package + ":")
                for current_platform in fullReport[currennt_hotfix]["package"][current_package]["platform"]:
                    print("        + " + current_platform + ":")
                    print("          Version:    " + fullReport[currennt_hotfix]["package"][current_package]["platform"][current_platform]["version"])
                    print("          Up To Date: %s" % fullReport[currennt_hotfix]["package"][current_package]["platform"][current_platform]["upToDate"])
                    print("          Installed: %s" % fullReport[currennt_hotfix]["package"][current_package]["platform"][current_platform]["installed"])
                    print("          OS :  " + fullReport[currennt_hotfix]["package"][current_package]["platform"][current_platform]["os"])
                    if "arch" in fullReport[currennt_hotfix]["package"][current_package]["platform"][current_platform]:
                        print("          arch:       " + fullReport[currennt_hotfix]["package"][current_package]["platform"][current_platform]["arch"])
                    print("        - Currently Installed Version Comparisons:")
                    for currentHost in fullReport[currennt_hotfix]["package"][current_package]["platform"][current_platform]["installedVersions"]:
                        print("            " + currentHost + " (host) @ " + \
                              fullReport[currennt_hotfix]["package"][current_package]["platform"][current_platform]["installedVersions"][currentHost][
                                  0] + " (%s) " % \
                              fullReport[currennt_hotfix]["package"][current_package]["platform"][current_platform]["installedVersions"][currentHost][1])

###########################################
#  compare_versions
#
# This function takes in two string formatted like so:
#   d.d.d[....]-dddddd
#
# Note:  The first string passed in will be the string that
# the playbook has passed in.  So, that will also contain
# OS specfic information.  It will be stripped out
# from splitdash1[1] below.
#
# The last string that is passed is whether or not to
# compare the time-date stamps.
#
# Here are the return values:
#   -1 the first string is lower than the second string
#    0 the first and second strings match exactly.
#    1 the first string is higher than the second string.
###############################################
def compare_versions (version1, version2, honorTimeStamp=True):
    return_code = 0

    splitdash1 = version1.split('-')
    splitdash2 = version2.split('-')
    splitdot1 = splitdash1[0].split('.')
    splitdot2 = splitdash2[0].split('.')
    length1 = len(splitdot1)
    length2 = len(splitdot2)

    for index in range (length1):
        if (index+1) > length2:
            return_code = 1
            break
        if int(splitdot1[index]) > int(splitdot2[index]):
            return_code = 1
            break
        if int(splitdot1[index]) < int(splitdot2[index]):
            return_code = -1
            break

    if return_code == 0 and honorTimeStamp:
        if length2 > length1:
            return_code= -1
        else:
            splitdate1 = splitdash1[1].split('.')
            splitdate2 = splitdash2[1].split('.')
            if int(splitdate1[0]) > int(splitdate2[0]):
                return_code = 1
            else:
                if int(splitdate1[0]) < int(splitdate2[0]):
                    return_code = -1
                else:
                    if int(splitdate1[1]) > int(splitdate2[1]):
                        return_code = 1
                    else:
                        if int(splitdate1[1]) < int(splitdate2[1]):
                            return_code = -1
    return return_code


# =====
# main() (Entry point for Ansible module execution)
# =====
def main():
    """
    Entry method for Ansible module.
    :return: JSON formatted representation of the SAS deployment across all hosts.
    """

    # the AnsibleModule object will be our abstraction for working with Ansible.
    # This includes instantiation, a couple of common attr that will be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=dict(
            hostvars=dict(type='raw', required=True),
            report_timestamp=dict(type=str, required=False, default=''),
            registered_dict_name=dict(type=str, required=False, default="get_sas_host_details_results"),
            include_hotfix_report=dict(type=bool, required=False, default=True),
            hotfix_url = dict(type=str, required=True)
    ),
        supports_check_mode=True
    )

    # get module parameters
    hostvars = module.params['hostvars']
    report_timestamp = module.params['report_timestamp']
    registered_dict_name = module.params['registered_dict_name']
    include_hotfix_report = module.params['include_hotfix_report']
    hotfix_url = module.params['hotfix_url']

    # Starting in Ansible 2.8.1, there is the potential for hostvars
    # to be passed as a byte string, if the dict is too large
    # This will convert the str back to a dict before proceeding
    if isinstance(hostvars, str):
        hostvars = ast.literal_eval(hostvars.decode())

    results = dict()
    results['sas_hosts'] = dict()
    results['created'] = report_timestamp

    for inventory_hostname, host_vars in hostvars.items():

        # set up returnable values
        unreachable = True
        failed = True
        failure_details = dict(
            msg="",
            rc=0,
            stderr="",
            stdout="",
        )

        # get the host details dict
        host_details = host_vars.get(registered_dict_name)

        # check if the host has the registered dict
        if host_details is not None:

            # host details exist, so host was reachable
            unreachable = False

            # check if the host failed
            failed = host_details['failed']

            # if the module reported a failure, collect details
            if failed:
                failure_details['msg'] = host_details['msg']
                failure_details['rc'] = host_details['rc']
                failure_details['stderr'] = host_details['module_stderr']
                failure_details['stdout'] = host_details['module_stdout']
            else:
                # get module results
                host_results = host_details.get('sas_host_details')

                if host_results is not None:
                    results['sas_hosts'].update(host_results)
                else:
                    failed = True

        # if the results dict could not be found, mark the host as unreachable
        if failed or unreachable:
            host_groups = host_vars.get('group_names')

            if host_groups is not None and 'sas_all' in host_groups:
                hostname = host_vars.get('ansible_fqdn')
                if hostname is None or hostname == "":
                    hostname = host_vars.get('ansible_hostname')
                    if hostname is None or hostname == "":
                        hostname = host_vars.get('ansible_host')
                        if hostname is None or hostname == "":
                            hostname = host_vars.get('inventory_hostname')
                            if hostname is None or hostname == "":
                                hostname = inventory_hostname

                try:
                    host_groups.remove('sas_all')
                    host_groups.remove('sas-all')
                except ValueError:
                    pass  # do nothing

                results['sas_hosts'][hostname] = dict(
                    _id=hostname.replace('.', '-'),
                    _unreachable=unreachable,
                    _failed=failed,
                    _failure_details=failure_details,
                    ansible_host_groups=host_groups
                )
            else:
                pass  # this host isn't in sas_all so there's no need to try and report on it

    ##################################################################################
    # This section will find all of the hotfixes available and add them to the report.
    ##################################################################################
    #
    # There are a few data structures that are complicated enough to warrant a description:
    # fullReport
    #  This will hold all of the data in a format condusive to printing it out in the final report.  This is how
    #  It is structured:
    #  fullReport (dict):
    #  key=Hot Fix Name, point to another dict:
    #    key="released", points to a string containing the release date of the hotfix.
    #      key= "installed", points to a boolean that will reflect whether any of the packages used by this hotfix are installed on any of the machines in the deployment.
    #      key="upToDate", point to a boolean that will reflest whether ALL of the packages used by this hotfix are up to date on ALL of the machines in the deployment.
    #      key="sasnote", points to another dict:
    #        key=SASNote number, points to the description of the SASNote.
    #      key="package", points to another dict:
    #        key="platform" , points to another dict:
    #          key=OS, points to another dict:
    #            key="version", points to the string of the version of the package.
    #            key="installed", points to a boolean which reflects whether this package is installed on any machine in the deployment.
    #            key="upToDate", points to a boolean which reflects whether this package is up to data on ALL of the machines in the deployment.
    #            key="os", points to the fully qualified name of the operating system.
    #            key="arch", points to the architecture of the OS (NOTE:  This does not exist on Windows systems.)
    #            key="alreadyUpdated", points to a boolean, which is used to keep track of whether the upToDate has already been set.
    #            key="installedVersions", points to another dict:
    #              key=machineName, points to a 2 element list:
    #                [0]=string containing package version that is currently installed.
    #                [1]=boolean reflecting whether this version is at or above the package delevered in this hotfix.
    #
    ###########################################################################
    #
    #  packageToHotFix
    #  This will hold a dict of lists:
    #  key:  package name, pointing to a 2 element list:
    #    [0] OS
    #    [1] The Hotfix that this package is associated with.
    #
    ###########################################################################
    #
    #  environmentReportDict
    #  This is inherited from the environment report, but it's probably worth documenting what it looks like.
    #  There is a lot of data inerherited, and I'm only describing what is used in this script.
    #  environmentReportDict
    #  key=hostname (for each machine in the deployment), pointing to another dict:
    #    key="OS", pointing to string for the OS family.
    #    key="arch", pointing to the string for the architecture of the host.
    #    key="sas_packages", pointing to another dict:
    #      key=package number, pointing to another dict:
    #        key="attributes", pointing to another dict:
    #          key="version", pointing to a string of the package versions currently installed on the host.
    ############################################################################


    # These properties will determine whether sections in the ansible output should be displayed or not.
    results["legacy_products_found"] = False
    results["hotfix_legacy_products"] = "There is no hotfix data available for the following products due to their age:\n"
    results["no_hotfixes_available"] = False
    results["no_hotfix_products"] = "The following products are installed, but there are no associated hotfixes for them:\n"

    results["include_hotfix_report"] = include_hotfix_report
    files_to_scan = []
    if include_hotfix_report:

        # Constants for the RPMs.
        VA_RPM='sas-sasvisualanalytics'
        ESM_RPM='sas-esm-service'
        ESP_RPM='sas-espcondb'
        IIM_RPM='sas-svi-intelligence-management'
        VI_RPM='sas-svi-visual-investigator'
        SPRE_RPM='sas-basecfg1'

        # The following list contains the RPMs that are unique to each of the product sets defined
        # in the default baseURL
        key_rpms = [VA_RPM,
                    ESM_RPM,
                    ESP_RPM,
                    IIM_RPM,
                    VI_RPM
                    ]
        # This is a list of the files on the hotfix website to use, depending on what is currently installed.
        # This is a dictionary of all rpms to their versions, across all machines in the deployment.
        all_installed_rpms = {}

        # Walk through all of the machines in the deployment.  Build the list of RPM -> Version.
        # If there is more than one copy of an RPM (expected on multi-machine deployments) and
        # there is a difference in version (which there should NOT be, though it is possible),
        # use the lowest version possible.
        for current_machine in results['sas_hosts']:
            if not results['sas_hosts'][current_machine]["_unreachable"] and not results['sas_hosts'][current_machine][
               "_failed"] and results['sas_hosts'][current_machine]['_sas_installed']:
                for current_rpm in results['sas_hosts'][current_machine]['sas_packages']:
                    # Skip any "noarch" packages, as they are not needed.
                    if results['sas_hosts'][current_machine]['sas_packages'][current_rpm]['attributes']['arch'].find('noarch') == -1:
                        current_rpm_version = \
                        results['sas_hosts'][current_machine]['sas_packages'][current_rpm]['attributes']['version']
                        if current_rpm in all_installed_rpms.keys():
                            if compare_versions(all_installed_rpms[current_rpm], current_rpm_version) < 0:
                                all_installed_rpms[current_rpm] = current_rpm_version
                        else:
                            all_installed_rpms[current_rpm] = current_rpm_version

        # Loop through the key RPM list.  If a key RPM exists, check the version and then add it to the list to be checked.
        for current_rpm in key_rpms:
            if current_rpm in all_installed_rpms.keys():
                rpm_version = all_installed_rpms[current_rpm]
                if current_rpm == VA_RPM:
                    # Viya 3.5 shipped with sas-visualanalytics at version 2.5.10.  If the version is at or above this,
                    # use the VA 3.5 hotfix file.
                    if compare_versions(rpm_version, "2.5.10", False) >= 0:
                        files_to_scan.append("Viya_3_5_lax_home.xml")
                    # Viya 3.4 (19w34) shipped with sas-visualanalytics at version 1.9.543.  If the version is at or
                    # above this, use the VA 3.4 hotfix file.
                    elif compare_versions(rpm_version, "1.9.543", False) >= 0:
                        files_to_scan.append("Viya_3_4_lax_0819_home.xml")
                    # Viya 3.4 (18w30) shipped at version 1.4.244.  However, there was a refresh at 19w21, but VA was not
                    # refreshed.  So, an additional check will need to be made to see if we are before or after  the
                    # 19w21 refresh.
                    elif (compare_versions(rpm_version, "1.4.244", False) >= 0):
                        # basecfg1 was updated at 19w21.  So, that is what will be looked at to see if the deployment is
                        # at least 19w21.
                        basecfg1_version = all_installed_rpms[SPRE_RPM]
                        if compare_versions(basecfg1_version, "3.19", False) >= 0:
                            files_to_scan.append("Viya_3_4_lax_0519_home.xml")
                        else:
                            files_to_scan.append("Viya_3_4_lax_home.xml")
                    # Viya 3.3 shipped with sas-visualanalytics at version 1.2.557.  If the version is at or
                    # above this, use the VA 3.3 hotfix file.
                    elif (compare_versions(rpm_version, "1.2.557", False) >= 0):
                        files_to_scan.append("Viya_3_3_home.xml")
                    # Viya 3.2 shipped with sas-visualanalytics at version 1.2.557.  If the version is at or
                    # above this, use the VA 3.3 hotfix file.
                    elif (compare_versions(rpm_version, "1.0.328", False) >= 0):
                        files_to_scan.append("Viya_3_2_home.xml")
                    # Otherwise, the version is too old.  Just note that this DU, though deployed, is too old and it
                    # won't be reported on.
                    else:
                        results["legacy_products_found"] = True
                        results["hotfix_legacy_products"] = results["hotfix_legacy_products"] + "  " + current_rpm + \
                                                            " is at version " + str(rpm_version) + \
                                                            ", but the minimum reported version is 1.0.328.\n"
                elif current_rpm == ESM_RPM:
                    # ESM 6.2 shipped with sas-esm-service at version 6.2.7.  If the version is at or above this,
                    # use the ESM 6.2 hotfix file.
                    if compare_versions(rpm_version, "6.2.7", False) >= 0:
                        files_to_scan.append('Viya_ESM_6_2_home.xml')
                    # ESM 6.1 shipped with sas-esm-service at version 6.1.76.  If the version is at or above this,
                    # use the ESM 6.1 hotfix file.
                    elif compare_versions(rpm_version, "6.1.76", False) >= 0:
                        files_to_scan.append('Viya_ESM_6_1_home.xml')
                    # ESM 5.2 shipped with sas-esm-service at version 5.2.40.  If the version is at or above this,
                    # use the ESM 5.2 hotfix file.
                    elif compare_versions(rpm_version, "5.2.40", False) >= 0:
                        files_to_scan.append('Viya_ESM_5_2_home.xml')
                    # ESM 5.1 shipped with sas-esm-service at version 5.1.13.  If the version is at or above this,
                    # use the ESM 5.1 hotfix file.
                    elif compare_versions(rpm_version, "5.1.13", False) >= 0 :
                        files_to_scan.append('Viya_ESM_5_1_home.xml')
                    # ESM 4.3 shipped with sas-esm-service at version 4.3.20.  If the version is at or above this,
                    # use the ESM 4.3 hotfix file.
                    elif compare_versions(rpm_version, "4.3.20", False) >= 0:
                        files_to_scan.append('Viya_ESM_4_3_home.xml')
                    # Otherwise, the version is too old.  Just note that this DU, though deployed, is too old and it
                    # won't be reported on.
                    else:
                        results["legacy_products_found"] = True
                        results["hotfix_legacy_products"] = results["hotfix_legacy_products"] + "  " + current_rpm + \
                                                            " is at version " + str(rpm_version) + \
                                                            ", but the minimum reported version is 6.1.76.\n"
                elif current_rpm == ESP_RPM:
                    # ESP 6.2 shipped with sas-espcondb at version 6.2.0.  If the version is at or above this,
                    # use the ESP 6.2 hotfix file.
                    if compare_versions(rpm_version, "6.2.0", False) >= 0:
                        files_to_scan.append("Viya_ESP_6_2_home.xml")
                    # ESP 6.1 shipped with sas-espcondb at version 6.1.0.  If the version is at or above this,
                    # use the ESP 6.1 hotfix file.
                    elif compare_versions(rpm_version, "6.1.0", False) >= 0:
                        files_to_scan.append("Viya_ESP_6_1_home.xml")
                    # ESP 5.2 shipped with sas-espcondb at version 5.2.0.  If the version is at or above this,
                    # use the ESP 5.2 hotfix file.
                    elif compare_versions(rpm_version, "5.2.0", False) >= 0:
                        files_to_scan.append("Viya_ESP_5_2_home.xml")
                    # ESP 5.1 shipped with sas-espcondb at version 5.1.0.  If the version is at or above this,
                    # use the ESP 5.1 hotfix file.
                    elif compare_versions(rpm_version, "5.1.0", False) >= 0:
                        files_to_scan.append("Viya_ESP_5_1_home.xml")
                    # ESP 4.3 shipped with sas-espcondb at version 4.3.0.  If the version is at or above this,
                    # use the ESP 4.3 hotfix file.
                    elif compare_versions(rpm_version, "4.3.0", False) >= 0:
                        files_to_scan.append("Viya_ESP_4_3_home.xml")
                    # Otherwise, the version is too old.  Just note that this DU, though deployed, is too old and it
                    # won't be reported on.
                    else:
                        results["legacy_products_found"] = True
                        results["hotfix_legacy_products"] = results["hotfix_legacy_products"] + "  " + current_rpm + \
                                                            " is at version " + str(rpm_version) + \
                                                            ", but the minimum reported version is 4.3.0.\n"
                elif current_rpm == IIM_RPM:
                    # IIM 1.5 shipped with sas-svi-intelligence-management at version 1.5.11.  If the version is at or
                    # above this, use the IIM 1.5 hotfix file.
                    if compare_versions(rpm_version, "1.5.11", False) >= 0:
                        files_to_scan.append("Viya_IIM_1_5_home.xml")
                    # IIM 1.4 shipped with sas-svi-intelligence-management at version 1.4.7.  If the version is at or
                    # above this, use the IIM 1.4 hotfix file.
                    elif compare_versions(rpm_version, "1.4.7", False) >= 0:
                        files_to_scan.append("Viya_IIM_1_4_home.xml")
                    # IIM 1.3 shipped with sas-svi-intelligence-management at version 1.3.10.  If the version is at or
                    # above this, use the IIM 1.3 hotfix file.
                    elif compare_versions(rpm_version, "1.3.10", False) >= 0:
                        files_to_scan.append('Viya_IIM_1_3_home.xml')
                    # Otherwise, the version is too old.  Just note that this DU, though deployed, is too old and it
                    # won't be reported on.
                    else:
                        results["legacy_products_found"] = True
                        results["hotfix_legacy_products"] = results["hotfix_legacy_products"] + "  " + current_rpm + \
                                                            " is at version " + str(rpm_version) + \
                                                            ", but the minimum reported version is 1.3.10.\n"
                elif current_rpm == VI_RPM:
                    # VI 10.6 shipped with sas-svi-visual-investigator at version 8.2.72.  If the version is at or
                    # above this, use the VI 10.6 hotfix file.
                    if compare_versions(rpm_version, "8.2.72", False) >= 0:
                        files_to_scan.append("Viya_VI_10_6_home.xml")
                    # VI 10.5.1 shipped with sas-svi-visual-investigator at version 7.5.129.  If the version is at or
                    # above this, use the VI 10.5.1 hotfix file.
                    elif compare_versions(rpm_version, "7.5.129", False) >= 0:
                        files_to_scan.append("Viya_VI_10_5_1_home.xml")
                    # VI 10.5 shipped with sas-svi-visual-investigator at version 7.4.22.  If the version is at or
                    # above this, use the VI 10.5 hotfix file.
                    elif compare_versions(rpm_version, "7.4.22", False) >= 0:
                        files_to_scan.append("Viya_VI_10_5_home.xml")
                    # VI 10.4 shipped with sas-svi-visual-investigator at version 7.1.51.  If the version is at or
                    # above this, use the VI 10.4 hotfix file.
                    elif compare_versions(rpm_version, "7.1.51", False) >= 0:
                        files_to_scan.append("Viya_VI_10_4_home.xml")
                    # VI 10.3.1 shipped with sas-svi-visual-investigator at version 6.4.6.  If the version is at or
                    # above this, use the VI 10.3.1 hotfix file.
                    elif compare_versions(rpm_version, "6.4.6", False) >= 0:
                        files_to_scan.append("Viya_VI_10_3_1_home.xml")
                    # VI 10.3 shipped with sas-svi-visual-investigator at version 6.3.2.  If the version is at or
                    # above this, use the VI 10.3 hotfix file.
                    elif compare_versions(rpm_version, "6.3.2", False) >= 0:
                        files_to_scan.append("Viya_VI_10_3_home.xml")
                    # Otherwise, the version is too old.  Just note that this DU, though deployed, is too old and it
                    # won't be reported on.
                    else:
                        results["legacy_products_found"] = True
                        results["hotfix_legacy_products"] = results["hotfix_legacy_products"] + "  " + current_rpm + \
                                                            " is at version " + str(rpm_version) + \
                                                            ", but the minimum reported version is 6.3.2.\n"

        # This is the URL base from which to pull the hotfix files.
        # Because the user can specify hotfix_url, we need to check to see if the trailing slash is there.  If not,
        # add it.
        if hotfix_url[-1:] == '/':
            baseURL = hotfix_url
        else:
            baseURL = hotfix_url + '/'
        # This is the top level object to store the hotfix report information (see above).
        fullReport = {}
        # This is a dict of package to hotfixes (see above).
        packageToHotfix = {}
        # This boolean will help with debugging.
        debug = False

        # Check to see if the base site can be reached.  If not, an error will be displayed in the deployment report
        # itself.  Note:  We don't actually care about the content.  This check is just to see if the page can be
        # reached.
        results["master_website"] = baseURL
        try:
            landing_page = web_request.urlopen(baseURL)
            http_output = landing_page.read()
            results["contact_hotfix_website"] = True
        except web_error.URLError :
            results["contact_hotfix_website"] = False
            if debug:
                print("***** Error parsing " + baseURL)
                print(traceback.format_exc())
                print("***** No hot fix information obtained.  Skipping hot fix report.\n\n")

        files_to_remove = []
        if len(files_to_scan) > 0:
            for currentFile in files_to_scan:
                fileToParse = baseURL + currentFile
                # Retrieve each file.
                # Inside of each file, the lines are keyed by the hot fix id.  There are three types of lines, in order:
                # 1) id and release date
                # 2) id, sasnote, sasnotetitle
                # 3) id, OS, package.
                # This script loops through to build a dictionary of dictonaries with the basic structure:
                #  ID
                #    Release Date
                #    SASNotes
                #      SASNote and Title
                #      ...
                #    Packages
                #      Package Name, Version, and OS
                try:
                    currentFileXML = web_request.urlopen(fileToParse)
                    currentFileRoot = ET.fromstring(currentFileXML.read())
                    updateID = ""
                    for update_tag in currentFileRoot.findall('update'):
                        currentUpdate = update_tag.get('id')
                        releaseDate = update_tag.get('released')
                        # To get the top level Dictionary seeded with the hot fix Name and release date.
                        if releaseDate is not None:
                            if currentUpdate in fullReport:
                                if debug:
                                    print("WARNING!  Hot Fix " + currentUpdate + " already discovered.  Skipping")
                                updateID = "DUPLICATE-SKIP"
                            else:
                                # The SCXXXX hot fixes are special.  The package files are only included in
                                # Viya_<version>_<platform>_home.xml  files.  So, the entries in the
                                # scheduled_update_<platform>_<shipevent>.xml files  can be skipped.
                                if currentUpdate.startswith("SC") and currentFile.find("scheduled_update_") < 0:
                                    continue
                                updateID = currentUpdate
                                fullReport[updateID] = {}
                                fullReport[updateID]["release_date"] = releaseDate
                                fullReport[updateID]["installed"] = False
                                fullReport[updateID]["upToDate"] = False
                        # To get the SASNote information under the hot fix
                        else:
                            if updateID == "DUPLICATE-SKIP":
                                continue
                            sasNote = update_tag.get('sasnote')
                            sasNoteTitle = update_tag.get('sasnoteTitle')
                            if sasNote is not None:
                                if "sasnote" not in fullReport[updateID]:
                                    fullReport[updateID]["sasnote"] = {}
                                # This string needs to be encoded because some non-ASCII characters are
                                # in some of the titles.
                                fullReport[updateID]["sasnote"][sasNote] = sasNoteTitle.encode('utf-8')
                            # To get the Package information under the hot fix.
                            else:
                                os = update_tag.get("os")
                                fullPackage = update_tag.get("package")
                                if fullPackage is not None:
                                    if "package" not in fullReport[updateID]:
                                        fullReport[updateID]["package"] = {}

                                    lastPeriodIndex = fullPackage.rfind(".")
                                    # Format the package information.
                                    # Windows does not have a dash in the version; Linux does.  So, we need to break differently,
                                    # depending on the OS.
                                    if os.lower().find("windows") >= 0:
                                        versionStartIndex = fullPackage.rfind("-")
                                        achitectureStartIndex = -1
                                        versionEndIndex = lastPeriodIndex
                                        osFamily = "Windows"
                                    else:
                                        versionStartIndex = fullPackage.rfind("-", 0, fullPackage.rfind("-"))
                                        # Linux has architecture in the package.  This will be stored in its own key.
                                        achitectureStartIndex = fullPackage.rfind(".", 0, lastPeriodIndex)
                                        # SLES has the string 'suse' in its package.  This will strip it out (as well as an extra .).
                                        if os.lower().find("suse") >= 0:
                                            versionEndIndex = achitectureStartIndex - 5
                                            osFamily = "Suse"
                                        else:
                                            if os.lower().find("yocto") >= 0:
                                                versionEndIndex = achitectureStartIndex - 6
                                                osFamily = "Yocto"
                                            else:
                                                if os.lower().find("ubuntu") >= 0:
                                                    versionStartIndex = fullPackage.rfind("_", 0, fullPackage.rfind("_"))
                                                    versionEndIndex = fullPackage.rfind("_")
                                                    achitectureStartIndex = versionEndIndex
                                                    osFamily = "Ubuntu"
                                                else:
                                                    if os.lower().find("red hat enterprise linux 7") >= 0:
                                                        versionStartIndex = versionStartIndex = fullPackage.rfind(":")
                                                        versionEndIndex = len(fullPackage)
                                                        achitectureStartIndex = -1
                                                        osFamily = "RedHat"
                                                    else:
                                                        versionEndIndex = achitectureStartIndex
                                                        osFamily = "RedHat"
                                    package = fullPackage[:versionStartIndex]
                                    packageVersion = fullPackage[versionStartIndex + 1:versionEndIndex]
                                    architecture = fullPackage[achitectureStartIndex + 1:lastPeriodIndex]

                                    if package not in fullReport[updateID]["package"]:
                                        fullReport[updateID]["package"][package] = {}
                                    if "platform" not in fullReport[updateID]["package"][package]:
                                        fullReport[updateID]["package"][package]["platform"] = {}
                                    if osFamily not in fullReport[updateID]["package"][package]["platform"]:
                                        fullReport[updateID]["package"][package]["platform"][osFamily] = {}
                                    fullReport[updateID]["package"][package]["platform"][osFamily]["version"] = packageVersion
                                    fullReport[updateID]["package"][package]["platform"][osFamily]["installed"] = False
                                    fullReport[updateID]["package"][package]["platform"][osFamily]["upToDate"] = False
                                    fullReport[updateID]["package"][package]["platform"][osFamily]["os"] = os
                                    fullReport[updateID]["package"][package]["platform"][osFamily]["installedVersions"] = {}
                                    if achitectureStartIndex != -1:
                                        fullReport[updateID]["package"][package]["platform"][osFamily]["arch"] = architecture
                                    # This property is used to make sure that when evaluating the installed packages,
                                    # the upToDate=false does not get overridden by a True at the end.
                                    fullReport[updateID]["package"][package]["platform"][osFamily]["alreadyUpdated"] = False

                                    # Add to the package to hot fix dict.
                                    if package not in packageToHotfix:
                                        packageToHotfix[package] = []
                                    packageToHotfix[package].append([osFamily, updateID])

                except ET.ParseError:
                    if debug:
                        print("***** Error parsing " + fileToParse)
                        print(traceback.format_exc())
                        print("***** Skipping file.\n\n")
                except web_error.HTTPError:
                    results["no_hotfixes_available"] = True
                    results["no_hotfix_products"] = results["no_hotfix_products"] + "  " + currentFile + "\n"
                    files_to_remove.append(currentFile)
                    if debug:
                        print("***** Cannot access " + fileToParse)
                        print(traceback.format_exc())
                        print("***** Skipping the file.\n\n")
                except:
                    if debug:
                        print("***** Error encountered with " + fileToParse)
                        print(traceback.format_exc())
                        print("***** Skipping the file.\n\n")

            # Remove files that have been flagged as not existing
            for this_file in files_to_remove:
                files_to_scan.remove(this_file)

            if debug:
                print("**** Build complete.  Here are the hot fixes:")
                print_Full_Report(fullReport)
                print("***********************************************************************************")
                print("**** Here is the package to hot fix dict:")
                print("***********************************************************************************")
                for current_package in packageToHotfix:
                    print("  " + current_package)
                    for machine_list in packageToHotfix[current_package]:
                        print("    " + machine_list[0] + " @ " + machine_list[1] + ".")
                print("***********************************************************************************")
                print("Report built.")
                print("Accessing environment Data.")

            for currentMachine in results['sas_hosts']:
                if not results['sas_hosts'][currentMachine]["_unreachable"] and not results['sas_hosts'][currentMachine]["_failed"]\
                   and results['sas_hosts'][currentMachine]['_sas_installed']:
                    currentOS = results['sas_hosts'][currentMachine]['os']['family']
                    for currentPackage in results['sas_hosts'][currentMachine]['sas_packages']:
                        if currentPackage in packageToHotfix:
                            for osHotfix in packageToHotfix[currentPackage]:
                                if osHotfix[0] == currentOS:
                                    currentHotfix = osHotfix[1]
                                    installedVersion = \
                                    results['sas_hosts'][currentMachine]['sas_packages'][currentPackage]['attributes']['version']
                                    if installedVersion.endswith('.suse'):
                                        installedVersion = installedVersion[:-5]
                                    else:
                                        if installedVersion.endswith('.yocto'):
                                            installedVersion = installedVersion[:-6]
                                        else:
                                            if '_' in installedVersion:
                                                installedVersion = installedVersion[0:installedVersion.rfind("_")]
                                    hotfixVersion = fullReport[currentHotfix]["package"][currentPackage]["platform"][currentOS]["version"]
                                    upToDate = compare_versions(installedVersion, hotfixVersion) >= 0
                                    fullReport[currentHotfix]["installed"] = True
                                    fullReport[currentHotfix]["package"][currentPackage]["platform"][currentOS]["installed"] = True
                                    # If a previous package marked updateToDate=True, it can still be pulled back to false if another package isn't
                                    # up to date.  If the previous package was marked upToDate=false, the hotfix cannot be marked true.
                                    if not fullReport[currentHotfix]["package"][currentPackage]["platform"][currentOS]["alreadyUpdated"] or \
                                        (fullReport[currentHotfix]["package"][currentPackage]["platform"][currentOS]["alreadyUpdated"] and
                                         fullReport[currentHotfix]["package"][currentPackage]["platform"][currentOS]["upToDate"]):
                                        fullReport[currentHotfix]["package"][currentPackage]["platform"][currentOS]["upToDate"] = upToDate
                                        fullReport[currentHotfix]["package"][currentPackage]["platform"][currentOS]["alreadyUpdated"] = True
                                    fullReport[currentHotfix]["package"][currentPackage]["platform"][currentOS]["installedVersions"][currentMachine] = [installedVersion, upToDate]

            if debug:
                print("Comparing evironment data to hotfix data.")
            for currentHotFix in fullReport:
                cumulativeOverallUpToDate = True
                # This will only allow the top level "upToDate" property to be set, if there is a package installed on this OS.
                allowTopLevelUpdate = False
                for currentPackage in fullReport[currentHotFix]["package"]:
                    cumulativeOSUpToDate = True
                    for currentOS in fullReport[currentHotFix]["package"][currentPackage]["platform"]:
                        if len(fullReport[currentHotFix]["package"][currentPackage]["platform"][currentOS]["installedVersions"]) > 0:
                            cumulativeOSUpToDate = cumulativeOSUpToDate and \
                                                   fullReport[currentHotFix]["package"][currentPackage]["platform"][currentOS][
                                                       "upToDate"]
                            allowTopLevelUpdate = True

                    cumulativeOverallUpToDate = cumulativeOverallUpToDate and cumulativeOSUpToDate
                if allowTopLevelUpdate:
                    fullReport[currentHotFix]["upToDate"] = cumulativeOverallUpToDate

            # Now that the fullReport has been updated, go back and add to results, for the final report.
            results["available_hotfixes"] = {}
            results["installed_hotfixes"] = {}

            for currentHotfix in fullReport:
                if not fullReport[currentHotfix]["installed"]:
                    continue
                if fullReport[currentHotfix]["upToDate"]:
                    hotfix_dict_to_use = "installed_hotfixes"
                else:
                    hotfix_dict_to_use = "available_hotfixes"
                results[hotfix_dict_to_use][currentHotfix] = {}
                results[hotfix_dict_to_use][currentHotfix]["release_date"] = fullReport[currentHotfix]["release_date"]
                results[hotfix_dict_to_use][currentHotfix]["packages"]     = []
                for currentPackage in fullReport[currentHotfix]["package"]:
                    for currentOS in fullReport[currentHotfix]["package"][currentPackage]["platform"]:
                        if not fullReport[currentHotfix]["package"][currentPackage]["platform"][currentOS]["installed"]:
                            continue
                        for currentHost in fullReport[currentHotfix]["package"][currentPackage]["platform"][currentOS]["installedVersions"]:
                            temp_dict = {}
                            temp_dict["hostname"]          = currentHost
                            temp_dict["package"]           = currentPackage
                            temp_dict["installed_version"] = fullReport[currentHotfix]["package"][currentPackage]["platform"][currentOS]["installedVersions"][currentHost][0]
                            temp_dict["hotfix_version"]    = fullReport[currentHotfix]["package"][currentPackage]["platform"][currentOS]["version"]
                            temp_dict["up_to_date"]        = fullReport[currentHotfix]["package"][currentPackage]["platform"][currentOS]["installedVersions"][currentHost][1]
                            results[hotfix_dict_to_use][currentHotfix]["packages"].append(temp_dict)
                # Format the SAS Note description so that we can respect any HTML tags that are included in the text.
                results[hotfix_dict_to_use][currentHotfix]["sas_notes"] = {}
                for current_number in fullReport[currentHotfix]["sasnote"]:
                    # Honor any html that is coming through.
                    temp_sasnote_description = fullReport[currentHotfix]["sasnote"][current_number].decode('utf-8')
                    temp_sasnote_description = temp_sasnote_description.replace("&lt;", "<")
                    temp_sasnote_description = temp_sasnote_description.replace("&gt;", ">")
                    # Build a link to the URL for the SAS Note.
                    hot_fix_prefix = current_number[:2]
                    hot_fix_postfix = current_number[2:]
                    sas_note_url = "http://support.sas.com/kb/" + hot_fix_prefix + "/" + hot_fix_postfix + ".html"
                    sas_note_html_link = "<a href=\"" + sas_note_url + "\"\>" + current_number + "</a>"
                    results[hotfix_dict_to_use][currentHotfix]["sas_notes"][current_number] = {"sas_note_link":sas_note_html_link, "description":temp_sasnote_description}

    if len(files_to_scan) == 0:
        formatted_file_output = "Installed products analyzed; no applicable hotfix files to report on.\n"
    else:
        formatted_file_output = "Installed Products analyzed; hotfix files used in report:\n"
        current_file_number = 1
        for current_file in files_to_scan:
            formatted_file_output = formatted_file_output + "  " + current_file_number.__str__() + ")  " + baseURL + current_file + "\n"
            current_file_number += 1

    results["hotfix_scanned_files"] = formatted_file_output

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    #
    # changed will always be 'False' since we'll never alter state on a host
    module.exit_json(changed=False, processed_host_details=results)


# =====
# Script entry point
# =====
if __name__ == '__main__':
    main()
