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
import logging
from collections import namedtuple

from pia.applications import appstrategy
from pia.conf import settings

logger = logging.getLogger(__name__)


class Props(object):
    """Global properties class.
    """
    _pia_hosts_list = {}
    _hosts = []
    _port = ''
    _conf_section = {}
    _cipher = ''
    _auth = ''
    _protocol = ''
    _debug = ''
    _root_ca = ''
    _root_crl = ''
    _default_port = '1198'
    _config_lookup = {
        'default': {
            'cipher': 'aes-128-cbc',
            'auth': 'sha1',
            'root_ca': 'ca.rsa.2048.crt',
            'root_crl': 'crl.rsa.2048.pem'
        },
        'strong': {
            'cipher': 'aes-256-cbc',
            'auth': 'sha256',
            'root_ca': 'ca.rsa.4096.crt',
            'root_crl': 'crl.rsa.4096.pem'
        },
        'alternative': {
            'cipher': 'bf-cbc',
            'auth': 'sha1',
            'root_ca': 'ca.crt',
            'root_crl': 'crl.pem'
        }
    }
    _port_lookup = {
        '53': {
            'protocol': 'udp',
            'config': 'alternative'
        },
        '80': {
            'protocol': 'tcp',
            'config': 'alternative'
        },
        '110': {
            'protocol': 'tcp',
            'config': 'alternative'
        },
        '443': {
            'protocol': 'tcp',
            'config': 'alternative'
        },
        '501': {
            'protocol': 'tcp',
            'config': 'strong'
        },
        '502': {
            'protocol': 'tcp',
            'config': 'default'
        },
        '1194': {
            'protocol': 'udp',
            'config': 'alternative'
        },
        '1197': {
            'protocol': 'udp',
            'config': 'strong'
        },
        '1198': {
            'protocol': 'udp',
            'config': 'default'
        },
        '8080': {
            'protocol': 'udp',
            'config': 'alternative'
        },
        '9201': {
            'protocol': 'udp',
            'config': 'alternative'
        },
    }

    def __init__(self):
        self.exclude_apps = None
        self.debug = settings.DEBUG
        self._login_config = settings.LOGIN_CONFIG
        self._conf_file = settings.PIA_CONFIG
        self.port = self._default_port
        self._default_hosts_list = get_default_hosts_list()

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
        return self._hosts or get_default_hosts_list(names_only=True)

    @hosts.setter
    def hosts(self, value):
        self._hosts = value

    @property
    def port(self):
        return self._port

    @property
    def protocol(self):
        return self._protocol

    @property
    def root_ca(self):
        return self._root_ca

    @property
    def root_crl(self):
        return self._root_crl

    @port.setter
    def port(self, value):
        try:
            self._port = value
            config = self._config_lookup[self._port_lookup[value]['config']]
            self._auth = config['auth']
            self._cipher = config['cipher']
            self._root_ca = config['root_ca']
            self._root_crl = config['root_crl']
            self._protocol = self._port_lookup[value]['protocol']

        except StopIteration:
            logger.debug("%s not found in usable ports. Defaulting to %s" %
                         (value, self.default_port))
            self._port = self.default_port

    @property
    def default_port(self):
        return self._default_port

    @property
    def cipher(self):
        return self._cipher

    @property
    def auth(self):
        return self._auth

    @property
    def debug(self):
        return self._debug

    @debug.setter
    def debug(self, value):
        self._debug = value

    @property
    def conf_section(self):
        return self._conf_section

    @conf_section.setter
    def conf_section(self, value):
        self._conf_section = value

    @property
    def default_hosts_list(self):
        return self._default_hosts_list


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
                values = [v.strip() for v in value.split(',')]
                dicts = [{k: v} for k, v in [d.split(':') for d in values]]
                merged = {}
                for d in dicts:
                    for k, v in d.items():
                        merged.setdefault(k, []).append(v)
                self.__dict__[key] = merged
            elif value.find(',') > 0:
                # list
                self.__dict__[key] = [v.strip() for v in value.split(',')]
            else:
                self.__dict__[key] = [value.strip()]

    def __repr__(self):
        return '<%s %s:%s>' % (self.__class__.__name__, 'section', self.__dict__['section'])


def parse_conf_file():
    """Parses configure file 'pia.conf' using the Parser Class"""

    try:
        pia_section = _Parser("pia")
        props.conf_section['pia'] = pia_section

    except configparser.NoSectionError:
        pia_section = None
        logger.debug("Reading configuration file error. No %s" % 'pia')
        pass

    try:
        configure_section = _Parser("configure")
        props.conf_section['configure'] = configure_section
    except configparser.NoSectionError:
        configure_section = None
        logger.debug("Reading configuration file error. No %s" % 'configure')

    if pia_section:
        appstrategy.set_option(getattr(props, 'openvpn'), autologin=getattr(pia_section, "openvpn_auto_login", False))
        props.strong_encryption = getattr(pia_section, "strong_encryption", False)

    if configure_section:
        [appstrategy.set_option(getattr(props, app_name), configure=False)
         for app_name in appstrategy.get_supported_apps()
         if app_name not in getattr(configure_section, "apps", appstrategy.get_supported_apps())]

        appstrategy.set_option(getattr(props, "openvpn"), configure=True)

        props.hosts = getattr(configure_section, "hosts", "")
        props.port = getattr(configure_section, "port", [props.default_port])[0]


def reset_properties():
    props.strong_encryption = False
    props.port = props.default_port
    props.hosts = []


def get_default_hosts_list(names_only=False):
    all_remotes = []
    remote = namedtuple('Remote', 'name fqdn')
    for host in open(settings.PIA_HOST_LIST):
        h, d = host.replace('\n', '').split(',')
        if not names_only:
            all_remotes.append(remote(name=h, fqdn=d))
        else:
            all_remotes.append(h)

    return all_remotes


props = Props()  # creates global property object
