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

>>> imean.blc[0:2] = [128, 128]
>>> print imean.blc
[128.0, 128.0, 0.0, 0.0, 0.0, 0.0, 0.0]

"""

# Global AIPS defaults.
from AIPS import AIPS

# Generic Task implementation.
from Task import Task, Range, List

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
        self._adverb_dict = {}
        self._input_list = []
        self._output_list = []

        # Optional arguments.
        if 'version' in kwds:
            self.version = kwds['version']
        if 'userno' in kwds:
            self.userno = kwds['userno']

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
        self._adverb_dict = params['adverb_dict']
        self._input_list = params['input_list']
        self._output_list = params['output_list']
        self._range_dict = params['range_dict']
        self._strlen_dict = params['strlen_dict']
        for adverb in self._range_dict:
            range = self._range_dict[adverb]
            range = Range(range['min'], range['max'])
            self._range_dict[adverb] = range
        for adverb in self._adverb_dict:
            if type(self._adverb_dict[adverb]) == list:
                value = self._adverb_dict[adverb]
                self._adverb_dict[adverb] = List(self, adverb, value)

        # Initialize all adverbs to their default values.
        self.__dict__.update(self._adverb_dict)

    def defaults(self):
        """Set adverbs to their defaults."""
        self.__dict__.update(self._adverb_dict)

    def __display_adverbs(self, adverbs):
        """Display ADVERBS."""

        for adverb in adverbs:
            if self.__dict__[adverb] == '':
                print "'%s': ''" % adverb
            else:
                print "'%s': %s" % (adverb, self.__dict__[adverb])

    def inputs(self):
        """Display all inputs for this task."""
        self.__display_adverbs(self._input_list)

    def outputs(self):
        """Display all outputs for this task."""
        self.__display_adverbs(self._output_list)

    def spawn(self):
        """Spawn the task."""

        if self.userno == 0:
            raise RuntimeError, "AIPS user number is not set"

        input_dict = {}
        for adverb in self._input_list:
            if type(self.__dict__[adverb]) == List:
                input_dict[adverb] = list(self.__dict__[adverb])
            else:
                input_dict[adverb] = self.__dict__[adverb]

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

        inst = getattr(proxy, self.__class__.__name__)
        tid = inst.spawn(self._name, self.version, self.userno,
                         self.msgkill, self.isbatch, input_dict)
        return (proxy, tid)

    def finished(self, proxy, tid):
        inst = getattr(proxy, self.__class__.__name__)
        return inst.finished(tid)

    def messages(self, proxy, tid):
        inst = getattr(proxy, self.__class__.__name__)
        return inst.messages(tid)

    def wait(self, proxy, tid):
        while not self.finished(proxy, tid):
            self.messages(proxy, tid)
        inst = getattr(proxy, self.__class__.__name__)
        output_dict = inst.wait(tid)
        for adverb in self._output_list:
            self.__dict__[adverb] = output_dict[adverb]

    def go(self):
        """Run the task."""

        (proxy, tid) = self.spawn()
        count = 0
        rotator = ['|\b', '/\b', '-\b', '\\\b']
        while not self.finished(proxy, tid):
            msg = self.messages(proxy, tid)
            if msg:
                sys.stdout.write(msg)
            else:
                sys.stdout.write(rotator[count % 4])
                sys.stdout.flush()
            count += 1
        return self.wait(proxy, tid)

    def __call__(self):
        self.go()

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
            # We treat 'infile' and 'outfile' special.  Instead of
            # checking the length of the complete string, we only
            # check the length of the final component of the pathname.
            # The backend will split of the direcrory component and
            # use that as an "area".
            (attr, dict) = self._findattr(name)
            file_adverbs = ['infile', 'outfile']
            if attr in file_adverbs and type(value) == str and \
                   os.path.dirname(value):
                if len(os.path.basename(value)) > self._strlen_dict[attr] - 2:
                    msg = "string '%s' is too long for attribute '%s'" \
                          % (value, attr)
                    raise ValueError, msg
                self.__dict__[attr] = value
            else:
                Task.__setattr__(self, name, value)


# Tests.
if __name__ == '__main__':
    import doctest, sys
    doctest.testmod(sys.modules[__name__])
