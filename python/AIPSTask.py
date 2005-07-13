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

This module provides the AIPSTask class.  It adapts the Task class from
the Task module to be able to run classic AIPS tasks:

>>> imean = AIPSTask('imean')

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

>>> imean.blc[1:] = [128, 128]
>>> print imean.blc
[None, 128.0, 128.0, 0.0, 0.0, 0.0, 0.0, 0.0]

>>> imean.blc = AIPSList([256, 256])
>>> print imean.blc
[None, 256.0, 256.0, 0.0, 0.0, 0.0, 0.0, 0.0]

It doesn't hurt to apply AIPSList to a scalar:
>>> AIPSList(1)
1

And it works on matrices (lists of lists) too:
>>> AIPSList([[1,2],[3,4],[5,6]])
[None, [None, 1, 2], [None, 3, 4], [None, 5, 6]]

It should also work for strings:
>>> AIPSList('foobar')
'foobar'
>>> AIPSList(['foo', 'bar'])
[None, 'foo', 'bar']
"""

# Global AIPS defaults.
from AIPS import AIPS

# Generic Task implementation.
from Task import Task, List

# Generic Python stuff.
import glob, os, pickle, sys


class AIPSTask(Task):

    """This class implements running AIPS tasks."""

    # Package.
    _package = 'AIPS'

    # List of adverbs referring to disks.
    _disk_adverbs = ['indisk', 'outdisk',
                     'in2disk', 'in3disk', 'in4disk', 'out2disk']

    # Default version.
    version = os.environ.get('VERSION', 'NEW')

    # Default user number.
    userno = 0

    # Default verbosity level.
    msgkill = 0

    # Default to batch mode.
    isbatch = 32000

    def __init__(self, name, **kwds):
        Task.__init__(self)
        self._name = name
        self._input_list = []
        self._output_list = []
        self._message_list = []

        # Optional arguments.
        if 'version' in kwds:
            self.version = kwds['version']

        # Update default user number.
        if self.__class__.userno == 0:
            self.__class__.userno = AIPS.userno

        # See if there is a proxy that can hand us the details for
        # this task.
        params = None
        for proxy in AIPS.proxies:
            try:
                inst = getattr(proxy, self.__class__.__name__)
                params = inst.params(name, self.version)
            except:
                continue
            break
        if not params:
            msg = "%s task '%s' is not available" % (self._package, name)
            raise RuntimeError, msg

        # The XML-RPC proxy will return the details as a dictionary,
        # not a class.
        self._default_dict = params['default_dict']
        self._input_list = params['input_list']
        self._output_list = params['output_list']
        self._min_dict = params['min_dict']
        self._max_dict = params['max_dict']
        self._strlen_dict = params['strlen_dict']
        self._help_string = params['help_string']
        for adverb in self._default_dict:
            if type(self._default_dict[adverb]) == list:
                value = self._default_dict[adverb]
                self._default_dict[adverb] = List(self, adverb, value)

        # Initialize all adverbs to their default values.
        self.__dict__.update(self._default_dict)

    def defaults(self):
        """Set adverbs to their defaults."""
        self.__dict__.update(self._default_dict)

    def __display_adverbs(self, adverbs):
        """Display ADVERBS."""

        for adverb in adverbs:
            if self.__dict__[adverb] == '':
                print "'%s': ''" % adverb
            else:
                value = PythonList(self.__dict__[adverb])
                print "'%s': %s" % (adverb, value)

    def inputs(self):
        """Display all inputs for this task."""
        self.__display_adverbs(self._input_list)

    def outputs(self):
        """Display all outputs for this task."""
        self.__display_adverbs(self._output_list)

    def _retype(self, value):
        """ Recursively transform a 'List' into a 'list' """

        if type(value) == List:
            value = list(value)
            for i in range(1, len(value)):
                value[i] = self._retype(value[i])

        return value

    def spawn(self):
        """Spawn the task."""

        if self.userno == 0:
            raise RuntimeError, "AIPS user number is not set"

        input_dict = {}
        for adverb in self._input_list:
            input_dict[adverb] = self._retype(self.__dict__[adverb])

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
                    url = AIPS.disks[disk].url
                    proxy = AIPS.disks[disk].proxy()
                if AIPS.disks[disk].url != url:
                    raise RuntimeError, \
                          "AIPS disks are not on the same machine"
                input_dict[adverb] = float(AIPS.disks[disk].disk)
        if not proxy:
            raise RuntimeError, \
                  "Unable to determine where to execute task"

        inst = getattr(proxy, self.__class__.__name__)
        tid = inst.spawn(self._name, self.version, self.userno,
                         self.msgkill, self.isbatch, input_dict)

        self._message_list = []
        return (proxy, tid)

    def finished(self, proxy, tid):
        """Determine whether the task specified by PROXY and TID has
        finished."""

        inst = getattr(proxy, self.__class__.__name__)
        return inst.finished(tid)

    def messages(self, proxy=None, tid=None):
        """Return messages for the task specified by PROXY and TID."""

        if not proxy and not tid:
            return self._message_list

        inst = getattr(proxy, self.__class__.__name__)
        messages = inst.messages(tid)
        if not messages:
            return None
        for message in messages:
            self._message_list.append(message[1])
            if message[0] > abs(self.msgkill):
                print message[1]
                pass
            continue
        return [message[1] for message in messages]

    def wait(self, proxy, tid):
        """Wait for the task specified by PROXY and TID to finish."""

        while not self.finished(proxy, tid):
            self.messages(proxy, tid)
        inst = getattr(proxy, self.__class__.__name__)
        output_dict = inst.wait(tid)
        for adverb in self._output_list:
            self.__dict__[adverb] = output_dict[adverb]

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
        if AIPS.log:
            for message in log:
                AIPS.log.write('%s\n' % message)
        return

    def __call__(self):
        return self.go()

    def __setattr__(self, name, value):
        data_adverbs = ['indata', 'outdata',
                        'in2data', 'in3data', 'in4data', 'out2data']
        if name in data_adverbs:
            prefix = name.replace('data', '')
            Task.__setattr__(self, prefix + 'name', value.name)
            Task.__setattr__(self, prefix + 'class', value.klass)
            Task.__setattr__(self, prefix + 'disk', value.disk)
            Task.__setattr__(self, prefix + 'seq', value.seq)
        else:
            # We treat 'infile', 'outfile' and 'outprint' special.
            # Instead of checking the length of the complete string,
            # we only check the length of the final component of the
            # pathname.  The backend will split of the direcrory
            # component and use that as an "area".
            attr = self._findattr(name)
            file_adverbs = ['infile', 'outfile', 'outprint']
            if attr in file_adverbs and type(value) == str and \
                   os.path.dirname(value):
                if len(os.path.basename(value)) > self._strlen_dict[attr] - 2:
                    msg = "string '%s' is too long for attribute '%s'" \
                          % (value, attr)
                    raise ValueError, msg
                self.__dict__[attr] = value
            else:
                Task.__setattr__(self, name, value)


def AIPSList(list):
    """Transform a Python array into an AIPS array.

    Returns a list suitable for using 1-based indices.
    """

    try:
        # Make sure we don't consider strings to be lists.
        if str(list) == list:
            return list
    except:
        pass

    try:
        # Insert 'None' at index zero, and transform LIST's elements.
        _list = [None]
        for l in list:
            _list.append(AIPSList(l))
            continue
        return _list
    except:
        # Apparently LIST isn't a list; simply return it unchanged.
        return list

def PythonList(list):
    """Transform an AIPS array into a Python array.

    Returns a list suitable for using normal 0-based indices.
    """

    try:
        if list[0] != None:
            return list

        _list = []
        for l in list[1:]:
            _list.append(PythonList(l))
            continue
        return _list
    except:
        # Apparently LIST isn't a list; simply return it unchanged.
        return list


# Tests.
if __name__ == '__main__':
    import doctest, sys
    doctest.testmod(sys.modules[__name__])
