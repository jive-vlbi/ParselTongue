import AIPS
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

fitld = AIPSTask('fitld')
fitld.datain = file
fitld.outdata = uvdata
fitld.msgkill = 2
fitld.go()

try:
    uvdata = WizAIPSUVData(name, 'UVDATA', 1, 1, AIPS.userno)
    count = 0
    inttim = 0
    for vis in uvdata[10:20]:
        inttim += vis.inttim
        count += 1
        continue
    assert(count == 10)
    assert(inttim == 40.0)
    count = 0
    inttim = 0
    for vis in uvdata[30000:]:
        assert(vis.time > 0.746901)
        inttim += vis.inttim
        count += 1
        continue
    assert(count == (len(uvdata) - 30000))
    assert(inttim == 24132.0)
    count = 0
    for vis in uvdata[30000:-10]:
        count += 1
        continue
    assert(count == (len(uvdata) - 30010))

finally:
    uvdata.zap()
