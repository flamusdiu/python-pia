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
import logging
import os
import sys
import re

from pia import __version__
from pia.conf import properties
from pia.applications import appstrategy
from pia.conf.properties import props
from docopt import docopt

logger = logging.getLogger(__name__)

# Checks to see which supported applications are installed
appstrategy.check_apps()

# Shortcut for the openvpn app object
openvpn = props.openvpn.app

if not openvpn.configs:
    logger.error("Missing OpenVPN configurations in /etc/openvpn!")
    exit(1)


def run():
    """Main function run from command line"""
    logger.debug('Parsing commandline args...')
    props.commandline = commandline_interface()

    if props.commandline.list_configurations:
        list_configurations()

    # Make sure we are running as root
    if os.getuid() > 0:
        logger.error('You must run this script with administrative privileges!')
        sys.exit(1)

    properties.parse_conf_file()

    if props.commandline.hosts or props.hosts:
        custom_hosts()

    [globals()[k]() for k, v in props.commandline.__dict__.items() if
        not k == 'hosts' and getattr(props.commandline, k, None)]


def exclude():
    """Excludes applications from being configured."""
    ex = props.commandline.exclude
    for e in ex.split():
        app = appstrategy.get_app(e)
        if app and not app.strategy == 'openvpn':
            app.configure = False


def custom_hosts():
    """Creates custom hosts list

    The host list is built from either commandline (by listing them after all other options)
    or in the config file in '/etc/private-internet-access-vpn' and combines the lists
    together. This then replaces the openvpn config list on which hosts to modify.

    """
    custom_configs = props.hosts or list()
    # Gets list of Hosts input from commandline
    if props.commandline.auto_configure:
        custom_configs.extend(props.commandline.hosts)

    # Removes any duplicate names
    openvpn.configs = list(set([re.sub(' ', '_', h.strip()) for h in custom_configs]))


def remove_configurations():
    """Removes configurations based on openvpn.configs"""
    logger.debug("Removing configurations!")
    for app_name in appstrategy.get_supported_apps():
        app = appstrategy.get_app(app_name)
        if app.strategy == 'openvpn':
            properties.reset_properties()
            for config in openvpn.all_configs:
                logger.debug("Removing config for %s" % config)
                app.config(*getattr(openvpn, config))
        else:  # We don't want to delete OpenVPN files!
            app.remove_configs(openvpn.all_configs)


def auto_configure():
    """Auto configures applications"""
    for config in openvpn.configs:
        print(appstrategy.get_app("openvpn").__dict__)
        for app_name in appstrategy.get_supported_apps():
            app = appstrategy.get_app(app_name)
            if app.configure:
                logger.debug("Configuring configurations for %s" % app_name)
                app.config(*getattr(openvpn, config))


def commandline_interface():
    """Configures PIA VPN Services for Connman, Network Manager, and OpenVPN

Usage: pia -a [-d] [-e STRATEGIES] [HOST [HOST]... ]
       pia -r [-d] [HOST [HOST]... ]
       pia -l [-d]
       pia -h | --help
       pia --version

Arguments:
  HOST [HOST]...                       A list of host names to configure
                                       (Example: Japan 'US East' Russia)

Options:
  -a, --auto-configure                 Automatically generates configurations
  -r, --remove-configurations          Removes auto-generated configurations
  -l, --list-configurations            Lists known OpenVPN hosts
  -e STRATEGIES, --exclude STRATEGIES  Excludes modifying the configurations of the listed
                                       program. (Example: -e cm,nm)
  -d, --debug                          enables debug logging to console
  -h, --help                           show this help message and exit
  --version                            show program's version number and exit
    """
    class CommandLineOptions(object):
        def __repr__(self):
            opts = {}
            for opt in self.__dict__.items():
                opts.update({opt[0]: opt[1] or None})

            return '<%s %s>' % (self.__class__.__name__, opts)

        def __setattr__(self, key, value):
            if key == "HOST":
                object.__setattr__(self, 'hosts', value)
            else:
                # Substitute option names: --an-option-name for an_option_name
                import re
                key = re.sub(r'^__', "", re.sub(r'-', "_", key))

                object.__setattr__(self, key, value)

        def __getattr__(self, item):
            return self.__dict__[item]

    cli_options = CommandLineOptions()

    options = docopt(commandline_interface.__doc__.__str__(), version=__version__)

    [setattr(cli_options, opt, options[opt]) for opt in options]
    return cli_options


def list_configurations():
    """Prints a list of installed OpenVPN configurations."""
    lis = appstrategy.get_app('openvpn').app.configs
    configs = dict()
    for c in lis:
        configs[c] = []

    # Checks if configuration is installed for a given config_id
    for app_name in appstrategy.get_supported_apps():
        app = appstrategy.get_app(app_name)
        if not app.strategy == 'openvpn' and app.configure:
                for c in lis:
                    if app.find_config(c):
                        logger.debug('Configuring %s for %s' % (c, app.strategy))
                        configs[c].extend([app.strategy])

    if len(configs) > 0:
        # Prints out the list
        print("List of OpenVPN configurations")
        for c in sorted(configs):
            dis = ''
            for app in configs[c]:
                dis += '[' + app + ']'
            print('   %s %s' % (re.sub('_', ' ', c), dis))
    else:
        logger.info("No OpenVPN configurations found!")
    sys.exit()


def debug():
    props.debug = True
    logging.getLogger("root").setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
