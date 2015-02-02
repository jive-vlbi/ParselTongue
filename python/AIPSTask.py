# Copyright (C) 2005, 2006 Joint Institute for VLBI in Europe
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


# This module provides the AIPSTask class.  It adapts the Task class from
# the Task module to be able to run classic AIPS tasks:
# 
# >>> imean = AIPSTask('imean')
# 
# The resulting class instance has all associated adverbs as attributes:
# 
# >>> print imean.ind
# 0.0
# >>> imean.ind = 1
# >>> print imean.indisk
# 1.0
# >>> imean.indi = 2.0
# >>> print imean.ind
# 2.0
# 
# It also knows the range for these attributes:
# 
# >>> imean.ind = -1
# Traceback (most recent call last):
#   ...
# ValueError: value '-1.0' is out of range for attribute 'indisk'
# >>> imean.ind = 10.0
# Traceback (most recent call last):
#   ...
# ValueError: value '10.0' is out of range for attribute 'indisk'
# 
# >>> imean.inc = 'UVDATA'
# 
# >>> print imean.inclass
# UVDATA
# 
# >>> imean.blc[1:] = [128, 128]
# >>> print imean.blc
# [None, 128.0, 128.0, 0.0, 0.0, 0.0, 0.0, 0.0]
# 
# >>> imean.blc = AIPSList([256, 256])
# >>> print imean.blc
# [None, 256.0, 256.0, 0.0, 0.0, 0.0, 0.0, 0.0]
# 
# It doesn't hurt to apply AIPSList to a scalar:
# >>> AIPSList(1)
# 1
# 
# And it works on matrices (lists of lists) too:
# >>> AIPSList([[1,2],[3,4],[5,6]])
# [None, [None, 1, 2], [None, 3, 4], [None, 5, 6]]
# 
# It should also work for strings:
# >>> AIPSList('foobar')
# 'foobar'
# >>> AIPSList(['foo', 'bar'])
# [None, 'foo', 'bar']
# 
# The AIPSTask class implements the copy method:
# 
# >>> imean2 = imean.copy()
# >>> print imean2.inclass
# UVDATA
# >>> imean2.inclass = 'SPLIT'
# >>> print imean.inclass
# UVDATA
# 
# It also implements the == operator, which checks whether task name and
# inputs match:
# 
# >>> imean2 == imean
# False
# >>> imean2.inclass = 'UVDATA'
# >>> imean2 == imean
# True
# 
# Make sure we handle multi-dimensional arrays correctly:
# 
# >>> sad = AIPSTask('sad')
# >>> sad.dowidth[1][1:] = [2, 2, 2]
# >>> sad.dowidth[1]
# [None, 2.0, 2.0, 2.0]
# >>> sad.dowidth[2]
# [None, 1.0, 1.0, 1.0]


# Global AIPS defaults.
import AIPS, AIPSTV

# Generic Task implementation.
from Task import Task, List

# Default proxy.
import LocalProxy

# Generic Python stuff.
import copy, fcntl, glob, os, pickle, pydoc, select, signal, sys


