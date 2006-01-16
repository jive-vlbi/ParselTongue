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

# Global AIPS defaults.
import AIPS

# AIPSTask implementation.
from AIPSTask import AIPSTask
from FITS import FITS

# Generic Task implementation.
from Task import Task, List

# Generic Python stuff.
import glob, os, pickle, sys

class ObitTask(AIPSTask):

    """This class implements running Obit tasks."""

    # Package.
    _package = 'Obit'

    # List of adverbs referring to disks.
    _disk_adverbs = ['inDisk', 'in2Disk', 'outDisk', 'out2Disk']

    # Default version.
    version = 'OBIT'

    # Default user number.
    userno = -1

    # Debugging?
    debug = False

    def __init__(self, name):
        AIPSTask.__init__(self, name)
        return

    def spawn(self):
        """Spawn the task."""

        if self.userno == 0:
            raise RuntimeError, "AIPS user number is not set"

        input_dict = {}
        for adverb in self._input_list:
            input_dict[adverb] = self._retype(self.__dict__[adverb])

        # Debugging?
        input_dict["DEBUG"] = self.debug

        # Figure out what proxy to use for running the task, and
        # translate the related disk numbers.
        url = None
        proxy = None
        for adverb in self._disk_adverbs:
            if adverb in input_dict:
                disk = int(input_dict[adverb])
                if disk == 0:
                    continue
                if not url and not proxy:
                    if self.__dict__['DataType'] == 'AIPS':
                        url = AIPS.disks[disk].url
                        proxy = AIPS.disks[disk].proxy()
                        if AIPS.disks[disk].url != url:
                            raise RuntimeError, \
                                  "AIPS disks are not on the same machine"
                        input_dict[adverb] = int(AIPS.disks[disk].disk)
                    elif self.__dict__['DataType'] == 'FITS':
                        url = FITS.disks[disk].url
                        proxy = FITS.disks[disk].proxy()
                        if FITS.disks[disk].url != url:
                            raise RuntimeError, \
                                  "FITS disks are not on the same machine"
                        input_dict[adverb] = int(FITS.disks[disk].disk)
        if not proxy:
            raise RuntimeError, \
                  "Unable to determine where to execute task"

        inst = getattr(proxy, self.__class__.__name__)
        tid = inst.spawn(self._name, self.version, self.userno,
                         self.msgkill, self.isbatch, input_dict)

        self._message_list = []
        return (proxy, tid)

    def messages(self, proxy=None, tid=None):
        """Return messages for the task specified by PROXY and TID."""

        if not proxy and not tid:
            return self._message_list

        inst = getattr(proxy, self.__class__.__name__)
        messages = inst.messages(tid)
        if not messages:
            return None
        self._message_list.extend(messages)
        return messages

    def go(self):
        """Run the task."""

        (proxy, tid) = self.spawn()
        log = []
        count = 0
        rotator = ['|\b', '/\b', '-\b', '\\\b']
        while not self.finished(proxy, tid):
            messages = self.messages(proxy, tid)
            if messages:
                log.extend(messages)
            elif sys.stdout.isatty():
                sys.stdout.write(rotator[count % 4])
                sys.stdout.flush()
                pass
            count += 1
            continue
        self.wait(proxy, tid)
        return


# Tests.
if __name__ == '__main__':
    import doctest, sys
    doctest.testmod(sys.modules[__name__])
