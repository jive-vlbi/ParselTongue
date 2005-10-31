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
fitld.infile = file
fitld.outdata = uvdata
fitld.msgkill = 2
fitld.go()

try:
    uvdata = WizAIPSUVData(name, 'UVDATA', 1, 1, AIPS.userno)
    count = 0
    weight = 0
    for vis in uvdata:
        weight += vis.weight
        count += 1
        continue
    assert(len(uvdata) == count)
    print 'Visibilities:', count
    print 'Total weight:', weight

finally:
    uvdata.zap()
