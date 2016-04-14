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
import os
import re
import stat
import pathlib
import logging

logger = logging.getLogger(__name__)


def has_proper_permissions(filepath):
    """Checks of file has 0600 permission and owned by root"""
    st = os.stat(filepath)

    return bool(st.st_uid == 0 & st.st_gid == 0 & int(oct(stat.S_IMODE(os.stat(filepath).st_mode)) == "0o600"))


def multiple_replace(dictionary, text):
    """Replaces keys on a single pass

    Returns:
        The modified text is returns on a single pass of the regular express.
    """
    # Create a regular expression  from the dictionary keys
    regex = re.compile("(%s)" % "|".join(map(re.escape, dictionary.keys())))

    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: dictionary[mo.string[mo.start():mo.end()]], text)


def get_login_credentials(login_config):
    """Loads login credentials from file

    Returns:
        A list containing username and password for login service.
    """
    try:
        if not has_proper_permissions(login_config):
            logger.error('%s must be owned by root and not world readable!' % login_config)
            exit(1)
    except OSError:
        logger.error('%s is missing! Auto-configuration failed!' % login_config)
        exit(1)

    p = pathlib.Path(login_config)
    try:
        # Opens login.conf and reads login and passwords from file
        with p.open() as f:
            content = f.read().splitlines()

        return list(filter(bool, content))
    except OSError:
        logger.error('%s is missing! Auto-configuration failed!' % login_config)
        exit(1)
