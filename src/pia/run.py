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

import os
import sys
import re

from pia import properties, __version__
from pia.applications import Application
from pia.properties import props
from pia.docopt import docopt

# Checks to see which supported applications are installed
props.apps = Application.check_apps()

# Shortcut for the openvpn app object
openvpn = props.openvpn.app


def run():
    """Main function run from command line"""
    props.commandline = commandline_interface()
    tmp_dict = dict([(re.sub('-', '_', x[2:].strip()), props.commandline[x])
                     for x in props.commandline if not x == 'HOST']).copy()
    tmp_dict.update({'HOST': props.commandline['HOST']})
    props.commandline = tmp_dict

    if props.commandline['list_configurations']:
        list_configurations()

    # Make sure we are running as root
    if os.getuid() > 0:
        print('ERROR: You must run this script with administrative privileges!')
        sys.exit(1)

    properties.parse_conf_file()

    if props.commandline['HOST'] or props.hosts:
        custom_hosts()

    try:
        [globals()[name]() for name in props.commandline if not name == 'HOST' and props.commandline[name]]
    except KeyError as e:
        docopt(globals()['commandline_interface'].__doc__, argv=['-h'], version=__version__)


def exclude():
    ex = props.commandline['exclude']
    for e in ex.split():
        app = Application.get_app(e)
        if app and not app.strategy == 'openvpn':
            app.configure = False


def custom_hosts():
    custom_configs = props.hosts or list()
    # Gets list of Hosts input from commandline
    if props.commandline['auto_configure']:
        custom_configs.extend(props.commandline['HOST'])
    else:
        custom_configs = props.commandline['HOST']

    # Removes any duplicate names
    openvpn.configs = list(set([re.sub(' ', '_', h.strip()) for h in custom_configs]))


def remove_configurations():
    for app_name in Application.get_supported_apps():
        app = Application.get_app(app_name)
        if not app.strategy == 'openvpn':  # We don't want to delete OpenVPN files!
            app.remove_configs(openvpn.configs)


def auto_configure():
    for config in openvpn.configs:
        for app_name in Application.get_supported_apps():
            app = Application.get_app(app_name)
            if app.configure:
                app.config(*getattr(openvpn, config))


def commandline_interface():
    """
Usage: pia -a [-e STRATEGIES] [HOST [HOST]... ]
       pia -r [HOST [HOST]... ]
       pia -l
       pia -h | --help
       pia --version

Configures PIA VPN Services for Connman, Network Manager, and OpenVPN

Arguments:
  HOST [HOST]...                       A list of host names to configure
                                       (Example: Japan 'US East' Russia)

Options:
  -a, --auto-configure                 Automatically generates configurations
  -r, --remove-configurations          Removes auto-generated configurations
  -l, --list-configurations            Lists known OpenVPN hosts
  -e STRATEGIES, --exclude STRATEGIES  Excludes modifying the configurations of the listed
                                       program. (Example: -e cm,nm)
  -h, --help                           show this help message and exit
  --version                            show program's version number and exit

    """
    args = docopt(commandline_interface.__doc__, version=__version__)
    return args


def list_configurations():
    """Prints a list of installed OpenVPN configurations."""
    lis = Application.get_app('openvpn').app.configs
    configs = dict()
    for c in lis:
        configs[c] = []

    # Checks if configuration is installed for a given config_id
    for app_name in Application.get_supported_apps():
        app = Application.get_app(app_name)
        if not app.strategy == 'openvpn' and app.configure:
            #  configured_list = [c for c in lis if app.find_config(c)]
            [configs[c].extend([app.strategy]) for c in lis if app.find_config(c)]

    if len(configs) > 0:
        # Prints out the list
        print("List of OpenVPN configurations")
        for c in sorted(configs):
            dis = ''
            for app in configs[c]:
                dis += '[' + app + ']'
            print('   %s %s' % (re.sub('_',' ',c), dis))
    else:
        print("No OpenVPN configurations found!")
    sys.exit()
