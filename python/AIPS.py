# Copyright (C) 2005 Joint Institute for VLBI in Europe
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""

This module provides the AIPSDisk class and serves as a container for
several AIPS-related defaults.  It provides some basic infrastructure
used by the AIPSTask and AIPSData modules.

"""

# Generic Python stuff.
import os, sys

# Generic AIPS functionality.
from AIPSUtil import ehex

# Debug log.  Define before including proxies.
debuglog = None

# Available proxies.
import LocalProxy
from xmlrpclib import ServerProxy


class AIPSDisk:
    
    """Class representing a (possibly remote) AIPS disk.  An instance
       of this class stores an AIPS disk number and the URL of the
       proxy through which it can be accessed.  For local AIPS disks
       the URL will be None."""

    def __init__(self, url, disk):
        self.url = url
        self.disk = disk
        return

    def proxy(self):
        """Return the proxy through which this AIPS disk can be
           accessed."""
        if self.url:
            return ServerProxy(self.url, allow_none=True)
        return LocalProxy

    pass                                # class AIPSDisk


# Default AIPS user ID.
userno = 0

# List of available proxies.
proxies = [ LocalProxy ]

# AIPS disk mapping. 
disks = [ None ]                        # Disk numbers are one-based.

# AIPS seems to support a maximum of 35 disks.
for disk in xrange(1, 36):
    area = 'DA' + ehex(disk, 2, '0')
    if not area in os.environ:
        break
    disks.append(AIPSDisk(None, disk))
    continue

# Message log.
log = None


# The code below is the result of a serious design flaw.  It should
# really die, but removing it will probably affect most scripts.

class _AIPS(object):
    
    """Backwards compatibility gunk."""

    def _get_userno(self):
        return sys.modules[__name__].userno
    def _set_userno(self, value):
        sys.modules[__name__].userno = value
    userno = property(_get_userno, _set_userno)

    def _get_disks(self):
        return sys.modules[__name__].disks
    def _set_disks(self, value):
        sys.modules[__name__].disks = value
    disks = property(_get_disks, _set_disks)

    def _get_log(self):
        return sys.modules[__name__].log
    def _set_log(self, value):
        sys.modules[__name__].log = value
    log = property(_get_log, _set_log)

    def _get_debuglog(self):
        return sys.modules[__name__].debuglog
    def _set_debuglog(self, value):
        sys.modules[__name__].debuglog = value
    debuglog = property(_get_debuglog, _set_debuglog)

    pass                                # class _AIPS

AIPS = _AIPS()
