#!/usr/bin/python

####################################################################
# ### process_sas_host_details.py                                ###
####################################################################
# ### Author: SAS Institute Inc.                                 ###
####################################################################

from ansible.module_utils.basic import AnsibleModule
import ast

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['release'],
    'supported_by': 'SAS'
}

DOCUMENTATION = '''
---
module: process_sas_host_details

short_description: Processes and formats collected SAS host details.

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
            registered_dict_name=dict(type=str, required=False, default="get_sas_host_details_results")
        ),
        supports_check_mode=True
    )

    # get module parameters
    hostvars = module.params['hostvars']
    report_timestamp = module.params['report_timestamp']
    registered_dict_name = module.params['registered_dict_name']

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