class AIPSTask(Task):

    """This class implements running AIPS tasks."""

    # Package.
    _package = 'AIPS'

    # List of adverbs referring to data.
    _data_adverbs = ['indata', 'outdata',
                     'in2data', 'in3data', 'in4data', 'out2data']

    # List of adverbs referring to disks.
    _disk_adverbs = ['indisk', 'outdisk',
                     'in2disk', 'in3disk', 'in4disk', 'out2disk']

    # List of adverbs referring to file names.
    # some new for 31DEC08
    # O.W.  07 Nov 2008
    _file_adverbs = ['infile', 'infile2', 'outfile', 'outprint',
                     'ofmfile', 'boxfile', 'oboxfile',
                     'intext', 'outtext', 'datain', 'dataout', 'calin',
                     'inlist', 'data2in'
                     ]

    # List of adverbs referring to channels.
    _chan_adverbs = ['bchan', 'echan', 'chansel', 'channel']

    # List of adverbs referring to image dimensions.
    _box_adverbs = ['blc', 'trc', 'tblc', 'ttrc', 'pixxy', 'imsize', 'box',
                    'clbox', 'fldsize', 'pix2xy', 'uvsize']

    # Default version.
    version = os.environ.get('VERSION', 'NEW')

    # Default user number.
    userno = -1

    # Default verbosity level.
    msgkill = 0

    # Default to batch mode.
    isbatch = 32000

    # Default tv
    tv = AIPSTV.AIPSTV()

    # This should be set to a file object...
    log = open("/dev/null", 'a')

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
        if self.userno == -1:
            self.userno = AIPS.userno

        # See if there is a proxy that can hand us the details for
        # this task.
        params = None
        for proxy in AIPS.proxies:
            try:
                inst = getattr(proxy, self.__class__.__name__)
                params = inst.params(name, self.version)
            except Exception, exception:
                if AIPS.debuglog:
                    print >>AIPS.debuglog, exception
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
        self._explain_string = params['explain_string']
        for adverb in self._default_dict:
            if type(self._default_dict[adverb]) == list:
                value = self._default_dict[adverb]
                self._default_dict[adverb] = List(self, adverb, value)

        # Initialize all adverbs to their default values.
        self.defaults()

        # The maximum value for disk numbers is system-dependent.
        for name in self._disk_adverbs:
            if name in self._max_dict:
                self._max_dict[name] = float(len(AIPS.disks) - 1)
                pass
            continue

        # The maximum channel is system-dependent.
        for name in self._chan_adverbs:
            if name in self._max_dict:
                # Assume the default
                self._max_dict[name] = 16384.0
                pass
            continue

        # The maximum image size is system-dependent.
        for name in self._box_adverbs:
            if name in self._max_dict:
                # Assume the default
                self._max_dict[name] = 32768.0
                pass
            continue

        return                          # __init__

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        if self._name != other._name:
            return False
        if self.userno != other.userno:
            return False
        for adverb in self._input_list:
            if self.__dict__[adverb] != other.__dict__[adverb]:
                return False
            continue
        return True

    def copy(self):
        task = AIPSTask(self._name, version=self.version)
        task.userno = self.userno
        for adverb in self._input_list:
            task.__dict__[adverb] = self.__dict__[adverb]
            continue
        return task

    def defaults(self):
        """Set adverbs to their defaults."""
        for attr in self._default_dict:
            self.__dict__[attr] = copy.copy(self._default_dict[attr])
            continue
        return

    def __display_adverbs(self, adverbs):
        """Display ADVERBS."""

        for adverb in adverbs:
            if self.__dict__[adverb] == '':
                print "'%s': ''" % adverb
            else:
                value = PythonList(self.__dict__[adverb])
                print "'%s': %s" % (adverb, value)
                pass
            continue

        return

    def explain(self):
        """Display more help for this task."""

        if self._explain_string:
            pydoc.pager(self._help_string +
                        64 * '-' + '\n' +
                        self._explain_string)
            pass

        return

    def inputs(self):
        """Display all inputs for this task."""
        self.__display_adverbs(self._input_list)
        return

    def outputs(self):
        """Display all outputs for this task."""
        self.__display_adverbs(self._output_list)
        return

    def _retype(self, value):
        """ Recursively transform a 'List' into a 'list' """

        if type(value) == List:
            value = list(value)
            for i in range(1, len(value)):
                value[i] = self._retype(value[i])
                continue
            pass

        return value

    def spawn(self):
        """Spawn the task."""

        if self.userno == -1:
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
                    proxy.__nonzero__ = lambda: True
                    pass
                if AIPS.disks[disk].url != url:
                    raise RuntimeError, \
                          "AIPS disks are not on the same machine"
                input_dict[adverb] = float(AIPS.disks[disk].disk)
                pass
            continue
        if not proxy:
            proxy = LocalProxy
            proxy.__nonzero__ = lambda: True
            for adverb in self._disk_adverbs:
                if adverb in input_dict:
                    proxy = None
                    break
                continue
            pass
        if not proxy:
            raise RuntimeError, \
                  "Unable to determine where to execute task"

        inst = getattr(proxy, self.__class__.__name__)
        tid = inst.spawn(self._name, self.version, self.userno, self.msgkill,
                         self.isbatch, str(self.tv), input_dict)

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

    def feed(self, proxy, tid, banana):
        """Feed the task specified by PROXY and TID with BANANA."""

        inst = getattr(proxy, self.__class__.__name__)
        return inst.feed(tid, banana)

    def wait(self, proxy, tid):
        """Wait for the task specified by PROXY and TID to finish."""

        while not self.finished(proxy, tid):
            self.messages(proxy, tid)
        inst = getattr(proxy, self.__class__.__name__)
        output_dict = inst.wait(tid)
        for adverb in self._output_list:
            self.__dict__[adverb] = output_dict[adverb]
            continue
        return

    def abort(self, proxy, tid, sig=signal.SIGTERM):
        """Abort the task specified by PROXY and TID."""

        inst = getattr(proxy, self.__class__.__name__)
        return inst.abort(tid, sig)

    def go(self):
        """Run the task."""

        (proxy, tid) = self.spawn()
        loglist = []
        count = 0
        rotator = ['|\b', '/\b', '-\b', '\\\b']
        try:
            try:
                while not self.finished(proxy, tid):
                    messages = self.messages(proxy, tid)
                    if messages:
                        loglist.extend(messages)
                    elif sys.stdout.isatty() and len(rotator) > 0:
                        sys.stdout.write(rotator[count % len(rotator)])
                        sys.stdout.flush()
                        pass
                    events = select.select([sys.stdin.fileno()], [], [], 0)
                    if sys.stdin.fileno() in events[0]:
                        flags = fcntl.fcntl(sys.stdin.fileno(), fcntl.F_GETFL)
                        flags |= os.O_NONBLOCK
                        fcntl.fcntl(sys.stdin.fileno(), fcntl.F_SETFL, flags)
                        message = sys.stdin.read(1024)
                        flags &= ~os.O_NONBLOCK
                        fcntl.fcntl(sys.stdin.fileno(), fcntl.F_SETFL, flags)
                        if message:
                            self.feed(proxy, tid, message)
                        rotator = []
                        pass
                    count += 1
                    continue
                pass
            except KeyboardInterrupt, exception:
                self.abort(proxy, tid)
                raise exception

            self.wait(proxy, tid)
        finally:
                    if self.log:
                        for message in loglist:
                            self.log.write('%s\n' % message)
                            continue
                        self.log.flush()
                        pass
		    if AIPS.log:
                        for message in loglist:
                            AIPS.log.write('%s\n' % message)
                            continue
                        AIPS.log.flush()
                        pass
                    pass
        return

    def __call__(self):
        return self.go()

    def __getattr__(self, name):
        if name in self._data_adverbs:
            class _AIPSData: pass
            value = _AIPSData()
            prefix = name.replace('data', '')
            value.name = Task.__getattr__(self, prefix + 'name')
            value.klass = Task.__getattr__(self, prefix + 'class')
            value.disk = Task.__getattr__(self, prefix + 'disk')
            value.seq = Task.__getattr__(self, prefix + 'seq')
            return value
        return Task.__getattr__(self, name)

    def __setattr__(self, name, value):
        if name in self._data_adverbs:
            prefix = name.replace('data', '')
            Task.__setattr__(self, prefix + 'name', value.name)
            Task.__setattr__(self, prefix + 'class', value.klass)
            Task.__setattr__(self, prefix + 'disk', value.disk)
            Task.__setattr__(self, prefix + 'seq', value.seq)
        elif name == 'intable':
            Task.__setattr__(self, 'inext', value.name)
            Task.__setattr__(self, 'invers', value.version)
        else:
            # We treat 'infile', 'outfile' and 'outprint' special.
            # Instead of checking the length of the complete string,
            # we only check the length of the final component of the
            # pathname.  The backend will split of the direcrory
            # component and use that as an "area".
            attr = self._findattr(name)
            if attr in self._file_adverbs and type(value) == str and \
                   os.path.dirname(value):
                if len(os.path.basename(value)) > self._strlen_dict[attr] - 2:
                    msg = "string '%s' is too long for attribute '%s'" \
                          % (value, attr)
                    raise ValueError, msg
                self.__dict__[attr] = value
            else:
                Task.__setattr__(self, name, value)
                pass
            pass
        return

    pass                                # class AIPSTask


class AIPSMessageLog:

    # Default user number.
    userno = -1

    def __init__(self):
        # Update default user number.
        if self.userno == -1:
            self.userno = AIPS.userno
        return

    def zap(self):
        """Zap message log."""

        proxy = AIPS.disks[1].proxy()
        inst = getattr(proxy, self.__class__.__name__)
        return inst.zap(self.userno)

    pass                                # class AIPSMessageLog


def AIPSList(list):
    """Transform a Python array into an AIPS array.

    Returns a list suitable for using 1-based indices.
    """

    try:
        # Make sure we don't consider strings to be lists.
        if str(list) == list:
            return list
        pass
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
        pass
    
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
        pass
    
    # Apparently LIST isn't a list; simply return it unchanged.
    return list


# Tests.
if __name__ == '__main__':
    import doctest, sys
    results = doctest.testmod(sys.modules[__name__])
    sys.exit(results[0])
