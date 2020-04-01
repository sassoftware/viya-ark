#!/usr/bin/env python

#
# Copyright (c) 2019-2020, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#

############################################################
#
#   merge_viya_deployment_files.py
#
############################################################

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves import configparser

import difflib
import json
import logging
import os
import re
import shutil
import six
import socket
import sys
import traceback

try:
    from ruamel.yaml import YAML
except ImportError:
    error_msg = 'The Python package YAML/emitter ruamel.yaml is not installed. Perform the PIP install command "pip install ruamel.yaml" from the Linux shell". Run the play after the ruamel.yaml install is successfully done.'
    # error_state = 'ruamel_yaml_is_not_installed'
    # LOG.error("Merging the vars.yml file failed with " + error_msg)
    raise ValueError(error_msg)


############################################################
#   GLOBALS
############################################################
# store intermediate work files here
WORKDIR = "$WORKDIR"

# create logging object
LOG = logging.getLogger()
LOG.setLevel(logging.INFO)
# console handle
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s filemerge [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
LOG.addHandler(ch)

############################################################
#  NEW PROPERTIES FOR POSTGRES HA
############################################################
HA_PGPOOL_VIRTUAL_IP_LINE    = "      - HA_PGPOOL_VIRTUAL_IP: ''\n"
HA_PGPOOL_WATCHDOG_PORT_LINE = "        HA_PGPOOL_WATCHDOG_PORT: ''\n"
PCP_PORT_LINE    = "      - PCP_PORT"
POOL_NUMBER_LINE = "        POOL_NUMBER: '0'\n"

############################################################
#   Get Local Environment
############################################################
def get_local_environment():

    """ Data to display in the log for debugging purposes """
    info = {}

    # hostname
    info['hostname'] = socket.gethostname()

    # cwd
    info['pwd'] = os.getcwd()

    # cli args
    info['script_args'] = sys.argv

    return info


############################################################
#   Write a yml file with the data
############################################################
def write_yaml(yaml_data, yaml_file):

    """ Performs the yaml write operation. """
    try:
        if not os.path.isdir(os.path.dirname(yaml_file)):
            os.makedirs(os.path.dirname(yaml_file))

        yaml = YAML()
        yaml.explicit_start = True
        yaml.indent(mapping=3)
        yaml.preserve_quotes = True  # not necessary for your current input
        with open(yaml_file, "wb") as outfile:
            yaml.dump(yaml_data, outfile)

        LOG.info("The vars.yml file has been merged successfully.")
        print("Created {0}".format(yaml_file))

    except (IOError, Exception):
        # Log error and raise exception if file cannot be created.
        error_msg = '{1}\nError writing {0}\n'.format(yaml_file, traceback.format_exc())
        LOG.error("Merging the vars.yml file failed with " + error_msg)
        raise ValueError(error_msg)


############################################################
#   Read data from the yaml and generate dict
############################################################
def read_yaml(yaml_file):
    """
    Load yaml file into dict structure.

    Argument:
        yaml_file(str) - full path/filename of yaml
    Returns:
        yaml_file_content(dict) - containing contents of yaml file
    Raises:
        ValueError raised when package yaml cannot be read
    """
    try:
        # Read the package yaml file
        yaml = YAML()
        yaml.explicit_start = True
        yaml.indent(mapping=3)
        yaml.preserve_quotes = True  # not necessary for your current input

        with open(yaml_file) as fp:
            data = yaml.load(fp)
        yaml.dump(data, sys.stdout)
        fp.close()
    except (IOError, ValueError):
        # Log error and raise exception if package yaml can't be read.
        error_msg = '{1}\nError loading {0}\n'.format(yaml_file, traceback.format_exc())
        LOG.error("Reading the vars.yml file failed with " + error_msg)
        raise ValueError(error_msg)

    return data


############################################################
#   Read values from the config file
############################################################
def read_config(cfg_file):
    cfg_parser = configparser.ConfigParser(allow_no_value=True)
    cfg_parser.optionxform = lambda option: option  # preserve as case-sensitive
    cfg_parser.read(cfg_file)
    return cfg_parser


############################################################
#   Read values from the given inventory file
############################################################
def read_inventory(inv_file, comments):
    tmp_file_name = 'inventory.tmp'
    if comments == 'yes':
        with open(inv_file) as current_file:
            with open(tmp_file_name, 'w') as tmp_file:
                tmp_file.writelines(i.replace('#', '99999;') for i in current_file.readlines())
    else:
        with open(inv_file) as current_file:
            with open(tmp_file_name, 'w') as tmp_file:
                tmp_file.writelines(i.replace('#', '#') for i in current_file.readlines())

    inv_parser = configparser.ConfigParser(allow_no_value=True)
    inv_parser.optionxform = lambda option: option  # preserve as case-sensitive
    try:
        inv_parser.read(tmp_file_name)
    except configparser.MissingSectionHeaderError:
        # need to inject [host-definitions] inventory section header to parse it
        try_again = six.StringIO()
        try_again.write('[host-definitions]\n')
        try_again.write(open(tmp_file_name).read())
        try_again.seek(0, os.SEEK_SET)
        inv_parser.readfp(try_again)

    return inv_parser


############################################################
#   Get Config Dict
############################################################
def _get_config_dict(some_config):
    config_dict = dict()
    for section in some_config.sections():
        config_dict[section] = some_config.items(section)

    return config_dict


############################################################
#   SKIP these properties when merging files
############################################################
SKIP_MERGE_OPTIONS = ['MAXIMUM_RECOMMENDED_ANSIBLE_VERSION', 'sas_install_type',
                      'LICENSE_FILENAME', 'LICENSE_COMPOSITE_FILENAME',
                      'remote_tmp', 'DEPLOYMENT_ID', 'tenant_instance',
                      'provider_endpoint_scheme', 'INSTALL_USER', 'INSTALL_GROUP',
                      'provider_endpoint_port','sas_consul_on_cas_hosts',
                      'casenv_tenant','REPOSITORY_WAREHOUSE','setup_sas_users','sas_users']


############################################################
#   Merge function for config file
############################################################
def _merge_config_option(current_config, new_config, section, option):
    if option in SKIP_MERGE_OPTIONS:
        if '99999;' not in option:
            LOG.info("The option " + option + " will not be carried to the newer file.")
        return

    value = current_config.get(section, option)

    if new_config.has_option(section, option):
        if '99999;' not in option:
            LOG.info("The current value of the option " + option + " was merged into the file.")
        else:
            if (option.startswith('99999; The ') & option.endswith('.')):
                option = '\n' + option.rstrip()
            pass
    else:
        if '99999;' not in option:
            LOG.info("The option " + option + " was added to the newer file.")
        else:
            if (option.startswith('99999; The ') & option.endswith('.')):
                option = '\n' + option.rstrip()
            pass

    section = section.lstrip()

    new_config.set(section, option, value)


############################################################
#   Merge function for vars.yml
############################################################
def _merge_vars_option(current_vars, new_vars, option):
    if option in SKIP_MERGE_OPTIONS:
        LOG.info("The option " + option + " will not be carried to the newer vars.yml file.")
        return

    value = current_vars.get(option)
    if option in new_vars:
        LOG.info("The current value of the option " + option + " was merged into the vars.yml file.")
        pass
    else:
        LOG.info("The option " + option + " was merged into the newer vars.yml file.")
        pass

    new_vars[option] = value


############################################################
#   Merge function for ansible.cfg
############################################################
def merge_ansible_config(current_config, new_config):
    test_result = dict()

    # read in the current config first, then merge into the new config
    current_sections = current_config.sections()
    new_sections = new_config.sections()

    for section in current_sections:
        if section in new_sections:
            LOG.info("The individual option " + section + " is merging into the existing section.")
            test_result[section] = 'MERGE'
            for option in current_config.options(section):
                _merge_config_option(current_config, new_config, section, option)

        else:
            LOG.info("The entire section " + section + " is moving to the newer ansible.cfg file unchanged.")
            test_result[section] = 'MOVE'

            new_config.add_section(section)

            for option in current_config.options(section):
                _merge_config_option(current_config, new_config, section, option)

    for section in new_sections:
        if section not in current_sections:
            LOG.info("The section " + section + " is a new section so no change will be made.")
            test_result[section] = 'NEW'

    # test_result['__MERGED__'] = str(_get_config_dict(new_config))

    return test_result


############################################################
#   Merge function for inventory.in
############################################################
def merge_inventory_ini(current_inventory, new_inventory, merge_default_host):
    test_result = dict()
    cmdline_hosts = ''

    # read in the current inventory first, then merge into the new inventory
    current_sections = current_inventory.sections()
    new_sections = new_inventory.sections()

    for section in current_sections:
        # save the current hosts for the commandline section
        if 'CommandLine' == section:
            for option in current_inventory.options(section):
                if cmdline_hosts is not '':
                    cmdline_hosts = cmdline_hosts + '\n' + option.split(' ', 1)[0]
                else:
                    cmdline_hosts = option.split(' ', 1)[0]

    for section in current_sections:
        # construct the hosts for the commandline section while keep the current hosts to the top
        if 'host-definitions' == section:
            for option in current_inventory.options(section):
                # append the rest of the hosts to the current Commandline host group
                if not re.search (r'\b' + option.split(' ', 1)[0] + '(?:\s|$)', cmdline_hosts):
                    cmdline_hosts = cmdline_hosts + '\n' + option.split(' ', 1)[0]

        if section in new_sections:
            if 'sas-all:children' == section or 'sas_all:children' == section:
                # leave the new children section intact
                continue

            LOG.info("The individual host group in the existing section " + section + " has been replaced.")

            test_result[section] = 'REPLACE'

            # first clear the new inventory hostgroup target placeholders
            for option in new_inventory.options(section):
                new_inventory.remove_option(section, option)

            # replace the current option with all hosts
            if 'CommandLine' == section:
                new_inventory.remove_option(section, option)
                new_inventory.set(section, cmdline_hosts, None)
            else:
                # merge in the current inventory hostgroup targets
                for option in current_inventory.options(section):
                    _merge_config_option(current_inventory, new_inventory, section, option)
        else:
            LOG.info("The entire host group in the existing section " + section + " does not exist.")
            test_result[section] = 'REMOVED'

    for section in new_sections:
        if section not in current_sections:
            if 'sas-all:children' == section or 'sas_all:children' == section:
                # leave the new children section intact
                continue

            test_result[section] = 'NEW'

            # first clear the new inventory hostgroup target placeholders
            for option in new_inventory.options(section):
                new_inventory.remove_option(section, option)

            if merge_default_host:
                new_inventory.set(section, merge_default_host, None)
                LOG.info("The new host group has been found and the host '" + merge_default_host + "' was added.")
            else:
                # set a temporary placeholder value to make the user choose later
                new_inventory.set(section, '? choose-target-host', None)
                LOG.info("The new host group has been found and a temporary value '? choose-target-host was added'. The temporary value must be replaced.")

    # test_result['__MERGED__'] = str(_get_config_dict(new_inventory))

    return test_result


############################################################
#   Post_proces after the merging inventory.ini
############################################################
def post_process_inventory(new_inventory_file, new_inventory_base_file):
    # apply post-processing on file contents to correct issues from ConfigParser
    # such as extra spaces between " = ", [host-definitions] group tag, and host range messups ucs[0 = 32]
    with open(new_inventory_file, 'r') as post_process_file:
        post_content = post_process_file.read()

        # remove [host-definitions] header line
        post_content = re.sub(r'^\[host-definitions\]$\n', '', post_content, flags=re.M)

        # fix range mixup e.g ucs[01 = 32] -> ucs[01:32]
        post_content = re.sub(r'^(.*\[\d+) = (\d+\].*)$', r'\1:\2', post_content, flags=re.M)

        # remove extra spaces around " = "
        post_content = re.sub(r'^(.*) = (.*)$', r'\1=\2', post_content, flags=re.M)

        # restore the removed comments
        post_content = re.sub('99999;', '#', post_content, flags=re.M)

        with open(new_inventory_file, 'w') as post_process_file:
            post_process_file.write(post_content)

        # restore the comments from the base inventory.ini
        searchquery = '#'
        searchword = ''

        with open(new_inventory_base_file) as f1:
            newline = ''
            lines = f1.readlines()
            for i, line in enumerate(lines):
                if line.startswith(searchquery):
                    newline = newline + line
                    searchword = lines[i + 1]
                    if not searchword.startswith(searchquery):
                        lineno = get_linenumber(new_inventory_file, searchword)
                        print (lineno)
                        replace_line(new_inventory_file, lineno, '\n' + newline)
                        newline = ''
                i = i + 1


############################################################
#   Merge function for vars.yaml
############################################################
def merge_vars_yml(current_vars, new_vars):
    test_result = dict()

    # read in the current vars first, then merge into the new vars
    current_options = current_vars.keys()
    new_options = new_vars.keys()

    for option in current_options:
        if option in new_options:
            test_result[option] = 'MERGE'

            _merge_vars_option(current_vars, new_vars, option)

        else:
            test_result[option] = 'MOVE'
            _merge_vars_option(current_vars, new_vars, option)

    for option in new_options:
        if option not in current_options:
            test_result[option] = 'NEW'

    # test_result['__MERGED__'] = str(new_vars)

    return test_result


############################################################
#   Print the diffs between the current and new file
############################################################
def print_diffs(current_file, new_file):
    baseline = ''
    diff = difflib.ndiff(open(current_file).readlines(), open(new_file).readlines())
    for line in diff:
        if line.startswith('-'):
            # sys.stdout.write(line)
            baseline += line
        elif line.startswith('+'):
            # sys.stdout.write('\t\t'+line)
            baseline += '\t\t' + line

    return baseline


############################################################
#   Restore the comments in the inventory.ini
############################################################
def replace_line(file_name, line_num, text):
    lines = open(file_name, 'r').readlines()
    lines[line_num] = text
    out = open(file_name, 'w+')
    out.writelines(lines)
    out.close()


def get_linenumber(cfg_file, searchword):
    line_no = 0
    with open(cfg_file) as f:
        for line_no, line in enumerate(f):
            if line == searchword:
                break
            else:
                line_no = -1
    return line_no-1


############################################################
#   Add new Postgres properties to cpspgpoolc and pgpoolc in the vars.yml
############################################################
def add_new_properties_invocation_variable (vars_file):
    with open(vars_file, "r") as in_file:
        buf = in_file.readlines()

    with open(vars_file, "w") as out_file:
        for line in buf:
            if line.startswith(PCP_PORT_LINE):
                line = HA_PGPOOL_VIRTUAL_IP_LINE + HA_PGPOOL_WATCHDOG_PORT_LINE + POOL_NUMBER_LINE +  line
            out_file.write(line)

############################################################
#   Main
############################################################
def main():
    fields = {
        "hostvars": {"required": True, "type": "str"},
        "current_inventory_file": {"required": True, "type": "str"},
        "current_files_dir": {"required": True, "type": "str"},
        "add_ha_properties": {"required": True, "type": "bool"},
        "log_file_name": {"required": True, "type": "str"},
        "tenant_id_string": {"required": False, "type": "str"},
        "merge_default_host": {"required": False, "type": "str"},
    }
    module = AnsibleModule(argument_spec=fields,
                           check_invalid_arguments=True,
                           supports_check_mode=True)

    current_inventory_file = module.params['current_inventory_file']
    current_files_dir = module.params['current_files_dir']
    add_ha_properties = module.params['add_ha_properties']

    if not current_inventory_file.startswith(os.sep):
        # force working with absolution path location
        current_inventory_file = os.getcwd() + os.sep + current_inventory_file

    if not os.path.isfile(current_inventory_file):
        fail_msg = "current_inventory_file is not a valid file: " + current_inventory_file
        LOG.error("The supplied inventory.ini " + current_inventory_file + " is not a valid file.")
        module.exit_json(failed=True, msg=fail_msg)

    current_vars_yml = os.path.join(current_files_dir, 'vars.yml')
    current_ansible_cfg = os.path.join(current_files_dir, 'ansible.cfg')

    if not os.path.isfile(current_vars_yml):
        fail_msg = "current_vars_yml is not a valid file: " + current_vars_yml
        LOG.error("The supplied vars.yml is not a valid file.")
        module.exit_json(failed=True, msg=fail_msg)

    if not os.path.isfile(current_ansible_cfg):
        fail_msg = "current_ansible_cfg is not a valid file: " + current_ansible_cfg
        LOG.error("The supplied ansible.cfg is not a valid file.")
        module.exit_json(failed=True, msg=fail_msg)

    # Create a file appender for the logger
    logfile = module.params['log_file_name']
    fhdlr = logging.FileHandler(logfile, 'w')
    new_inventory_dir = os.path.dirname(logfile)

    formatter = logging.Formatter(
        '%(asctime)s merge_viya_deployment_files [%(levelname)s] %(message)s')
    fhdlr.setFormatter(formatter)
    LOG.addHandler(fhdlr)
    LOG.info(" ")
    LOG.info("Process that merges SAS Viya deployment files started.")
    LOG.info("Current version of the merge_viya_deployment_files script: 19w34")
    LOG.debug("Temporary directory: %s" % WORKDIR)

    # Log details about the environment
    localinfo = get_local_environment()
    keys = sorted(localinfo.keys())
    for k in keys:
        LOG.debug("%s - %s" % (k, localinfo[k]))
    LOG.debug("")

    current_cfg = read_config(current_ansible_cfg)
    current_inventory = read_inventory(current_inventory_file, 'no')
    current_vars = read_yaml(current_vars_yml)
    hostvars_str = module.params['hostvars']
    hostvars = json.loads(hostvars_str)


    new_inventory_file = os.path.join(new_inventory_dir, 'inventory.ini')
    # back up the new inventory file
    new_inventory_base_file = os.path.join(new_inventory_dir, 'inventory.ini.default')
    shutil.copyfile(new_inventory_file, new_inventory_base_file)

    new_vars_yml = os.path.join(new_inventory_dir, 'vars.yml')
    new_ansible_cfg = os.path.join(new_inventory_dir, 'ansible.cfg')

    if not os.path.isfile(new_vars_yml):
        fail_msg = "new_vars_yml is not a valid file: " + new_vars_yml
        LOG.error("The vars.yml is not a valid file.")
        module.exit_json(failed=True, msg=fail_msg)

    if not os.path.isfile(new_ansible_cfg):
        fail_msg = "new_ansible_cfg is not a valid file: " + new_ansible_cfg
        LOG.error("The ansible.cfg is not a valid file.")
        module.exit_json(failed=True, msg=fail_msg)

    # Get the merge_default_host
    merge_default_host = module.params['merge_default_host']
    if merge_default_host:
        LOG.info("The merge_default_host is: " + merge_default_host)

    new_cfg = read_config(new_ansible_cfg)
    new_inventory = read_inventory(new_inventory_file, 'yes')
    new_vars = read_yaml(new_vars_yml)

    merge_cfg = merge_ansible_config(current_cfg, new_cfg)
    merge_inventory = merge_inventory_ini(current_inventory, new_inventory, merge_default_host)
    merge_vars = merge_vars_yml(current_vars, new_vars)

    # write merged results to files
    with open(new_ansible_cfg, 'w') as merge_file:
        new_cfg.write(merge_file)
    with open(new_inventory_file, 'w') as merge_file:
        new_inventory.write(merge_file)
    write_yaml(new_vars, new_vars_yml)

    # add new HA properties
    if add_ha_properties:
        add_new_properties_invocation_variable(new_vars_yml)
        LOG.info("The new postgres HA properties werer added to the newer vars.yml file.")

    # Get the tenant_id_list and do merge the tenant_vars.yml files
    tenant_string = module.params['tenant_id_string']
    try:
        if tenant_string:
            LOG.info("The tenant ID list is: " + tenant_string)
            tenant_ids = tenant_string.split(',')
            # LOG.info("The tenant ID list is: " + tenant_ids)
            for tenant in tenant_ids:
                LOG.info("The tenant ID is: " + tenant)
                LOG.info("The tenant ID vars.yml is: " + tenant + '_vars.yml')
                current_tenant_vars_yml = os.path.join(current_files_dir, tenant + '_vars.yml')
                current_tenant_vars = read_yaml(current_tenant_vars_yml)
                new_tenant_vars_yml = os.path.join(new_inventory_dir, tenant + '_vars.yml')
                new_tenant_vars = read_yaml(new_tenant_vars_yml)
                merge_tenant_vars = merge_vars_yml(current_tenant_vars, new_tenant_vars)
                write_yaml(new_tenant_vars, new_tenant_vars_yml)
    except NameError:
        pass

    # apply post-processing on file contents to correct issues from ConfigParser
    post_process_inventory(new_inventory_file, new_inventory_base_file)

    msg = ['Merge was done successfully:',
           'yaml_lib=%s' % YAML.__name__,
           'merge_cfg=%s' % str(merge_cfg),
           'merge_inventory=%s' % str(merge_inventory),
           'merge_vars=%s' % str(merge_vars)]
    module.exit_json(failed=False, msg=msg, merge=current_files_dir + ' -> ' + new_inventory_dir)


if __name__ == '__main__':
    main()
