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
        """Check whether the date set exists.
        
        Return True if the data set exists, False otherwise."""

        try:
            self._init(desc)
        except:
            return False
        return True

    def verify(self, desc):
        """Verify whether this date set can be accesed."""

        self._init(desc)
        return True                # Return something other than None.

    def header(self, desc):
        data = self._init(desc)
        return data.Desc.Dict

    def tables(self, desc):
        data = self._init(desc)
        return TableList.PGetList(data.TableList, self.err)

    def table_highver(self, desc, type):
        data = self._init(desc)
        return TableList.PGetHigh(data.TableList, type)

    def zap(self, desc):
        data = self._init(desc)
        data.Zap(self.err)
        return True                # Return something other than None.

    def header_table(self, desc, type, version):
        data = self._init(desc)
        table = data.NewTable(1, type, version, self.err)
        if OErr.PIsErr(self.err):
            OErr.printErrMsg(self.err, "AIPSData.header_table")
        return table.Desc.Dict

    def getrow_table(self, desc, type, version, rowno):
        data = self._init(desc)
        table = data.NewTable(1, type, version, self.err)
        if OErr.PIsErr(self.err):
            OErr.printErrMsg(self.err, "AIPSData.getrow_table")
        return table.ReadRow(rowno, self.err)

    def zap_table(self, desc, type, version):
        data = self._init(desc)
        data.ZapTable(type, version, self.err)
        if OErr.PIsErr(self.err):
            OErr.printErrMsg(self.err, "AIPSData.zap_table")
        data.UpdateTables(self.err)
        return True                # Return something other than None.


class AIPSImage(AIPSData):
    def _init(self, desc):
        userno = OSystem.PGetAIPSuser()
        OSystem.PSetAIPSuser(desc['userno'])
        image = Image.newPAImage(desc['name'], desc['name'], desc['klass'],
                                 desc['disk'], desc['seq'], True, self.err)
        OSystem.PSetAIPSuser(userno)
        if OErr.PIsErr(self.err):
            OErr.printErrMsg(self.err, "AIPSImage._init")
        return image


class AIPSUVData(AIPSData):
    def _init(self, desc):
        userno = OSystem.PGetAIPSuser()
        OSystem.PSetAIPSuser(desc['userno'])
        uvdata = UV.newPAUV(desc['name'], desc['name'], desc['klass'],
                            desc['disk'], desc['seq'], True, self.err)
        OSystem.PSetAIPSuser(userno)
        if OErr.PIsErr(self.err):
            OErr.printErrMsg(self.err, "AIPSUVData._init")
        return uvdata
