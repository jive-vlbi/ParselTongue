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
    tacop = AIPSTask('tacop')
    tacop.indata = uvdata
    tacop.outdata = uvdata
    tacop.inext = 'CL'
    tacop.invers = 1
    tacop.outvers = 3
    tacop()

    assert([3, 'AIPS CL'] in uvdata.tables)

    uvdata.zap_table('CL', 1)

    assert([3, 'AIPS CL'] in uvdata.tables)
    assert([1, 'AIPS CL'] not in uvdata.tables)

    tacop = AIPSTask('tacop')
    tacop.indata = uvdata
    tacop.outdata = uvdata
    tacop.inext = 'CL'
    tacop.invers = 3
    tacop.outvers = 5
    tacop()

    uvdata2 = WAIPSUVData(uvdata.name, uvdata.klass, uvdata.disk, uvdata.seq)

    assert([5, 'AIPS CL'] in uvdata2.tables)

    uvdata2.zap_table('CL', 0)

    assert([5, 'AIPS CL'] not in uvdata2.tables)
    assert([3, 'AIPS CL'] in uvdata2.tables)
    assert([1, 'AIPS CL'] not in uvdata2.tables)

    count = 0
    for cl in uvdata2.table('CL', 3):
        count += 1
        continue
    assert(count > 0)

finally:
    uvdata.zap()
