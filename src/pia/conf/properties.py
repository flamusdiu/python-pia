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

import configparser
from pia.applications import appstrategy
from pia.conf import settings


class Props(object):
    """Global properties class.

    Attributes:
        login_config: path to where VPN login credentials are stored
        progs: list of supported programs
        apps: dictionary of application objects that will be configured
    """
    _hosts = []

    def __init__(self):
        self._exclude_apps = None
        self._debug = settings.DEBUG
        self._login_config = settings.LOGIN_CONFIG
        self._conf_file = settings.PIA_CONFIG

    def __repr__(self):
        return '<%s %s:%s>' % (self.__class__.__name__, 'hosts', self._hosts)

    @property
    def conf_file(self):
        return self._conf_file

    @property
    def login_config(self):
        """path to where VPN login credentials are stored"""
        return self._login_config

    @property
    def hosts(self):
        return self._hosts

    @hosts.setter
    def hosts(self, value):
        self._hosts = value

    @property
    def debug(self):
        return self._debug

    @debug.setter
    def debug(self, value):
        self._debug = value


class _Parser(object):
    """attributes may need additional manipulation"""

    def __init__(self, section):
        """section to return all options on, formatted as an object
        transforms all comma-delimited options to lists
        comma-delimited lists with colons are transformed to dicts
        dicts will have values expressed as lists, no matter the length
        """
        c = configparser.ConfigParser()
        c.read(props.conf_file)

        self.section_name = section

        self.__dict__.update({k: v for k, v in c.items(section)})

        # transform all ',' into lists, all ':' into dicts
        for key, value in self.__dict__.items():
            if value.find(':') > 0:
                # dict
                values = value.split(',')
                dicts = [{k: v} for k, v in [d.split(':') for d in values]]
                merged = {}
                for d in dicts:
                    for k, v in d.items():
                        merged.setdefault(k, []).append(v)
                self.__dict__[key] = merged
            elif value.find(',') > 0:
                # list
                self.__dict__[key] = value.split(',')
            else:
                self.__dict__[key] = [value]

    def __repr__(self):
        return '<%s %s:%s>' % (self.__class__.__name__, 'section', self.__dict__['section'])


def parse_conf_file():
    import logging

    logger = logging.getLogger(__name__)
    
    """Parses configure file 'pia.conf' using the Parser Class"""

    try:
        pia_section = _Parser("pia")
    except configparser.NoSectionError:
        pia_section = None
        logger.debug("Reading configuration file error. No %s" % 'pia')
        pass

    try:
        configure_section = _Parser("configure")
    except configparser.NoSectionError:
        configure_section = None
        logger.debug("Reading configuration file error. No %s" % 'configure')

    if pia_section and getattr(pia_section, "openvpn_auto_login"):
        appstrategy.set_option(getattr(props, 'openvpn'), autologin=pia_section.openvpn_auto_login)

    if configure_section and getattr(configure_section, "apps"):
        for app_name in configure_section.apps:
            appstrategy.set_option(getattr(props, app_name), configure=True)

    if configure_section and getattr(configure_section, "hosts"):
        props.hosts = configure_section.hosts


props = Props()  # creates global property object
