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

"""

This module provides the AIPSImage and AIPSUVData classes.  These
classes implement most of the data oriented verb-like functionality
from classic AIPS.

Images can be manipulated by creating instances of the AIPSImage class:

>>> image = AIPSImage('NONAME', 'IMAGE', 1, 1)

For UV data, the AIPSUVData class should be used:

>>> uvdata = AIPSUVData('NONAME', 'UVDATA', 1, 1)

Checking whether the image or UV data actually exists is easy:

>>> image.exists()
False
>>> uvdata.exists()
False

>>> print uvdata
AIPSUVData('NONAME', 'UVDATA', 1, 1)

Checking whether two instance refer to the same data is fairly simple:

>>> image == uvdata
False

>>> image == AIPSImage('NONAME', 'IMAGE', 1, 1)
True

Both classes implement the copy method:

>>> uvjunk = uvdata.copy()
>>> uvjunk == uvdata
True
>>> uvjunk.name = 'GARBAGE'
>>> uvjunk != uvdata
True

"""

# Global AIPS defaults.
import AIPS

# Generic Python stuff.
import sys

# This code is way too clever.  Instead of implementing each and every
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

    def __init__(self, name, klass, disk, seq, userno):
        self.name = name
        self.klass = klass
        self.disk = disk
        self.seq = seq
        self.userno = userno
        return

    # Provide a dictionary-like interface to deal with the
    # idiosyncrasies of XML-RPC.
    def __getitem__(self, key):
        return self.__dict__[key]

    pass                                # class _AIPSDataDesc


class _dictify(dict):

    def __getattr__(self, item):
        return self[item]

    pass                                # class _dictify


class _AIPSDataHeader(_dictify):

    """This class describes the header of an AIPS image or UV data set."""

    pass                                # class _AIPSDataHeader


