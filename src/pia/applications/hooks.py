import glob
import os
import pathlib
import warnings
import re

from uuid import uuid4
from collections import namedtuple
from pia.conf import settings, properties
from pia.utils.misc import get_login_credentials
from pia.applications.appstrategy import StrategicAlternative


class ApplicationStrategyOPENVPN(StrategicAlternative):
    """Strategy file for OpenVPN

    OpenVPN's strategy class is always created. It has extra functions then other
    strategic classes.

    Attributes:
        command_bin: list containing which files to check if the application is installed
        conf_dir: directory to the application stores it's configurations
        configs: the list of openVPN configurations to modify
    """
    _COMMAND_BIN = ['/usr/bin/openvpn']
    _CONF_DIR = '/etc/openvpn'

    @property
    def configs(self):
        return self._configs

    @configs.setter
    def configs(self, configs):
        """the list of openVPN configurations to modify"""
        self._configs = configs

    def __init__(self):
        super().__init__('openvpn')
        self._configs = self._get_configs()

    def config(self, config_id, filename):
        """Configures configuration file for the given strategy.

        Args:
            config_id: the name of the profile (i.e. "US East") used as the name of the VPN endpoint
            filename: the filename of where to store the finished configuration file
            enable: allows auto-login in openVPN configs

        Raises:
            OSError: problems with reading or writing configuration files
        """
        p = pathlib.Path(filename)
        content = ''

        try:
            with p.open() as f:
                content = f.read()
        except IOError:
            warnings.warn('Cannot access %s.' % config_id)

        content = re.sub(r'(auth-user-pass)(?:.*)', '\g<1> ' + settings.LOGIN_CONFIG, content)
        content = re.sub(r'(remote\s.*\.privateinternetaccess\.com\s)(?:\d+)', '\g<1>' + properties.props.port, content)

        # content = re.sub('(auth-user-pass)(?:.*)', 'auth-user-pass', content)

        try:
            with open(filename, "w") as f:
                f.write(content)
        except IOError:
            warnings.warn('Cannot access %s.' % config_id)

    def _get_configs(self):
        """Gets the list of configuration files to be modified"""

        config = namedtuple('Config', 'name, conf')
        for filename in glob.glob(self.conf_dir + '/*.conf'):
            c = {'name': re.sub('_', ' ', re.match(r"^/(.*/)*(.+)\.conf$", filename).group(2)),
                 'conf': filename}
            var_name = re.sub(' ', '_', re.match(r"^/(.*/)*(.+)\.conf$", filename).group(2))
            self.__dict__[var_name] = config(**c)

        return [i for i, j in self.__dict__.items() if type(self.__dict__[i]).__name__ == 'Config']

    def find_config(self, config_id):
        """Not implemented for OpenVPN. No need to search for a configuration."""
        raise NotImplementedError('%s does not implement find_config()!' % self.__module__.__name__)

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
            warnings.warn('Cannot read %s to get remove address!' % config)
            return None

        return ''.join(re.findall("(?:remote.)(.*)(?:.\d{4})", contents))


class ApplicationStrategyNM(StrategicAlternative):
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
        username, password = get_login_credentials(settings.LOGIN_CONFIG)

        # Directory of replacement values for NetworkManager's configuration files
        re_dict = {"##username##": username,
                   "##password##": password,
                   "##id##": config_id,
                   "##uuid##": str(uuid4()),
                   "##remote##": ApplicationStrategyOPENVPN.get_remote_address(filename),
                   "##port##": properties.props.port}

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


class ApplicationStrategyCM(StrategicAlternative):
    """Strategy file for Connman

    Attributes:
        command_bin: list containing which files to check if the application is installed
        conf_dir: directory to the application stores it's configurations
    """
    _CONF_DIR = '/var/lib/connman-vpn'
    _COMMAND_BIN = ['/usr/bin/connmanctl']

    def __init__(self):
        super().__init__('cm')

    def config(self, config_id, filename):
        """Configures configuration file for the given strategy.

        Args:
            config_id: the name of the profile (i.e. "US East") used as the name of the VPN endpoint
            filename: the filename of where to store the finished configuration file
            enable: NOT USED

        """

        # Directory of replacement values for connman's configuration files
        re_dict = {"##id##": config_id,
                   "##filename##": filename,
                   "##remote##": ApplicationStrategyOPENVPN.get_remote_address(filename),
                   "##port##": properties.props.port}

        # Complete path of configuration file
        conf = self.conf_dir + "/" + re.sub(' ', '_', config_id) + ".config"

        # Modifies configuration file
        self.update_config(re_dict, conf)

    def find_config(self, config_id):
        """Find if a configuration is configured

        Args:
            config_id: configuration name

        Returns:
            Returns bool depending on if the configuration is already installed

        """
        conf = self.conf_dir + "/" + re.sub(' ', '_', config_id) + ".config"

        return os.access(conf, os.F_OK)
