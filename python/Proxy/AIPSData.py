"""

This module provides the bits and pieces to implement AIPSImage and
AIPSUVData objects.

"""

# Bits from Obit.
import OErr, OSystem
import Image, UV
import TableList

class AIPSData:
    def __init__(self):
        self.err = OErr.OErr()
        self.sys = OSystem.OSystem("ParselTongue", 1, 1, -1, [], -1, [],
                                   True, False, self.err)

    def exists(self, desc):
        self._init(desc)
        if OErr.PIsErr(self.err):
            OErr.PClear(self.err)
            return False
        return True

    def _verify(self, desc):
        data = self._init(desc)
        if OErr.PIsErr(self.err):
            OErr.printErrMsg(self.err, "AIPSData._verify")
            raise RuntimeError, "Cannot open data set %s" % desc['name']
        return data

    def verify(self, desc):
        data = self._verify(desc)
        return True                # Return something other than None.

    def header(self, desc):
        data = self._verify(desc)
        return data.Desc.Dict

    def tables(self, desc):
        data = self._verify(desc)
        return TableList.PGetList(data.TableList, self.err)

    def table_highver(self, desc, type):
        data = self._verify(desc)
        return TableList.PGetHigh(data.TableList, type)

    def zap(self, desc):
        data = self._verify(desc)
        data.Zap(self.err)
        return True                # Return something other than None.

    def header_table(self, desc, type, version):
        data = self._verify(desc)
        table = data.NewTable(1, type, version, self.err)
        if OErr.PIsErr(self.err):
            OErr.printErrMsg(self.err, "AIPSData.header_table")
            msg = "Cannot open %s table version %d", (type, version)
            raise RuntimeError, msg
        return table.Desc.Dict

    def getrow_table(self, desc, type, version, rowno):
        data = self._verify(desc)
        table = data.NewTable(1, type, version, self.err)
        if OErr.PIsErr(self.err):
            OErr.printErrMsg(self.err, "AIPSData.getrow_table")
            msg = "Cannot open %s table version %d", (type, version)
            raise RuntimeError, msg
        return table.ReadRow(rowno, self.err)

    def zap_table(self, desc, type, version):
        data = self._verify(desc)
        data.ZapTable(type, version, self.err)
        if OErr.PIsErr(self.err):
            OErr.printErrMsg(self.err, "AIPSData.zap_table")
            msg = "Cannot open %s table version %d", (type, version)
            raise RuntimeError, msg
        data.UpdateTables(self.err)
        return True                # Return something other than None.


class AIPSImage(AIPSData):
    def _init(self, desc):
        userno = OSystem.PGetAIPSuser()
        OSystem.PSetAIPSuser(desc['userno'])
        image = Image.newPAImage(desc['name'], desc['name'], desc['klass'],
                                 desc['disk'], desc['seq'], True, self.err)
        OSystem.PSetAIPSuser(userno)
        return image


class AIPSUVData(AIPSData):
    def _init(self, desc):
        userno = OSystem.PGetAIPSuser()
        OSystem.PSetAIPSuser(desc['userno'])
        uvdata = UV.newPAUV(desc['name'], desc['name'], desc['klass'],
                            desc['disk'], desc['seq'], True, self.err)
        OSystem.PSetAIPSuser(userno)
        return uvdata
