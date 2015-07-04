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

import importlib as imp
import os

class Application(object):
    """Creates class to hold public API for different applications.

    Call this class as Application(strategy). For example, one of the predefined strategies is for NetworkManager,
    or 'nm' for short. To call this class for NetworkManager, use Application("nm").

    Attributes:
        strategy: name of the strategy this object refers to
    """

    @property
    def strategy(self):
        """Returns then strategy name.

        Returns strategy name from when this class was created.

        Returns:
            A string containing the strategy name.
        """
        return self._strategy

    def __init__(self, strategy):
        self._strategy = strategy
        self.app = \
            imp.import_module("pia.applications.hooks").__dict__[strategy].ApplicationStrategy(strategy)

    def config(self, config_id, filename, enable=False):
        """Configures configuration file for the given strategy.

        Calls the function config(config_id, filename) directly on the strategy object stored in self.app.

        Args:
            config_id: the name of the profile (i.e. "US East") used as the name of the VPN endpoint
            filename: the filename of where to store the finished configuration file
            enable: NOT USED
        """
        self.app.config(config_id, filename)

    def remove_configs(self):
        """Removes all configurations for a strategy"""
        self.app.remove_configs()

    def is_installed(self):
        """Checks to see if application for a strategy is installed"""
        installed = False
        for command in self.app.command_bin:
            try:
                if os.access(command, os.F_OK):
                    installed = True
            except OSError:
                installed = False
                continue

        return installed

    def find_config(self, config_id):
        """Find if a configuration is configured

        Args:
            config_id: configuration name

        Returns:
            Returns bool depending on if the configuration is already installed
        """
        return self.app.find_config(config_id)