class _AIPSData(object):

    """This class describes generic AIPS data."""

    def __init__(self, *args):
        # Instances can be created by specifying name, class, disk,
        # sequence number and (optionally) user number explicitly, or
        # by passing an object that has the appropriate attributes.
        # This allows the creation of a non-Wizardry object from its
        # Wizardry counterpart.

        if len(args) not in [1, 4, 5]:
            msg = "__init__() takes 2, 5 or 6 arguments (%d given)" \
                  % (len(args) + 1)
            raise TypeError, msg

        if len(args) == 1:
            name = args[0].name
            klass = args[0].klass
            disk = args[0].disk
            seq = args[0].seq
            userno = args[0].userno
        else:
            name = args[0]
            klass = args[1]
            disk = args[2]
            seq = args[3]
            userno = -1
            if len(args) == 5:
                userno = args[4]
                pass
            pass

        if userno == -1:
            userno = AIPS.userno
        self._disk = disk
        disk = AIPS.disks[disk]
        self.desc = _AIPSDataDesc(name, klass, disk.disk, seq, userno)
        self.proxy = disk.proxy()
        return

    def _set_name(self, name): self.desc.name = name; pass
    name = property(lambda self: self.desc.name, _set_name,
                    doc='Name of this data set.')
    def _set_klass(self, klass): self.desc.klass = klass; pass
    klass = property(lambda self: self.desc.klass, _set_klass,
                     doc='Class of this data set.')
    def _set_disk(self, disk):
        self._disk = disk
        disk = AIPS.disks[disk]
        self.desc.disk = disk.disk
        self.proxy = disk.proxy()
        pass
    disk = property(lambda self: self._disk, _set_disk,
                    doc='Disk where this data set is stored.')
    def _set_seq(self, seq): self.desc.seq = seq; pass
    seq = property(lambda self: self.desc.seq, _set_seq,
                   doc='Sequence number of this data set.')
    def _set_userno(self, userno): self.desc.userno = userno; pass
    userno = property(lambda self: self.desc.userno, _set_userno,
                      doc='User number used to access this data set.')

    def __repr__(self):
        repr = "%s('%s', '%s', %d, %d)" % \
               (self.__class__.__name__,
                self.name, self.klass, self.disk, self.seq)
        return repr

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        if self.desc.name != other.desc.name:
            return False
        if self.desc.klass != other.desc.klass:
            return False
        if self.desc.disk != other.desc.disk:
            return False
        if self.desc.seq != other.desc.seq:
            return False
        if self.desc.userno != other.desc.userno:
            return False
        return True

    def __str__(self):
        return self.__repr__()

    def __getattr__(self, name):
        if name in self.desc.__dict__:
            return self.desc.__dict__[name]
        return _AIPSDataMethod(self, name)

    def __len__(self):
        return _AIPSDataMethod(self, '_len')()

    def copy(self):
        return self.__class__(self.name, self.klass, self.disk, self.seq,
                              self.userno)

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

    def _generate_header(self):
        dict = self._method('header')(self.desc)
        return _AIPSDataHeader(dict)
    header = property(_generate_header,
                      doc='Header for this data set.')

    def _generate_keywords(self):
        return _AIPSDataMethod(self, 'keywords')()
    keywords = property(_generate_keywords,
                        doc='Keywords for this data set.')

    def _generate_tables(self):
        dict = self._method('tables')(self.desc)
        return dict
    tables = property(_generate_tables,
                      doc='Extension tables for this data set.')

    history = property(lambda self: _AIPSHistory(self),
                       doc='History table for this data set.')

    def table_highver(self, type):
        """Get the highest version of an extension table.

        Returns the highest available version number of the extension
        table TYPE."""
        return self._method(_whoami())(self.desc, type)

    def rename(self, name=None, klass=None, seq=None, **kwds):
        """Rename this image or data set.

        NAME is the new name, KLASS is the new class and SEQ is the
        new sequence number for the data set.  Note that you can't
        change the disk number, since that would require copying the
        data."""
        if name == None: name = self.name
        if klass == None: klass = self.klass
        if seq == None: seq = self.seq
        if 'name' in kwds: name = kwds['name']
        if 'klass' in kwds: klass = kwds['name']
        if 'seq' in kwds: seq = kwds['seq']
        result = self._method(_whoami())(self.desc, name, klass, seq)
        self.name = result[0]
        self.klass = result[1]
        self.seq = result[2]
        return result

    def zap(self, force=False):
        """Destroy this image or data set."""
        return self._method(_whoami())(self.desc, force)

    def clrstat(self):
        """Clear all read and write status flags."""
        return self._method(_whoami())(self.desc)

    def header_table(self, type, version):
        """Get the header of an extension table.

        Returns the header of version VERSION of the extension table
        TYPE."""
        return self._method(_whoami())(self.desc, type, version)

    # XXX Deprecated.
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

    def _generate_antennas(self):
        return self._method('antennas')(self.desc)
    antennas = property(_generate_antennas,
                        doc = 'Antennas in this data set.')

    def _generate_polarizations(self):
        return self._method('polarizations')(self.desc)
    polarizations = property(_generate_polarizations,
                             doc='Polarizations in this data set.')

    def _generate_sources(self):
        return self._method('sources')(self.desc)
    sources = property(_generate_sources,
                       doc='Sources in this data set.')

    def _generate_stokes(self):
        return self._method('stokes')(self.desc)
    stokes = property(_generate_stokes,
                      doc='Stokes parameters for this data set.')

    pass                                # class AIPSData


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
        func = self.inst._data._method(self.name + '_table')
        return func(self.inst._data.desc,
                    self.inst._name, self.inst._version, *args)

    pass                                # class _AIPSTableMethod


class _AIPSTableRow(_dictify):

    """This class describes a row of an AIPS extenstion table."""

    pass                                # class _AIPSTableRow


class _AIPSTableIter:

    """This class provides an iterator for AIPS extension tables."""

    def __init__(self, table):
        self._table = table
        self._len = len(self._table)
        self._index = 0
        return

    def next(self):
        if self._index >= self._len:
            raise StopIteration
        result = self._table[self._index]
        self._index += 1
        return result

    pass                                # class _AIPSTableIter
    

