from AIPS import AIPS
from AIPSTask import AIPSTask
from AIPSData import AIPSUVData

AIPS.userno = 1999

name = 'UVCON'
uvdata = AIPSUVData(name, 'UVDATA', 1, 1)
if uvdata.exists():
    uvdata.zap()
    pass

assert(not uvdata.exists())

uvcon = AIPSTask('uvcon', version='31DEC06')
uvcon.outdata = uvdata
uvcon.infile = 'VLBA1.UVCON'
uvcon.smodel = [None, 1.0, 0.0, 0.0, 0]
uvcon.aparm = [None, 1.4, 0, 30, -12, 12, 0, 120, 1, 1]
uvcon.bparm = [None, -1, 0, 0, 0, 0]
uvcon()

print uvdata.tables

uvdata.zap()
