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
from pia.utils import has_proper_permissions
from pia.applications.Application import Application


class Props(object):
    """Global properties class.

    Attributes:
        login_config: path to where VPN login credentials are stored
        progs: list of supported programs
        apps: dictionary of application objects that will be configured
    """
    _login_config = '/etc/private-internet-access/login.conf'
    _progs = {'cm': False, 'nm': False, 'openvpn': False}
    _apps = dict()

    @property
    def login_config(self):
        """path to where VPN login credentials are stored"""
        return self._login_config

    @property
    def progs(self):
        """list of supported programs"""
        return self._progs

    @property
    def apps(self):
        """dictionary of application objects that will be configured"""
        return self._apps

    def check_installed(self):
        """Check which applications are installed.

        Calls is_installed() on each app object
        """
        for p in self.progs.keys():
            self.apps[p] = Application(p)
            self.progs[p] = self.apps[p].is_installed()

            if not self.progs[p]:
                self.apps.pop(p)

    @classmethod
    def get_login_credentials(cls):
        """Loads login credentials from file

        Returns:
            A list containing username and password for login service.
        """
        if not has_proper_permissions(props.login_config):
            print('ERROR: ' + props.login_config + ' must be owned by root and not world readable!')
            exit(1)

        p = pathlib.Path(props.login_config)
        try:
            # Opens login.conf and reads login and passwords from file
            with p.open() as f:
                content = f.read().splitlines()
        except OSError:
            return None

        return list(filter(bool,content))

props = Props()  # creates global property object
