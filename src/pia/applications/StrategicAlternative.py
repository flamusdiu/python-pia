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
from pia.utils import multiple_replace
from pkg_resources import resource_string


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
        command_bin: list containing which files to check if the application is installed
        conf_dir: directory to the application stores it's configurations
        strategy: name of which strategy created this class
        config_template: location of the application's config_template

    """
    _conf_dir = ''
    _command_bin = []

    @property
    def command_bin(self):
        """list containing which files to check if the application is installed"""
        return self._command_bin

    @property
    def config_template(self):
        """location of the application's config_template"""
        return self._config_template

    @property
    def conf_dir(self):
        """directory to the application stores it's configurations"""
        return self._conf_dir

    @property
    def strategy(self):
        """name of which strategy created this class"""
        return self._strategy

    def __init__(self, strategy=None):
        self._strategy = strategy
        self._config_template = self.get_config_template()

    def config(self, config_id, filename):
        """Implemented in the subclass to modify configuration template for each VPN endpoint"""
        pass

    def remove_configs(self):
        """Removes all configurations for a strategy"""
        try:
            for f in os.listdir(self.conf_dir):
                path = os.path.join(self.conf_dir, f)
                os.remove(path)
        except OSError:
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
            print("Cannot access " + conf)

        try:
            os.chmod(conf, 0o600)  # Sets permissions to Read, Write, to Owner only.
            os.chown(conf, 0, 0)  # Sets ownership to root:root (uid 0).
        except OSError:
            print("Cannot change permissions on " + conf)

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
            return None

    def find_config(self, config_id):
        """Find if a configuration is configured

        Args:
            config_id: configuration name

        Returns:
            Returns bool depending on if the configuration is already installed
        """
        pass
