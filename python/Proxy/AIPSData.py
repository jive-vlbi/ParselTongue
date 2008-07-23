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

This module provides the bits and pieces to implement AIPSImage and
AIPSUVData objects.

"""

# Bits from Obit.
import Obit, OErr, OSystem
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
        """Checks that this instance of AIPSData refers to a dataset that is
        actually present in the AIPS catalogue."""

        assert(not self.err.isErr)
        cno = Obit.AIPSDirFindCNO(desc['disk'], desc['userno'], desc['name'],
                                  desc['klass'], self.type,  desc['seq'],
                                  self.err.me)
        if cno == -1:
            OErr.PClear(self.err)
            return False
        return True

    def verify(self, desc):
        data = self._init(desc)
        return True                # Return something other than None.

    def header(self, desc):
        """Returns the data header."""
        data = self._init(desc)
        return data.header._generate_dict()

    def _len(self, desc):
        data = self._init(desc)
        return len(data)

    def keywords(self, desc):
        data = self._init(desc)
        return data.keywords._generate_dict()

    def stokes(self, desc):
        data = self._init(desc)
        return data.stokes

    def tables(self, desc):
        data = self._init(desc)
        return data.tables

    def table_highver(self, desc, type):
        """Returns the highest version number of the specified table type."""
        data = self._init(desc)
        return data.table_highver(type)

    def rename(self, desc, name, klass, seq):
        """Renames the data set."""
        data = self._init(desc)
        return data.rename(name, klass, seq)

    def zap(self, desc, force):
        """Removes the data set from the AIPS catalogue."""
        self._init(desc).zap(force)
        return True                # Return something other than None.

    def clrstat(self, desc):
        """Unsets the 'busy' state in the AIPS catalogue. Useful should an
		AIPS task die mid-step."""
        self._init(desc).clrstat()
        return True                # Return something other than None.

    def keywords_table(self, desc, type, version):
        data = self._init(desc)
        table = data.table(type, version)
        try:
            result = table.keywords._generate_dict()
        finally:
            table.close()
            pass
        return result

    def version_table(self, desc, type, version):
        data = self._init(desc)
        table = data.table(type, version)
        try:
            result = table.version
        finally:
            table.close()
            pass
        return result

    def _getitem_table(self, desc, type, version, key):
        data = self._init(desc)
        table = data.table(type, version)
        try:
            result = table[key]._generate_dict()
        finally:
            table.close()
            pass
        return result

    def _len_table(self, desc, type, version):
        data = self._init(desc)
        table = data.table(type, version)
        try:
            result = len(table)
        finally:
            table.close()
            pass
        return result

    def zap_table(self, desc, type, version):
        """Remove the specified version of the indicated table type."""
        data = self._init(desc)
        data.zap_table(type, version)
        return True                # Return something other than None.

    def _getitem_history(self, desc, key):
        data = self._init(desc)
        history = data.history
        try:
            result = history[key]
        finally:
            history.close()
            pass
        return result

    pass                           # class AIPSData


class AIPSImage(AIPSData):
    def __init__(self):
        self.type = 'MA'
        AIPSData.__init__(self)
        return

    def _init(self, desc):
        userno = OSystem.PGetAIPSuser()
        uvdata = WAIPSImage(desc['name'], desc['klass'], desc['disk'],
                            desc['seq'], desc['userno'])
        OSystem.PSetAIPSuser(userno)
        return uvdata

    pass


class AIPSUVData(AIPSData):
    def __init__(self):
        self.type = 'UV'
        AIPSData.__init__(self)
        return

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
        for cno in xrange(1, num_slots):
            entry = AIPSDir.PInfo(disk, userno, cno, self.err)
            if entry:
                dict = {}
                dict['cno'] = cno
                dict['name'] = entry[0:12].strip()
                dict['klass'] = entry[13:19].strip()
                dict['seq'] = int(entry[20:25])
                dict['type'] = entry[26:28]
                dict['date'] = entry[29:40]
                dict['time'] = entry[41:49]
                catalog.append(dict)
                pass
            continue
        OSystem.PSetAIPSuser(_userno)
        return catalog

    pass