class _AIPSTable(object):

    """This class describes a generic AIPS extension table."""

    def __init__(self, data, name, version):
        self._data = data
        self._name = name
        self._version = version
        return

    def __getattr__(self, name):
        return _AIPSTableMethod(self, name)

    def __getitem__(self, key):
        dict = _AIPSTableMethod(self, '_getitem')(key)
        return _AIPSTableRow(dict)

    def __iter__(self):
        return _AIPSTableIter(self)

    def __len__(self):
        return _AIPSTableMethod(self, '_len')()

    def _generate_keywords(self):
        return _AIPSTableMethod(self, 'keywords')()
    keywords = property(_generate_keywords,
                        doc='Keywords for this table.')

    def _generate_name(self):
        return self._name
    name = property(_generate_name, doc='Table extension name.')

    def _generate_version(self):
        return _AIPSTableMethod(self, 'version')()
    version = property(_generate_version, doc='Table version.')

    pass                                # class _AIPSTable


class _AIPSHistoryMethod(_AIPSDataMethod):

    """ This class implements dispatching history oriented function
    calls to a proxy."""

    def __init__(self, inst, name):
        _AIPSDataMethod.__init__(self, inst, name)

    def __call__(self, *args):
        func = self.inst._data._method(self.name + '_history')
        return func(self.inst._data.desc, *args)

    pass                                # class _AIPSHistoryMethod


class _AIPSHistory(object):

    """This class describes an AIPS hostory table."""

    def __init__(self, data):
        self._data = data
        return

    def __getitem__(self, key):
        return _AIPSHistoryMethod(self, '_getitem')(key)

    pass                                # class _AIPSHistory


class _AIPSCatEntry(_dictify):

    """This class describes an AIPS catalog entry."""

    pass                                # class _AIPSCatEntry


class AIPSCat(object):

    """This class describes an entire AIPS catalogue."""

    def __init__(self, disk=0):
        disks = [disk]
        if disk == 0:
            disks = range(1, len(AIPS.disks))
            pass
            
        self._cat = {}
        for disk in disks:
            proxy = AIPS.disks[disk].proxy()
            catalog = proxy.AIPSCat.cat(AIPS.disks[disk].disk, AIPS.userno)
            self._cat[disk] = [_AIPSCatEntry(entry) for entry in catalog]
            continue
        return

    def __getitem__(self, key):
        return self._cat[key]

    def __repr__(self):
        return repr(self._cat)

    def __iter__(self):
        return self._cat.iterkeys()

    def __str__(self):
        s = ''
        for disk in self._cat:
            s += 'Catalog on disk %2d\n' % disk
            s += ' Cat Mapname      Class   Seq  Pt     Last access\n'
            if len(self._cat[disk]) > 0:
                s += ''.join([' %3d %-12.12s.%-6.6s. %4d %-2.2s %s %s\n' \
                              % (entry.cno, entry.name, entry.klass,
                                 entry.seq, entry.type, entry.date,
                                 entry.time) for entry in self._cat[disk]])
                pass
            continue
        return s.strip()

    def zap(self, force=False, **kwds):

        """Removes a catalogue entry."""

        name = None
        if 'name' in kwds: name = kwds['name']; del kwds['name']
        klass = None
        if 'klass' in kwds: klass = kwds['klass']; del kwds['klass']
        seq = None
        if 'seq' in kwds: seq = kwds['seq']; del kwds['seq']

        # Make sure we don't zap if the user made a typo.
        if len(kwds) > 0:
            keys = ["'%s'" % key for key in kwds.keys()]
            msg = "zap() got an unexpected keyword argument %s" % keys[0]
            raise TypeError, msg

        for disk in self._cat:
            for entry in self._cat[disk]:
                if name and not entry['name'] == name:
                    continue
                if klass and not entry['klass'] == klass:
                    continue
                if seq and not entry['seq'] == seq:
                    continue
                if entry['type'] == 'MA':
                    AIPSImage(entry['name'], entry['klass'],
                              disk, entry['seq']).zap(force)
                elif entry['type'] == 'UV':
                    AIPSUVData(entry['name'], entry['klass'],
                               disk, entry['seq']).zap(force)
                    pass
                continue
            continue
        return

    pass                                # class AIPSCat


# Tests.
if __name__ == '__main__':
    import doctest, sys
    results = doctest.testmod(sys.modules[__name__])
    sys.exit(results[0])
