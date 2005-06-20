# Copyright (C) 2005 Joint Institute for VLBI in Europe
# Copyright (C) 2005 Associated Universities, Inc. Washington DC, USA.
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

This module provides the ObitTask class.  It adapts the Task class from
the Task module to be able to run Obit tasks:

>>> imean = ObitTask('Template')

The resulting class instance has all associated adverbs as attributes:

>>> print imean.ind
0.0
>>> imean.ind = 1
>>> print imean.indisk
1.0
>>> imean.indi = 2.0
>>> print imean.ind
2.0

It also knows the range for these attributes:

>>> imean.ind = -1
Traceback (most recent call last):
  ...
ValueError: value '-1.0' is out of range for attribute 'indisk'
>>> imean.ind = 10.0
Traceback (most recent call last):
  ...
ValueError: value '10.0' is out of range for attribute 'indisk'

>>> imean.inc = 'UVDATA'

>>> print imean.inclass
UVDATA

"""

# AIPSTask implementation.
from AIPSTask import AIPSTask
from AIPS import AIPS
from FITS import FITS

# Generic Python stuff.
import glob, os, pickle, sys

class ObitTask(AIPSTask):

    """This class implements running Obit tasks."""

    # Package.
    _package = 'Obit'

    # List of adverbs referring to disks.
    _disk_adverbs = ['inDisk', in2Disk', 'outDisk', 'out2Disk']

    # Default version.
    version = 'OBIT'

    def __init__(self, name):
        AIPSTask.__init__(self, name)
        if self.userno == 0:
            self.userno = 1

    def go(self):
        """Run the task."""

        (proxy, tid) = self.spawn()
        log = []
        count = 0
        rotator = ['|\b', '/\b', '-\b', '\\\b']
        while not self.finished(proxy, tid):
            messages = self.messages(proxy, tid)
            if messages:
                for message in messages:
                    log.append(message)
                    print message
                    continue
                pass
            elif sys.stdout.isatty():
                sys.stdout.write(rotator[count % 4])
                sys.stdout.flush()
                pass
            count += 1
            continue
        self.wait(proxy, tid)
        return log


# Tests.
if __name__ == '__main__':
    import doctest, sys
    doctest.testmod(sys.modules[__name__])
