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

This module provides the AIPSImage and AIPSUVData classes.  These
classes implement most of the data oriented verb-like functionality
from classic AIPS.

Images can be manipulated by creating instances of the AIPSImage class:

>> image = AIPSImage('NONAME', 'IMAGE', 1, 1)

For UV data, the AIPSUVData class should be used:

>>> uvdata = AIPSUVData('NONAME', 'UVDATA', 1, 1)

Checking whether the image or UV data actually exists is easy:

>>> image.exists()
False
>>> uvdata.exists()
False

"""

# Global AIPS defaults.
from AIPS import AIPS

# Generic Python stuff.
import sys

# This code is way to clever.  Instead of implementing each and every
# function call provided by a proxy, class _Method implements a
# callable object that invokes a named method of a proxy, passing a
# description of the AIPS data it should operate on as the first
# argument.  To make matters worse, the same implementation is used
# for class AIPSImage and class AIPSData and dispatching is done based
# on the name of the class.  This way adding a function to the proxy
# automatically makes it callable as a method of both AIPSImage and
# AIPSUVData.

def _whoami():
    """Return the name of the function that called us."""
    return sys._getframe(1).f_code.co_name


class _AIPSDataMethod:

    """This class implements dispatching function calls to a proxy."""

    def __init__(self, inst, name):
        self.inst = inst
        self.name = name

    def __call__(self, *args):
        func = self.inst._method(self.name)
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
        return

    name = property(lambda self: self.desc.name,
                    doc='Name of this data set.')
    klass = property(lambda self: self.desc.klass,
                     doc='Class of this data set.')
    disk = property(lambda self: self.desc.disk,
                    doc='Disk where this data set is stored.')
    seq = property(lambda self: self.desc.seq,
                   doc='Sequence number of this data set.')
    userno = property(lambda self: self.desc.userno,
                      doc='User number used to access this data set.')

    def __repr__(self):
        repr = "%s('%s', '%s', %d, %d)" % \
               (self.__class__.__name__,
                self.name, self.klass, self.disk, self.seq)
        return repr

    def __str__(self):
        return self.__repr__()

    def __getattr__(self, name):
        if name in self.desc.__dict__:
            return self.desc.__dict__[name]
        return _AIPSDataMethod(self, name)

    def table(self, type, version):
        return _AIPSTable(self, type, version)

    def _method(self, name):
        return getattr(getattr(self.proxy, self.__class__.__name__), name)

    def exists(self):
        """Check whether this image or data set exists.

        Returns True if the image or data set exists, False otherwise."""
        return self._method(_whoami())(self.desc)

    def verify(self):
        """Verify whether this image or data set can be accessed."""
        return self._method(_whoami())(self.desc)

    def header(self):
        """Get the header for this image or data set.

        Returns the header as a dictionary."""
        return self._method(_whoami())(self.desc)

    def tables(self):
        """Get the list of extension tables."""
        return self._method(_whoami())(self.desc)

    def table_highver(self, type):
        """Get the highest version of an extension table.

        Returns the highest available version number of the extension
        table TYPE."""
        return self._method(_whoami())(self.desc, type)

    def zap(self):
        """Destroy this image or data set."""
        return self._method(_whoami())(self.desc)

    def header_table(self, type, version):
        """Get the header of an extension table.

        Returns the header of version VERSION of the extension table
        TYPE."""
        return self._method(_whoami())(self.desc, type, version)

    def getrow_table(self, type, version, rowno):
        """Get a row from an extension table.

        Returns row ROWNO from version VERSION of extension table TYPE
        as a dictionary."""
        return self._method(_whoami())(self.desc, type, version, rowno)

    def zap_table(self, type, version):
        """Destroy an extension table.

        Deletes version VERSION of the extension table TYPE.  If
        VERSION is 0, delete the highest version of table TYPE.  If
        VERSION is -1, delete all versions of table TYPE."""
        return self._method(_whoami())(self.desc, type, version)


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
        func = self.inst.data._method(self.name + '_table')
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


class AIPSCat:
    def __init__(self, disk):
        proxy = AIPS.disks[disk].proxy()
        self.catalog = proxy.AIPSCat.cat(disk, AIPS.userno)
        return

    def __repr__(self):
        # Print something useful if the catalof is empty.
        if len(self.catalog) == 0:
            return 'Empty'

        return ''.join (['%s\n' % entry for entry in self.catalog]).strip()
