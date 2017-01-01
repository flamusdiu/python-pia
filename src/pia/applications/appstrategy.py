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
import inspect
import logging
import os
import shutil
from re import findall, escape
import sys
import warnings

import re

import pia
import importlib
from pkg_resources import resource_string

from pia.conf import properties
from pia.utils.misc import multiple_replace

logger = logging.getLogger(__name__)


class Application(object):
    """Creates class to hold public API for different applications.

    Call this class as Application(strategy). For example, one of the predefined strategies is for NetworkManager,
    or 'nm' for short. To call this class for NetworkManager, use Application("nm").

    Attributes:
        @strategy: name of the strategy this object refers to
    """

    @property
    def app(self):
        return self._app

    @app.setter
    def app(self, a):
        self._app = a

    @property
    def configure(self):
        return self._configure

    @configure.setter
    def configure(self, b):
        self._configure = b

    @property
    def strategy(self):
        """Returns the strategy name.

        Returns strategy name from when this class was created.

        Returns:
            A string containing the strategy name.
        """
        return self.app.strategy

    def __init__(self):
        self._configure = False
        self._app = None

    def config(self, config_id,):
        """Configures configuration file for the given strategy.

        Calls the function config(config_id, filename) directly on the strategy object stored in self.app.

        Args:
            config_id: the name of the profile (i.e. "US East") used as the name of the VPN endpoint
        """
        self.app.config(config_id)

    def remove_configs(self):
        """Removes all configurations for a strategy

        Raises:
            OSError: Throws if config cannot be removed
            FileNotFoundError: Thrown if the configuration directory doesn't exists

        """

        hosts = [re.sub(' ', '_', h) for h in properties.get_default_hosts_list(names_only=True)]
        conf_dir = self.app.conf_dir

        cdir = []

        try:
            cdir = os.listdir(conf_dir)
        except FileNotFoundError:
            pass

        if hosts:
            regex = re.compile("(%s)" % "|".join(map(escape, hosts)))
            cdir = [d for d in cdir if regex.match(d)]

        try:
            for f in cdir:
                path = os.path.join(conf_dir, f)
                os.remove(path)
        except OSError:
            pass

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
    """Creates an application options with strategy

    Args:
        strategy: name of the strategy from pia.applications.hooks directory (no .py)

    Returns:
        Application object with the name strategy
    """
    application = Application()
    application.app = getattr(importlib.import_module('pia.applications.hooks'),
                              'ApplicationStrategy' + strategy.upper())()

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
                logger.warning('Cannot set opt: %s on a %s!' % (opt, type(application).__name__))

    for opt in bad_options:
        logger.warning("Option %s is not unsupported." % opt)
 

def get_app(app_key):
    """Gets the application object by name

    Arguments:
        app_key: Name of the application to return

    Returns:
        Returns an application instance from the global properties object.
    """
    return getattr(pia.conf.properties.props, app_key, None)


def check_apps():
    """Verifies each supported application is installed

    Gets a list of supported applications and builds the application objects.
    Checks to see if the application is installed using the Application.is_installed()
    method. All applications installed are automatically set to be configured unless '-e' is
    given when running the application.

    """
    apps = get_supported_apps()
    for app in apps:
        a = build_strategy(app)
        a.configure = a.is_installed()
        pia.conf.properties.props.__dict__[app] = a


def get_supported_apps():
    """Scans Hooks folder for application files

    Returns:
        A list of configured applications in a hooks directory
    """
    apps = list()

    try:
        importlib.import_module('pia.applications.hooks')
    except OSError:
        logger.error("Cannot read application hooks.")
        sys.exit(1)

    tmp_apps = [n[0] for n in inspect.getmembers(sys.modules['pia.applications.hooks'], inspect.isclass)]

    logger.debug("Application hooks found: %s" % tmp_apps)

    for n in tmp_apps:
        apps.extend([a.lower() for a in findall('ApplicationStrategy([A-Za-z]*)', n) if a])

    return apps


class StrategicAlternative(object):
    """Each application requires its own StrategicAlternative object

    This class must be extended to 'applications.hooks' for each application that is supported.
    An example extended class of this class is:
        class ApplicationStrategy(StrategicAlternative):
            _conf_dir = '/var/lib/configdir'
            _command_bin = ['/usr/bin/example-app']

            def config(self, config_id, filename, enable=None):
                #You must create your own function to update the configuration files.
                #By default, each class creates a 're_dict' to hold a directory of replacement files
                #and calls self.update_config() to update the configuration
                pass

    Attributes:
        @command_bin: list containing which files to check if the application is installed
        @conf_dir: directory to the application stores it's configurations
        @strategy: name of which strategy created this class
        @config_template: location of the application's config_template

    """
    _CONF_DIR = ''
    _COMMAND_BIN = []

    @property
    def command_bin(self):
        """list containing which files to check if the application is installed"""
        return self._COMMAND_BIN

    @property
    def config_template(self):
        """location of the application's config_template"""
        return self._CONFIG_TEMPLATE

    @property
    def conf_dir(self):
        """directory to the application stores it's configurations"""
        return self._CONF_DIR

    @property
    def strategy(self):
        """name of which strategy created this class"""
        return self._strategy

    def __init__(self, strategy):
        self._strategy = strategy
        self._CONFIG_TEMPLATE = self.get_config_template()

    def __repr__(self):
        return '<%s %s:%s>' % ('StrategicAlternative.' + type(self).__name__, 'strategy', self._strategy)

    def config(self, config_id):
        """Implemented in the subclass to modify configuration template for each VPN endpoint"""
        pass

    def update_config(self, re_dict, conf):
        """Modifies configuration file with dictionary

        You must create a dictionary to do a single pass, multi-replacement on each configuration.
        An example dictionary is:
                re_dict = {"##id##": config_id,
                   "##filename##": filename,
                   "##remote##": openVPN.get_remote_address(filename)}
        Each of the '##<ATTRIBUTE>## is located in the configuration template and will be replaced
        with the value of each key.

        Args:
            re_dict: dictionary to replace values in the configuration files
            conf: a string which is the full path to the configuration file to create

        Raises:
            OSError: problems trying to write or change permissions on config files.
        """
        try:
            with open(conf, "w") as c:
                c.write(multiple_replace(re_dict, self.config_template))
        except OSError:
            warnings.warn("Cannot access %s." % conf)

        try:
            logger.debug('Changing permission on %s.' % conf)
            os.chmod(conf, 0o600)  # Sets permissions to Read, Write, to Owner only.
            shutil.chown(conf, "root", "network")  # Sets ownership to root:root (uid 0).
            logger.debug('Changing permission on %s was successful.' % conf)
        except OSError:
            warnings.warn("Cannot change permissions on %s." % conf)

    def get_config_template(self):
        """Loads the config template file.

        Returns:
            The complete configuration template file from the package directory located
            at <package dir>/template-configs

        Raises:
            OSError: problem reading the template file from the file system.
        """
        try:
            return resource_string(__name__, 'template-configs/' + self.strategy + '.cfg').decode()
        except OSError:
            if not self.strategy:
                logger.warning("Cannot load template file: %s" % 'template-configs/' + self.strategy + '.cfg')
            return None

    def find_config(self, config_id):
        """Find if a configuration is configured

        Args:
            config_id: configuration name

        Returns:
            Returns bool depending on if the configuration is already installed
        """
        os_access = os.access(self.conf_dir + '/' + re.sub(' ', '_', config_id), os.F_OK)

        if not os_access:
            os_access = os.access(self.conf_dir + '/' + re.sub(' ', '_', config_id) + '.conf', os.F_OK)

        return os_access
