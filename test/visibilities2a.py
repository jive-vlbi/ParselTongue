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
fitld.douvcomp = 0
fitld.msgkill = 2
fitld.go()

uvdata = WizAIPSUVData(name, 'UVDATA', 1, 1, AIPS.userno)
for vis in uvdata:
    vis.visibility[0][0][0][2] = 1.234
    vis.update()
    continue
