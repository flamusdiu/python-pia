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
from pia.utils.misc import is_sequence

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
    _debug = ''
    _cert_modulus = ''
    _strong_encryption = ''
    _default_port = 'UDP/1198'
    _usable_ports = ['TCP/80', 'TCP/443', 'TCP/110', 'UDP/53', 'UDP/8080', 'UDP/9201']
    _usable_ciphers = ['aes-128-cbc', 'aes-256-cbc', 'bf-cbc', 'None']
    _usable_auth = ['sha1', 'sha256']
    _usable_cert_modulus = ['2048', '4096']
    _default_cipher = 'aes-128-cbc'
    _default_auth = 'sha1'
    _default_cert_modulus = '2048'

    def __init__(self):
        self.exclude_apps = None
        self.debug = settings.DEBUG
        self._login_config = settings.LOGIN_CONFIG
        self._conf_file = settings.PIA_CONFIG
        self.cipher = self.default_cipher
        self.port = self.default_port
        self.auth = self.default_auth
        self.cert_modulus = self.default_cert_modulus
        self._default_hosts_list = get_default_hosts_list()

    def __repr__(self):
        return '<%s %s:%s>' % (self.__class__.__name__, 'hosts', self._hosts)

    @property
    def default_cert_modulus(self):
        return self._default_cert_modulus

    @property
    def strong_encryption(self):
        return self._strong_encryption

    @strong_encryption.setter
    def strong_encryption(self, choice):
        if is_sequence(choice):
            choice = choice[0]

        if choice:
            self._port = 'UDP/1197'
            self.auth = 'sha256'
            self.cipher = 'aes-256-cbc'
            self.cert_modulus = '4096'
        else:
            self.port = self.default_port
            self.auth = self.default_auth
            self.cipher = self.default_cipher
            self.cert_modulus = self.default_cert_modulus

        self._strong_encryption = choice

    @property
    def usable_ports(self):
        return self._usable_ports

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

    @port.setter
    def port(self, value):
        if not self.strong_encryption:
            try:
                self._port = next(x for x in self._usable_ports if x.split('/')[1] == value)
            except StopIteration:
                logger.debug("%s not found in usable ports. Defaulting to %s" % (value, self._default_port))
                self._port = self._default_port

    @property
    def cert_modulus(self):
        return self._cert_modulus

    @cert_modulus.setter
    def cert_modulus(self, value):
        if not self.strong_encryption:
            try:
                self._cert_modulus = next(x for x in self._usable_cert_modulus if value == x)
            except StopIteration:
                logger.debug("%s not found in usable cert modulus. Defaulting to %s" %
                             (value, self._default_cert_modulus))
                self._cert_modulus = self._default_cert_modulus

    @property
    def usable_ciphers(self):
        return self._usable_ciphers

    @property
    def usable_auth(self):
        return self._usable_auth

    @property
    def cipher(self):
        return self._cipher

    @cipher.setter
    def cipher(self, value):
        if not self.strong_encryption:
            try:
                self._cipher = next(x for x in self._usable_ciphers if value == x)
            except StopIteration:
                logger.debug("%s not found in usable ciphers. Defaulting to %s" % (value, self._default_cipher))
                self._cipher = self._default_cipher

    @property
    def auth(self):
        return self._auth

    @auth.setter
    def auth(self, value):
        if not self.strong_encryption:
            try:
                self._auth = next(x for x in self._usable_auth if value == x)
            except StopIteration:
                logger.debug("%s not found in usable authentication methods. Defaulting to %s"
                             % (value, self._default_auth))
                self._auth = self._default_auth

    @property
    def default_port(self):
        return self._default_port

    @property
    def default_auth(self):
        return self._default_auth

    @property
    def default_cipher(self):
        return self._default_cipher

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
        props.cipher = getattr(configure_section, "cipher", [props.default_cipher])[0]
        props.auth = getattr(configure_section, "auth", [props.default_auth])[0]


def enable_strong_encryption():
    props.strong_encryption = True


def reset_properties():
    props.strong_encryption = False
    props.port = props.default_port
    props.auth = props.default_auth
    props.cipher = props.default_cipher
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
