from AIPS import AIPS
from AIPSTask import AIPSTask
from AIPSData import AIPSUVData

import os

AIPS.userno = 1999

name = 'UVCON'
uvdata = AIPSUVData(name, 'UVDATA', 1, 1)
if uvdata.exists():
    uvdata.zap()
    pass

os.system('cp VLBA1.UVCON /tmp')

assert(not uvdata.exists())

uvcon = AIPSTask('uvcon')
uvcon.outdata = uvdata
uvcon.infile = '/tmp/VLBA1.UVCON'
uvcon.smodel = [None, 1.0, 0.0, 0.0, 0]
uvcon.aparm = [None, 1.4, 0, 30, -12, 12, 0, 120, 1, 1]
uvcon.bparm = [None, -1, 0, 0, 0, 0]
uvcon()

print uvdata.tables

uvdata.zap()
