# -*- coding: utf-8 -*-

#    Private Internet Access Configuration auto-configures VPN files for PIA
#    Copyright (C) 2016  Jesse Spangenberger <azulephoenix[at]gmail[dot]com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
from collections import OrderedDict

import os
import sys

from pia import properties, __VERSION__
from pia.applications import Application
from pia.properties import props
from pia.docopt import docopt


def commandline_interface():
    doc = """
Usage: pia (-a | -r) [-v] [-e=STRATEGY...] [HOST... ]
       pia -l
       pia -h | --help
       pia --version

Configures PIA VPN Services for Connman, Network Manager, and OpenVPN

Arguments:
  HOST...                        A list of host names to configure

Options:
  -a, --auto-configure             Automatically generates configurations
  -r, --remove-configurations      Removes auto-generated configurations
  -l, --list-configurations        Lists known OpenVPN hosts
  -e=STRATEGY, --exclude=STRATEGY  Excludes modifying the configurations of the listed
                                   program. (Example: -e=cm,nm)
  -v, --verbose                    Enables more verbose logging
  -h, --help                       show this help message and exit
  --version                        show program's version number and exit

    """
    args = docopt(doc, version=__VERSION__)
    return args


def print_config_list():
    """Prints a list of installed OpenVPN configurations."""
    lis = Application.get_app('openvpn').app.configs.keys()
    configs = dict()
    for c in lis:
        configs[c] = []

    # Checks if configuration is installed for a given config_id
    for app_name in Application.get_supported_apps():
        app = Application.get_app(app_name)
        if not app.strategy == 'openvpn' and app.configure:
            configured_list = [c for c in lis if app.find_config(c)]
            for c in configured_list:
                configs[c].extend([app.strategy])

    if len(configs) > 0:
        # Prints out the list
        print("List of OpenVPN configurations")
    else:
        print("No OpenVPN configurations found!")

    for c in sorted(configs):
        dis = ''
        for app in configs[c]:
            dis += '[' + app + ']'
        print('   %s %s' % (c, dis))
    sys.exit()


def run():
    """Main function run from command line"""
    props.commandline = commandline_interface()

    # Checks to see which supported applications are installed

    props.apps = Application.check_apps()

    properties.parse_conf_file()

    if props.commandline['--list-configurations']:
        print_config_list()

    # Make sure we are running as root
    if os.getuid() > 0:
        print('ERROR: You must run this script with administrative privileges!')
        sys.exit(1)

    # If "-e" option was given, then make sure to set that application as 'False'
    # to keep from having it configured and cause errors.
    if props.commandline['--exclude']:
        for e in props.exclude.split(','):
            app = Application.get_app(e)
            if app and not app.strategy == 'openvpn':
                app.configure = False

    # Holds custom configuration list if any "HOSTS" were passed on the command line.
    custom_configs = {}

    # Shortcut for the openvpn app object
    openvpn = props.openvpn.app

    # Gets list of Hosts input from commandline
    if props.commandline['HOST']:
        props.hosts.extend(props.commandline['HOST'])

    # Removes any duplicate names
    props.hosts = list(set([h.strip() for h in props.hosts]))

    # Complies a list of custom configs
    if len(props.hosts) > 0:
        for config_id in props.hosts:
            custom_configs[config_id] = openvpn.configs[config_id]

    # Replaces OpenVPN complete set of configs with our custom set
    if custom_configs:
        openvpn.configs = custom_configs

    # if "-a" was given, then we need to configure each OpenVPN for our supported application,
    # else remove all configurations for supported applications other then OpenVPN.
    if props.commandline['--auto-configure']:
        for config in openvpn.configs:
            config_id, filename = openvpn.configs[config]

            for app_name in Application.get_supported_apps():
                app = Application.get_app(app_name)
                if app.configure:
                    app.config(config_id, filename)
    elif props.commandline['--remove-configurations']:
        for app_name in Application.get_supported_apps():
            app = Application.get_app(app_name)
            if not app.strategy == 'openvpn':  # We don't want to delete OpenVPN files!
                app.remove_configs()
