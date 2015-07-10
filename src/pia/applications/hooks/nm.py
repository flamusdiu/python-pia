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

from uuid import uuid4
import os

import pia
from pia.applications.StrategicAlternative import StrategicAlternative
from pia.applications.hooks import openvpn
from pia.utils import get_login_credentials


class ApplicationStrategy(StrategicAlternative):
    """Strategy file for NetworkManager.

    Attributes:
        command_bin: list containing which files to check if the application is installed
        conf_dir: directory to the application stores it's configurations
    """
    _CONF_DIR = '/etc/NetworkManager/system-connections'
    _COMMAND_BIN = ['/usr/bin/nmcli', '/usr/lib/networkmanager/nm-openvpn-service']

    def __init__(self):
        super().__init__('nm')

    def config(self, config_id, filename):
        """Configures configuration file for the given strategy.

        NetworkManager requires VPN credentials in its configuration files. So, those are
        pulled in using Props.get_login_credentials() classmethod.

        Args:
            config_id: the name of the profile (i.e. "US East") used as the name of the VPN endpoint
            filename: the filename of where to store the finished configuration file
            enable: NOT USED
        """

        # Gets VPN username and password
        username, password = get_login_credentials(pia.properties.props.login_config)

        # Directory of replacement values for NetworkManager's configuration files
        re_dict = {"##username##": username,
                   "##password##": password,
                   "##id##": config_id,
                   "##uuid##": str(uuid4()),
                   "##remote##": openvpn.get_remote_address(filename)}

        # Complete path of configuration file
        conf = self.conf_dir + "/" + config_id

        # Modifies configuration file
        self.update_config(re_dict, conf)

    def find_config(self, config_id):
        """Find if a configuration is configured

        Args:
            config_id: configuration name

        Returns:
            Returns bool depending on if the configuration is already installed
        """
        conf = self.conf_dir + "/" + config_id

        return os.access(conf, os.F_OK)
