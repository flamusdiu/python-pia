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
import argparse
import sys

from pia.properties import props


def menu():
    """Command line menu configuration."""

    # All options are stored globally in 'props' var.
    parser = argparse.ArgumentParser(
        description='Configures PIA VPN Services for Connman, Network Manager, and OpenVPN')

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-a', '--auto-configure', dest='configure', action='store_true',
                       help='Automatically generates configurations')
    group.add_argument('-r', '--remove-configurations', dest='configure', action='store_false',
                       help='Removes auto-generated configurations')
    parser.add_argument('-l', '--list-configurations', dest='list', action='store_true',
                        help='Lists known OpenVPN hosts')
    parser.add_argument('-e', '--exclude', dest='exclude', choices=props.progs, action='append',
                        help='Excludes modifying the configurations of the listed program. Maybe used more then once.')
    parser.add_argument('host', nargs='*', help='A list of host names to configure')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help='Enables more verbose logging')
    parser.add_argument('--version', action='version', version='%(prog)s 2.1')
    parser.parse_args(namespace=props)


def print_config_list():
    """Prints a list of installed OpenVPN configurations."""
    lis = props.apps['openvpn'].app.configs.keys()
    configs = {}

    # Changes the list of configs to a dictionary
    for item in lis:
        configs[item] = []

    # Checks if configuration is installed for a given config_id
    for config_id in configs:
        for app in props.apps:
            if not app == 'openvpn':
                configs[config_id].append(
                    {'app': app,
                     'configured': props.apps[app].app.find_config(config_id)}
                )

    # Prints out the list
    print("List of OpenVPN configurations")
    for c in sorted(configs):
        config = configs[c]
        dis = ''
        for app in config:
            if app['configured']:
                dis += '[' + app['app'] + ']'
        print('   %s %s' % (c, dis))
    sys.exit()


def run():
    """Main function run from command line"""
    menu()

    # Checks to see which supported applications are installed
    props.check_installed()

    if props.list:
        print_config_list()

    # Make sure we are running as root
    if os.getuid() > 0:
        print('ERROR: You must run this script with administrative privileges!')
        sys.exit(1)

    # If "-e" option was given, then make sure to set that application as 'False'
    # to keep from having it configured and cause errors.
    if props.exclude:
        for p in props.exclude:
            props.progs[p] = False

    # Holds custom configuration list if any "HOSTS" were passed on the command line.
    custom_configs = {}

    # Shortcut for the openvpn app object
    openvpn = props.apps['openvpn']

    # Complies a list of custom configs
    if props.host:
        for config_id in props.host:
            custom_configs[config_id] = openvpn.app.configs[config_id]

    # Replaces OpenVPN complete set of configs with our custom set
    if custom_configs:
        openvpn.app.configs = custom_configs

    # if "-a" was given, then we need to configure each OpenVPN for our supported application,
    # else remove all configurations for supported applications other then OpenVPN.
    if props.configure:
        for config in openvpn.app.configs:
            config_id, filename = openvpn.app.configs[config]

            if props.configure:
                for app in props.apps.keys():
                    if props.progs[app] and not app == 'openvpn':
                        props.apps[app].config(config_id, filename)
    else:
        for app in props.apps.keys():
            if not app == 'openvpn':  # We don't want to delete OpenVPN files!
                props.apps[app].remove_configs()
