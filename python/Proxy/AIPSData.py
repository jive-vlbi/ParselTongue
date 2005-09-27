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

This module provides the bits and pieces to implement AIPSImage and
AIPSUVData objects.

"""

# Bits from Obit.
import OErr, OSystem
import AIPSDir
import Image, UV
import TableList

# Wizardry bits.
from Wizardry.AIPSData import AIPSUVData as WAIPSUVData
from Wizardry.AIPSData import AIPSImage as WAIPSImage

class AIPSData:
    def __init__(self):
        self.err = OErr.OErr()
        return

    def exists(self, desc):
        try:
            self._init(desc)
        except OErr.OErr, err:
            OErr.PClear(err)
            return False
        return True

    def verify(self, desc):
        data = self._init(desc)
        return True                # Return something other than None.

    def header(self, desc):
        data = self._init(desc)
        return data.header

    def tables(self, desc):
        data = self._init(desc)
        return TableList.PGetList(data._data.TableList, self.err)

    def table_highver(self, desc, type):
        data = self._init(desc)
        return TableList.PGetHigh(data._data.TableList, type)

    def zap(self, desc):
        self._init(desc).zap()
        return True                # Return something other than None.

    def header_table(self, desc, type, version):
        data = self._init(desc)
        table = data.table(type, version)
        return table._table.Desc.Dict

    def keywords_table(self, desc, type, version):
        data = self._init(desc)
        table = data.table(type, version)
        return table.keywords

    # XXX Deprecated.
    def getrow_table(self, desc, type, version, rowno):
        data = self._init(desc)
        table = data.table(type, version)
        return table[rowno - 1]._row

    def _getitem_table(self, desc, type, version, key):
        data = self._init(desc)
        table = data.table(type, version)
        return table[key]._dict()

    def _len_table(self, desc, type, version): 
        data = self._init(desc)
        table = data.table(type, version)
        return len(table)

    def zap_table(self, desc, type, version):
        data = self._init(desc)
        data.zap_table(type, version)
        return True                # Return something other than None.

    pass


class AIPSImage(AIPSData):
    def _init(self, desc):
        userno = OSystem.PGetAIPSuser()
        uvdata = WAIPSImage(desc['name'], desc['klass'], desc['disk'],
                            desc['seq'], desc['userno'])
        OSystem.PSetAIPSuser(userno)
        return uvdata

    pass


class AIPSUVData(AIPSData):
    def _init(self, desc):
        userno = OSystem.PGetAIPSuser()
        uvdata = WAIPSUVData(desc['name'], desc['klass'], desc['disk'],
                             desc['seq'], desc['userno'])
        OSystem.PSetAIPSuser(userno)
        return uvdata

    def antennas(self, desc):
        uvdata = self._init(desc)
        return uvdata.antennas

    def polarizations(self, desc):
        uvdata = self._init(desc)
        return uvdata.polarizations

    def sources(self, desc):
        uvdata = self._init(desc)
        return uvdata.sources

    def stokes(self, desc):
        uvdata = self._init(desc)
        return uvdata.stokes

    pass


class AIPSCat:
    def __init__(self):
        self.err = OErr.OErr()
        return

    def cat(self, disk, userno):
        _userno = OSystem.PGetAIPSuser()
        OSystem.PSetAIPSuser(userno)

        try:
            num_slots = AIPSDir.PNumber(disk, userno, self.err)
        except OErr.OErr, err:
            OErr.PClear(err)
            return []

        catalog = []
        for slot in xrange(1, num_slots):
            entry = AIPSDir.PInfo(disk, userno, slot, self.err)
            if entry:
                catalog.append('%d %s' % (slot, entry))
                pass
            continue
        OSystem.PSetAIPSuser(_userno)
        return catalog

    pass
