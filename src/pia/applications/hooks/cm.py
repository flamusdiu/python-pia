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

import re

from pia.applications.StrategicAlternative import StrategicAlternative
from pia.applications.hooks.openvpn import ApplicationStrategy as openVPN


class ApplicationStrategy(StrategicAlternative):
    """Strategy file for Connman

    Attributes:
        command_bin: list containing which files to check if the application is installed
        conf_dir: directory to the application stores it's configurations
    """
    _conf_dir = '/var/lib/connman-vpn'
    _command_bin = ['/usr/bin/connmanctl']

    def config(self, config_id, filename, enable=None):
        """Configures configuration file for the given strategy.

        Args:
            config_id: the name of the profile (i.e. "US East") used as the name of the VPN endpoint
            filename: the filename of where to store the finished configuration file
            enable: NOT USED
        """

        # Directory of replacement values for connman's configuration files
        re_dict = {"##id##": config_id,
                   "##filename##": filename,
                   "##remote##": openVPN.get_remote_address(filename)}

        # Complete path of configuration file
        cm_conf = self.conf_dir + "/" + re.sub(' ', '_', config_id) + ".config"

        # Modifies configuration file
        self.update_config(re_dict, cm_conf)
