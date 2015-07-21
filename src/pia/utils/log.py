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
import logging
import sys
import logging.config
from pia.conf import settings

from pia.conf.properties import props


def configure_logging():
    if not sys.warnoptions:
        # Route warnings through python logging
        logging.captureWarnings(True)

    if settings.LOGGING:
        logging.config.dictConfig(settings.LOGGING)


class RequireDebugFalse(logging.Filter):
    def filter(self, record):
        return not props.debug


class RequireDebugTrue(logging.Filter):
    def filter(self, record):
        return props.debug
