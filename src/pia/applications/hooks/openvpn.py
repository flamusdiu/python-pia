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

import pathlib
import glob
import re

from pia.applications.StrategicAlternative import StrategicAlternative
from pia.properties import props


class ApplicationStrategy(StrategicAlternative):
    """Strategy file for OpenVPN

    OpenVPN's strategy class is always created. It has extra functions then other
    strategic classes.

    Attributes:
        command_bin: list containing which files to check if the application is installed
        conf_dir: directory to the application stores it's configurations
        configs: the list of openVPN configurations to modify
    """
    _command_bin = ['/usr/bin/openvpn']
    _conf_dir = '/etc/openvpn'
    _configs = {}

    @property
    def configs(self):
        return self._configs

    @configs.setter
    def configs(self, configs):
        """the list of openVPN configurations to modify"""
        self._configs = configs

    def __init__(self, strategy):
        super().__init__(strategy)
        self.get_configs()

    def config(self, config_id, filename, enable=True):
        """Configures configuration file for the given strategy.

        Args:
            config_id: the name of the profile (i.e. "US East") used as the name of the VPN endpoint
            filename: the filename of where to store the finished configuration file
            enable: allows auto-login in openVPN configs

        Raises:
            OSError: problems with reading or writing configuration files
        """
        print(filename)
        p = pathlib.Path(filename)
        content = ''

        try:
            with p.open() as f:
                content = f.read()
        except IOError:
            print('Cannot access ' + config_id + '.')
            exit(1)

        if enable:
            content = re.sub('(auth-user-pass)(?:.*)', 'auth-user-pass ' + props.login_config, content)
        else:
            content = re.sub('(auth-user-pass)(?:.*)', 'auth-user-pass', content)

        try:
            with open(filename, "w") as f:
                f.write(content)
        except IOError:
            print('Cannot access ' + config_id + '.')
            exit(1)

    def get_configs(self):
        """Gets the list of configuration files to be modified"""
        for filename in glob.glob(self.conf_dir + '/*.conf'):
            config_id = re.sub('_', ' ', re.match(r"^/(.*/)*(.+)\.conf$", filename).group(2))
            self.configs[config_id] = [re.sub(' ', '_', config_id), filename]

    def remove_configs(self):
        """Not implemented for OpenVPN. We don't want to delete installed configs."""
        raise NotImplementedError

    @staticmethod
    def get_remote_address(config):
        """Finds the remote server host/ip address

        Args:
            config: string with the full path to configuration file

        Returns:
            Returns the host or ip address in the OpenVPN configuration file

        Raises:
            OSError: problems reading configuration file

        """
        p = pathlib.Path(config)
        try:
            with p.open() as f:
                contents = f.read()
        except OSError:
            return None

        return ''.join(re.findall("(?:remote.)(.*)(?:.\d{4})", contents))

    def find_config(self, config_id):
        """Not implemented for OpenVPN. No need to search for a configuration."""
        raise NotImplementedError
