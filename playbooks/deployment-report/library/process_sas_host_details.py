#!/usr/bin/python

####################################################################
# ### process_sas_host_details.py                                ###
####################################################################
# ### Author: SAS Institute Inc.                                 ###
####################################################################

from ansible.module_utils.basic import AnsibleModule

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
            hostvars=dict(type=dict, required=True),
            report_timestamp=dict(type=str, required=False, default=''),
            registered_dict_name=dict(type=str, required=False, default="sas_host_details")
        ),
        supports_check_mode=True
    )

    # get module parameters
    hostvars = module.params['hostvars']
    report_timestamp = module.params['report_timestamp']
    registered_dict_name = module.params['registered_dict_name']

    results = dict()
    results['sas_hosts'] = dict()
    results['created'] = report_timestamp

    for inventory_hostname, host_vars in hostvars.items():
        if host_vars.get(registered_dict_name) is not None:
            results['sas_hosts'].update(host_vars.get(registered_dict_name)['results'])
        else:
            host_groups = host_vars.get('group_names')

            if host_groups is not None and 'sas-all' in host_groups:
                hostname = host_vars.get('ansible_host')
                if hostname is None:
                    hostname = host_vars.get('ansible_hostname')
                    if hostname is None:
                        hostname = host_vars.get('inventory_hostname')
                        if hostname is None:
                            hostname = inventory_hostname

                try:
                    host_groups.remove('sas-all')
                except ValueError:
                    pass  # do nothing

                results['sas_hosts'][hostname] = dict(
                    _id=hostname.replace('.', '-'),
                    _unreachable=True,
                    ansible_host_groups=host_groups
                )
            else:
                pass  # this host isn't in sas-all so there's no need to try and report on it

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    #
    # changed will always be 'False' since we'll never alter state on a host
    module.exit_json(changed=False, results=results)


# =====
# Script entry point
# =====
if __name__ == '__main__':
    main()
