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
import re
import sys
import pia.properties

from pkg_resources import resource_listdir
from importlib import import_module


class Application(object):
    """Creates class to hold public API for different applications.

    Call this class as Application(strategy). For example, one of the predefined strategies is for NetworkManager,
    or 'nm' for short. To call this class for NetworkManager, use Application("nm").

    Attributes:
        strategy: name of the strategy this object refers to
    """

    @property
    def configure(self):
        return self._configure

    @configure.setter
    def configure(self, b):
        self._configure = b

    @property
    def strategy(self):
        """Returns then strategy name.

        Returns strategy name from when this class was created.

        Returns:
            A string containing the strategy name.
        """
        return self.app.strategy

    def __init__(self):
        self._configure = False
        self.app = None

    def config(self, config_id, filename):
        """Configures configuration file for the given strategy.

        Calls the function config(config_id, filename) directly on the strategy object stored in self.app.

        Args:
            config_id: the name of the profile (i.e. "US East") used as the name of the VPN endpoint
            filename: the filename of where to store the finished configuration file
            enable: NOT USED
        """
        self.app.config(config_id, filename)

    def remove_configs(self, hosts):
        """Removes VPN configurations for a strategy"""

        self.app.remove_configs(self.app.conf_dir, hosts)

    def is_installed(self):
        """Checks to see if application for a strategy is installed"""
        installed = None
        for command in self.app.command_bin:
            try:
                installed = os.access(command, os.F_OK)
            except OSError:
                installed = False
        return installed

    def find_config(self, config_id):
        """Find if a configuration is configured

        Args:
            config_id: configuration name

        Returns:
            Returns bool depending on if the configuration is already installed
        """
        return self.app.find_config(config_id)


def build_strategy(strategy):
    """Creates an applicaiton options with strategy

    Args:
        strategy: name of the strategy from pia.applications.hooks directory (no .py)

    Returns:
        Application object with the name strategy
    """
    application = Application()
    application.app = getattr(import_module('pia.applications.hooks.' + strategy), 'ApplicationStrategy')()

    return application


def set_option(application, **kwargs):
    """Sets an option on an application

    Only values in the 'supported_options' list will be configured. Any other options will be kicked out
    in a list on the command line.

    Args:
        application: instance of the Application class
        kwargs: list of keyword options to add to the application

    """
    supported_options = ['autologin', 'configure']
    options = [opt for opt in kwargs if opt in supported_options]
    bad_options = [opt for opt in kwargs if opt not in supported_options]

    for opt in options:
        try:
            setattr(application, opt, kwargs[opt])
        except AttributeError:
            if application:
                application.__dict__[opt] = kwargs[opt]
            else:
                print('Cannot set opt: %s on a %s!' % (opt, type(application).__name__))

    for opt in bad_options:
        print("Option %s is not unsupported." % opt)


def get_app(app_key):
    try:
        app = getattr(pia.properties.props, app_key)
    except AttributeError:
        return None
    return app


def check_apps():
    apps = get_supported_apps()
    for app in apps:
        a = build_strategy(app)
        a.configure = a.is_installed()

        pia.properties.props.__dict__[app] = a


def get_supported_apps():
    """Scans Hooks folder for application files

    Returns:
        A list of configured applications in a hooks directory
    """
    apps = list()

    try:
        for a in [f[:-3] for f in resource_listdir(__name__, 'hooks')
                  if not re.match(r'__[A-Za-z0-9]*__', f)]:
            apps.extend([a])
    except OSError:
        print("ERROR: Cannot read application hooks.")
        sys.exit(1)

    return apps
