"""

This module provides the AIPSImage and AIPSUVData classes.  These
classes implement most of the data oriented verb-like functionality
from classic AIPS.

"""

# Global AIPS defaults.
from AIPS import AIPS

# This code is way to clever.  Instead of implementing each and every
# function call provided by a proxy, class _Method implements a
# callable object that invokes a named method of a proxy, passing a
# description of the AIPS data it should operate on as the first
# argument.  To make matters worse, the same implementation is used
# for class AIPSImage and class AIPSData and dispatching is done based
# on the name of the class.  This way adding a function to the proxy
# automatically makes it callable as a method of both AIPSImage and
# AIPSUVData.

class _AIPSDataMethod:

    """This class implements dispatching function calls to a proxy."""

    def __init__(self, inst, name):
        self.inst = inst
        self.name = name

    def __call__(self, *args):
        inst = getattr(self.inst.proxy, self.inst.__class__.__name__)
        func = getattr(inst, self.name)
        return func(self.inst.desc, *args)


class _AIPSDataDesc:

    """This class implements the description of AIPS data that is used
       when dispatching function calls to a proxy."""

    def __init__(self, name, klass, disk, seq):
        self.userno = AIPS.userno
        self.name = name
        self.klass = klass
        self.disk = disk
        self.seq = seq

    # Provide a dictionary-like interface to deal with the
    # idiosyncrasies of XML-RPC.
    def __getitem__(self, key):
        return self.__dict__[key]


class _AIPSData:

    """This class describes generic AIPS data."""

    def __init__(self, name, klass, disk, seq):
        self.desc = _AIPSDataDesc(name, klass, AIPS.disks[disk].disk, seq)
        self.proxy = AIPS.disks[disk].proxy()
        self.disk = disk

    def __getattr__(self, name):
        if name in self.desc.__dict__:
            return self.desc.__dict__[name]
        return _AIPSDataMethod(self, name)

    def table(self, type, version):
        return _AIPSTable(self, type, version)


class AIPSImage(_AIPSData):

    """This class describes an AIPS image."""
    pass


class AIPSUVData(_AIPSData):

    """This class describes an AIPS UV data set."""
    pass


class _AIPSTableMethod(_AIPSDataMethod):

    """ This class implements dispatching table oriented function
    calls to a proxy."""

    def __init__(self, inst, name):
        _AIPSDataMethod.__init__(self, inst, name)

    def __call__(self, *args):
        inst = getattr(self.inst.data.proxy, self.inst.data.__class__.__name__)
        func = getattr(inst, self.name + '_table')
        return func(self.inst.data.desc,
                    self.inst.name, self.inst.version, *args)


class _AIPSTable:

    """This class describes a generic AIPS extension table."""

    def __init__(self, data, name, version):
        self.data = data
        self.name = name
        self.version = version

    def __getattr__(self, name):
        return _AIPSTableMethod(self, name)
