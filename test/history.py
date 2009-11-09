from AIPS import AIPS
from AIPSTask import AIPSTask
from AIPSData import AIPSUVData
from Wizardry.AIPSData import AIPSUVData as WizAIPSUVData

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
    count = 0
    for record in uvdata.history:
        print record
        if record[0:5] == 'FITLD':
            count += 1
            pass
        continue
    assert(count > 5)

    uvdata = WizAIPSUVData(uvdata)
    history = uvdata.history
    history.append('Something new!')
    history.close()

    uvdata = AIPSUVData(uvdata)
    seen = 0
    for record in uvdata.history:
        print record
        if record[0:5] == 'Somet':
            seen = 1
            pass
        continue
    assert(seen)

finally:
    uvdata.zap()
