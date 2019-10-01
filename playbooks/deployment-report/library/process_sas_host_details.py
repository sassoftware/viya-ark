#!/usr/bin/python

####################################################################
# ### process_sas_host_details.py                                ###
####################################################################
# ### Author: SAS Institute Inc.                                 ###
####################################################################

from ansible.module_utils.basic import AnsibleModule
import ast
import urllib2
import traceback
import xml.etree.ElementTree as ET

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
    hotfix_master_file:
        description:
            -  The file that holds all of the hotfix infomration.
        require:  False
        default:  Viya_Update_Page_Index.xml
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
# This function takes in two string formated like so:
#   d.d.d[....]-dddddd
#
# Note:  The first string passed in will be the string that
# the playbook has passed in.  So, that will also contain
# OS specfic information.  It will be stripped out
# from splitdash1[1] below.
#
# Here are the return values:
#   -1 the first string is lower than the second string
#    0 the first and second strings match exactly.
#    1 the first string is higher than the second string.
###############################################
def compare_versions (version1, version2):
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

    if return_code == 0:
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
            hotfix_url = dict(type=str, required=True),
            hotfix_master_file = dict(type=str, required=True)
    ),
        supports_check_mode=True
    )

    # get module parameters
    hostvars = module.params['hostvars']
    report_timestamp = module.params['report_timestamp']
    registered_dict_name = module.params['registered_dict_name']
    include_hotfix_report = module.params['include_hotfix_report']
    hotfix_url = module.params['hotfix_url']
    hotfix_master_file = module.params['hotfix_master_file']

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

    results["include_hotfix_report"] = include_hotfix_report
    if include_hotfix_report:
        # This is the URL from which to pull the hotfix files.
        if hotfix_url[-1:] == '/':
            baseURL = hotfix_url
        else:
            baseURL = hotfix_url + '/'
        # This is the master file that lists which other files should be examined for the actual hotfixes themselves.
        masterFile = hotfix_master_file
        # This is the top level object to store the hotfix report information (see above).
        fullReport = {}
        # This is a dict of package to hotfixes (see above).
        packageToHotfix = {}
        # This boolean will help with debugging.
        debug = False

        try:
            # Parse the master file to obtain where the hotfix files are.
            masterFileXML = urllib2.urlopen(baseURL + masterFile)

            # Parse the master file and build a list of all files.
            allFilesRoot = ET.fromstring(masterFileXML.read())
            results["contact_hotfix_website"] = True
        except urllib2.URLError :
            results["contact_hotfix_website"] = False
            results["master_website"] = baseURL + masterFile
            if debug:
                print("***** Error parsing " + baseURL + masterFile)
                print(traceback.format_exc())
                print("***** No hot fix information obtained.  Skipping hot fix report.\n\n")

        if results["contact_hotfix_website"]:
            # Loop through the files discoverd in the master file
            if debug:
                print("Building hot fix report, based on master file input.")
            for file_tag in allFilesRoot.findall('File'):
                currentFile = file_tag.get('fileName')
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
                    currentFileXML = urllib2.urlopen(fileToParse)
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
                                    if os.lower().find("windows") > -1:
                                        versionStartIndex = fullPackage.rfind("-")
                                        achitectureStartIndex = -1
                                        versionEndIndex = lastPeriodIndex
                                        osFamily = "Windows"
                                    else:
                                        versionStartIndex = fullPackage.rfind("-", 0, fullPackage.rfind("-"))
                                        # Linux has architecture in the package.  This will be stored in its own key.
                                        achitectureStartIndex = fullPackage.rfind(".", 0, lastPeriodIndex)
                                        # SLES has the string 'suse' in its package.  This will strip it out (as well as an extra .).
                                        if os.lower().find("suse") > -1:
                                            versionEndIndex = achitectureStartIndex - 5
                                            osFamily = "Suse"
                                        else:
                                            if os.lower().find("yocto") > -1:
                                                versionEndIndex = achitectureStartIndex - 6
                                                osFamily = "Yocto"
                                            else:
                                                if os.lower().find("ubuntu") > -1:
                                                    versionStartIndex = fullPackage.rfind("_", 0, fullPackage.rfind("_"))
                                                    versionEndIndex = fullPackage.rfind("_")
                                                    achitectureStartIndex = versionEndIndex
                                                    osFamily = "Ubuntu"
                                                else:
                                                    if os.lower().find("red hat enterprise linux 7") > -1:
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
                except urllib2.HTTPError:
                    if debug:
                        print("***** Cannot access " + fileToParse)
                        print(traceback.format_exc())
                        print("***** Skipping the file.\n\n")
                except:
                    if debug:
                        print("***** Error encountered with " + fileToParse)
                        print(traceback.format_exc())
                        print("***** Skipping the file.\n\n")

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
                if not results['sas_hosts'][currentMachine]["_unreachable"] and not results['sas_hosts'][currentMachine]["_failed"]:
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
                                    # If a previous pacakage marked updateToDate=True, it can still be pulled back to false if another package isn't
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
                    temp_sasnote_description = fullReport[currentHotfix]["sasnote"][current_number]
                    temp_sasnote_description = temp_sasnote_description.replace("&lt;", "<")
                    temp_sasnote_description = temp_sasnote_description.replace("&gt;", ">")
                    # Build a link to the URL for the SAS Note.
                    hot_fix_prefix = current_number[:2]
                    hot_fix_postfix = current_number[2:]
                    sas_note_url = "http://support.sas.com/kb/" + hot_fix_prefix + "/" + hot_fix_postfix + ".html"
                    sas_note_html_link = "<a href=\"" + sas_note_url + "\"\>" + current_number + "</a>"
                    results[hotfix_dict_to_use][currentHotfix]["sas_notes"][current_number] = {"sas_note_link":sas_note_html_link, "description":temp_sasnote_description}

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
