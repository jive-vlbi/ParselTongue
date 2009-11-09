from AIPS import AIPS
from AIPSTask import AIPSTask
from AIPSData import AIPSUVData
from Wizardry.AIPSData import AIPSUVData as WAIPSUVData

import os
import urllib

AIPS.userno = 1999

# Download a smallish FITS file from the EVN archive.
url = 'http://archive.jive.nl/exp/N03L1_030225/fits/n03l1_1_1.IDI1'
file = '/tmp/' + os.path.basename(url)
if not os.path.isfile(file):
    urllib.urlretrieve(url, file)
assert(os.path.isfile(file))

name = os.path.basename(url).split('_')[0].upper()
uvdata = AIPSUVData(name, 'UVDATA', 1, 1)
if uvdata.exists():
    uvdata.zap()
    pass

assert(not uvdata.exists())

fitld = AIPSTask('fitld')
fitld.datain = file
fitld.outdata = uvdata
fitld.msgkill = 2
fitld.go()

assert(uvdata.exists())

try:
    uvflg = AIPSTask('uvflg')
    uvflg.indata = uvdata
    uvflg.bchan = 1
    uvflg.echan = 1
    uvflg.antennas[1] = 1
    uvflg.stokes = 'CROS'
    uvflg.reason = 'TEST'
    uvflg()

    uvflg.stokes = 'RL'
    uvflg()
    
    print uvdata.tables
    fqtable = uvdata.table('FQ', 0)
    print fqtable[0]
    fgtable = uvdata.table('FG', 0)
    for row in fgtable:
        print row
        continue
    assert (fgtable[0].pflags == [0, 0, 1, 1])
    assert (fgtable[1]['pflags'] == [0, 0, 1, 0])

    uvdata2 = WAIPSUVData(uvdata.name, uvdata.klass, uvdata.disk, uvdata.seq)
    fgtable = uvdata2.table('FG', 0)
    row = fgtable[1]
    row.ants = [2, 0]
    fgtable.append(row)
    fgtable.close()
    
    fgtable = uvdata.table('FG', 0)
    for row in fgtable:
        print row
        continue
    
    assert (fgtable[2].ants == [2, 0])

finally:
    uvdata.zap()
