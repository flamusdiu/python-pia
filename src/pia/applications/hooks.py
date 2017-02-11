import logging
import os
import re

from uuid import uuid4
from pia.conf import settings, properties
from pia.utils.misc import get_login_credentials
from pia.applications.appstrategy import StrategicAlternative

logger = logging.getLogger(__name__)


class ApplicationStrategyOPENVPN(StrategicAlternative):
    """Strategy file for OpenVPN

    OpenVPN's strategy class is always created. It has extra functions then other
    strategic classes.

    Attributes:
        @command_bin: list containing which files to check if the application is installed
        @conf_dir: directory to the application stores it's configurations
        @configs: the list of openVPN configurations to modify
    """
    _COMMAND_BIN = ['/usr/bin/openvpn']
    _CONF_DIR = '/etc/openvpn/client'
    _configs = []

    @property
    def configs(self):
        return self._configs

    @configs.setter
    def configs(self, configs):
        """the list of openVPN configurations to modify"""
        self._configs = configs

    def __init__(self):
        super().__init__('openvpn')

    def config(self, config_id):
        """Configures configuration file for the given strategy.

        Args:
            config_id: the name of the profile (i.e. "US East") used as the name of the VPN endpoint

        Raises:
            OSError: problems with reading or writing configuration files
        """

        # Directory of replacement values for OpenVPN's configuration files
        re_dict = {'##port##': properties.props.port,
                   '##cipher##': properties.props.cipher,
                   '##proto##': properties.props.protocol.lower(),
                   '##root_ca##': properties.props.root_ca,
                   '##root_crl##': properties.props.root_crl,
                   '##login_config##': properties.settings.LOGIN_CONFIG,
                   '##remote##': self.get_remote_address(config_id),
                   '##auth##': properties.props.auth}

        # Complete path of configuration file
        conf = self.conf_dir + '/' + re.sub(' ', '_', config_id) + '.conf'

        # Modifies configuration file
        self.update_config(re_dict, conf)

    def find_config(self, config_id):
        """Find if a configuration is configured

        Args:
            config_id: configuration name

        Returns:
            Returns bool depending on if the configuration is already installed

        """
        conf = self.conf_dir + "/" + re.sub(' ', '_', config_id) + '.conf'

        return os.access(conf, os.F_OK)

    @staticmethod
    def get_remote_address(config_id):
        """Finds the remote server host/ip address
        """

        return [h.fqdn for h in properties.get_default_hosts_list() if h.name == re.sub('_', ' ', config_id)][0]


class ApplicationStrategyNM(StrategicAlternative):
    """Strategy file for NetworkManager.

    Attributes:
        @command_bin: list containing which files to check if the application is installed
        @conf_dir: directory to the application stores it's configurations
    """
    _CONF_DIR = '/etc/NetworkManager/system-connections'
    _COMMAND_BIN = ['/usr/bin/nmcli', '/usr/lib/NetworkManager/nm-openvpn-service']

    def __init__(self):
        super().__init__('nm')

    def config(self, config_id):
        """Configures configuration file for the given strategy.

        NetworkManager requires VPN credentials in its configuration files. So, those are
        pulled in using Props.get_login_credentials() classmethod.

        Args:
            config_id: the name of the profile (i.e. "US East") used as the name of the VPN endpoint
        """

        # Gets VPN username and password

        username, password = get_login_credentials(settings.LOGIN_CONFIG)

        # Directory of replacement values for NetworkManager's configuration files
        re_dict = {'##username##': username,
                   '##password##': password,
                   '##id##': config_id,
                   '##uuid##': str(uuid4()),
                   '##remote##': ApplicationStrategyOPENVPN.get_remote_address(config_id),
                   '##port##': properties.props.port,
                   '##cipher##': properties.props.cipher.upper(),
                   '##use_tcp##': "yes" if properties.props.protocol.upper() == 'TCP' else 'no',
                   '##root_ca##': properties.props.root_ca,
                   '##auth##': properties.props.auth.upper()}

        # Complete path of configuration file
        conf = self.conf_dir + '/' + re.sub(' ', '_', config_id)

        # Modifies configuration file
        self.update_config(re_dict, conf)

    def find_config(self, config_id):
        """Find if a configuration is configured

        Args:
            config_id: configuration name

        Returns:
            Returns bool depending on if the configuration is already installed
        """
        conf = self.conf_dir + "/" + re.sub(' ', '_', config_id)

        return os.access(conf, os.F_OK)


class ApplicationStrategyCM(StrategicAlternative):
    """Strategy file for Connman

    Attributes:
        @command_bin: list containing which files to check if the application is installed
        @conf_dir: directory to the application stores it's configurations
    """
    _CONF_DIR = '/var/lib/connman-vpn'
    _COMMAND_BIN = ['/usr/bin/connmanctl']

    def __init__(self):
        super().__init__('cm')

    def config(self, config_id):
        """Configures configuration file for the given strategy.

        Args:
            config_id: the name of the profile (i.e. "US East") used as the name of the VPN endpoint

        """

        # Directory of replacement values for connman's configuration files
        re_dict = {'##id##': config_id,
                   '##filename##': properties.appstrategy.get_app('openvpn').app.conf_dir + '/' +
                                   re.sub(' ', '_', config_id) + '.conf',
                   '##remote##': ApplicationStrategyOPENVPN.get_remote_address(config_id),
                   '##port##': properties.props.port,
                   '##cipher##': properties.props.cipher,
                   '##auth##': properties.props.auth,
                   '##root_ca##': properties.props.root_ca}

        # Complete path of configuration file
        conf = self.conf_dir + '/' + re.sub(' ', '_', config_id) + '.config'

        # Modifies configuration file
        self.update_config(re_dict, conf)

    def find_config(self, config_id):
        """Find if a configuration is configured

        Args:
            config_id: configuration name

        Returns:
            Returns bool depending on if the configuration is already installed

        """
        conf = self.conf_dir + "/" + re.sub(' ', '_', config_id) + '.config'

        return os.access(conf, os.F_OK)
